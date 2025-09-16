import logging
import os

from celery import shared_task
from celery.signals import worker_ready
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.db import transaction, DatabaseError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from satagro.helpers import api_request, parse_safe_datetime, warning_has_changed
from satagro.models import MeteoWarning, District, MeteoWarningArchive

logger = logging.getLogger(__name__)

@shared_task
def generate_districts():
    """Function to generate districts from a Geoportal districts file (pgr.gml)"""
    logger.info("generating districts")
    file_path = "./pgr.gml"

    if not os.path.exists(file_path):
        logger.error("File pgr.gml does not exist")
        return False

    try:
        ds = DataSource(file_path)
        layer = ds[0]

        existing_codes = set(District.objects.values_list('district_code', flat=True))
        districts_to_create = []

        for feature in layer:
            try:
                if feature["JPT_KOD_JE"].value not in existing_codes:
                    polygon = GEOSGeometry(feature.geom.wkt)
                    polygon.srid = layer.srs.srid
                    polygon.transform(4326)

                    if isinstance(polygon, Polygon):
                        polygon = MultiPolygon(polygon)
                    version_from = timezone.make_aware(parse_datetime(feature["WERSJA_OD"].value)) if feature[
                        "WERSJA_OD"].value else None
                    version_to = timezone.make_aware(parse_datetime(feature["WERSJA_DO"].value)) if feature[
                        "WERSJA_DO"].value else None
                    valid_from = timezone.make_aware(parse_datetime(feature["WAZNY_OD"].value)) if feature[
                        "WAZNY_OD"].value else None
                    valid_to = timezone.make_aware(parse_datetime(feature["WAZNY_DO"].value)) if feature[
                        "WAZNY_DO"].value else None

                    districts_to_create.append(District(
                        district_code=feature["JPT_KOD_JE"].value,
                        id=feature["JPT_ID"].value,
                        name=feature["JPT_NAZWA_"],
                        type=feature["JPT_SJR_KO"],
                        version_from=version_from,
                        version_to=version_to,
                        valid_from=valid_from,
                        valid_to=valid_to,
                        regon=feature["REGON"],
                        geom=polygon
                    ))
            except Exception as e:
                logger.error("Error processing feature: {}".format(e))
                continue
        if districts_to_create:
            District.objects.bulk_create(districts_to_create, batch_size=1000)
    except Exception as e:
        logger.error("Could not load datasource: {}".format(e))
        return False
    return True

@shared_task
def move_old_meteo_warnings_to_archive():
    """Function to archive old meteo warnings"""
    logger.info("move_old_meteo_warnings_to_archive")

    warnings_to_archive = MeteoWarning.objects.filter(valid_to__lt=timezone.now())
    logger.info(f"Found {warnings_to_archive.count()} warnings to archive")

    for warning in warnings_to_archive:
        try:
            with transaction.atomic():
                archived, created = MeteoWarningArchive.objects.update_or_create(
                    id=warning.id,
                    defaults={
                        'name_of_event': warning.name_of_event,
                        'grade': warning.grade,
                        'probability': warning.probability,
                        'valid_from': warning.valid_from,
                        'valid_to': warning.valid_to,
                        'published': warning.published,
                        'content': warning.content,
                        'comment': warning.comment,
                        'office': warning.office,
                    }
                )
                archived.districts.clear()
                archived.districts.add(*warning.districts.all())
                warning.delete()

        except Exception as e:
            logger.error(f"Could not archive warning {warning.id}: {e}")

    logger.info("Archiving process completed")


@worker_ready.connect
def run_at_start(sender, **kwargs):
    generate_districts()


@shared_task
def get_meteo_warnings():
    """Function that is called every minute to download current meteorological warnings"""
    logger.info("get_meteo_warnings_")
    events = api_request('https://danepubliczne.imgw.pl/api/data/warningsmeteo')
    for event in events:
        try:
            existing_warning = MeteoWarning.objects.get(id=event.get("id"))
            if warning_has_changed(existing_warning, event):
                logger.info(f"Warning {event.get('id')} was updated (detected changes in fields)")
                update_warning(existing_warning, event)
        except MeteoWarning.DoesNotExist:
            create_warning(event)


def create_warning(event):
    """Create Warning if not exists in db"""
    valid_from = parse_safe_datetime(event.get("obowiazuje_od"))
    valid_to = parse_safe_datetime(event.get("obowiazuje_do"))
    published = parse_safe_datetime(event.get("opublikowano"))
    try:
        with transaction.atomic():
            meteo = MeteoWarning.objects.create(
                id=event["id"],
                name_of_event=event.get("nazwa_zdarzenia"),
                grade=event.get("stopien"),
                probability=event.get("prawdopodobienstwo"),
                valid_from=valid_from,
                valid_to=valid_to,
                published=published,
                content=event.get("tresc"),
                comment=event.get("komentarz"),
                office=event.get("biuro")
            )
            districts = District.objects.filter(district_code__in=event.get("teryt"))
            meteo.districts.add(*districts)
    except DatabaseError as e:
        logger.error("Database error saving warning {}: {}".format(event.get('id'), e))
    except Exception as e:
        logger.error("Unexpected error saving warning {}: {}".format(event.get('id'), e))


def update_warning(existing_warning, event):
    """Update warning if published date changed"""
    try:
        with transaction.atomic():
            valid_from = parse_safe_datetime(event.get("obowiazuje_od"))
            valid_to = parse_safe_datetime(event.get("obowiazuje_do"))
            published = parse_safe_datetime(event.get("opublikowano"))

            existing_warning.name_of_event = event.get("nazwa_zdarzenia", "")
            existing_warning.grade = event.get("stopien")
            existing_warning.probability = event.get("prawdopodobienstwo")
            existing_warning.valid_from = valid_from
            existing_warning.valid_to = valid_to
            existing_warning.published = published
            existing_warning.content = event.get("tresc")
            existing_warning.comment = event.get("komentarz")
            existing_warning.office = event.get("biuro")
            existing_warning.save()
            existing_warning.districts.clear()
            districts = District.objects.filter(district_code__in=event.get("teryt"))
            existing_warning.districts.add(*districts)
            logger.info(f"Successfully updated warning {existing_warning.id}")
    except DatabaseError as e:
        logger.error(f"Database error updating warning {existing_warning.id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error updating warning {existing_warning.id}: {e}")
