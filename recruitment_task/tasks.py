import logging
import traceback
import requests
from celery import shared_task
from celery.signals import worker_ready
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.db import transaction, DatabaseError
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from satagro.models import MeteoWarning, District, MeteoWarningArchive
from satagro.helpers import api_request, parse_safe_datetime

logger = logging.getLogger(__name__)

@shared_task
def generate_districts():
    """Function to generate districts from a Geoportal districts file (pgr.gml)"""
    logger.info("generating districts")
    ds = DataSource("./pgr.gml")
    layer = ds[0]
    for feature in layer:
        polygon = GEOSGeometry(feature.geom.wkt)
        polygon.srid = layer.srs.srid
        polygon.transform(4326)
        if isinstance(polygon, Polygon):
            polygon = MultiPolygon(polygon)
        try:
            District.objects.get(district_code=feature["JPT_KOD_JE"])
        except District.DoesNotExist:
            try:
                version_from = timezone.make_aware(parse_datetime(feature["WERSJA_OD"].value)) if feature["WERSJA_OD"].value else None
                version_to = timezone.make_aware(parse_datetime(feature["WERSJA_DO"].value)) if feature["WERSJA_DO"].value else None
                valid_from = timezone.make_aware(parse_datetime(feature["WAZNY_OD"].value)) if feature["WAZNY_OD"].value else None
                valid_to = timezone.make_aware(parse_datetime(feature["WAZNY_DO"].value)) if feature["WAZNY_DO"].value else None
                District.objects.create(district_code=feature["JPT_KOD_JE"],
                                        id=feature["JPT_ID"].value,
                                        name=feature["JPT_NAZWA_"],
                                        type=feature["JPT_SJR_KO"],
                                        version_from=version_from,
                                        version_to=version_to,
                                        valid_from=valid_from,
                                        valid_to=valid_to,
                                        regon=feature["REGON"],
                                        geom=polygon)
            except Exception as e:
                logger.error("Could not create district {}: {}".format(feature['JPT_KOD_JE'], e))


# @shared_task
# def get_meteo_warnings():
#     """Function that is called every minute to download current meteorological warnings"""
#     logger.info("get_meteo_warnings")
#     req = requests.get('https://danepubliczne.imgw.pl/api/data/warningsmeteo')
#     events = req.json()
#     for event in events:
#         try:
#             MeteoWarning.objects.get(id=event["id"])
#         except MeteoWarning.DoesNotExist:
#             valid_from = timezone.make_aware(parse_datetime(event["obowiazuje_od"]))
#             valid_to = timezone.make_aware(parse_datetime(event["obowiazuje_do"]))
#             published = timezone.make_aware(parse_datetime(event["opublikowano"]))
#             with transaction.atomic():
#                 meteo = MeteoWarning.objects.create(
#                     id=event["id"],
#                     name_of_event=event["nazwa_zdarzenia"],
#                     grade=event["stopien"],
#                     probability=event["prawdopodobienstwo"],
#                     valid_from=valid_from,
#                     valid_to=valid_to,
#                     published=published,
#                     content=event["tresc"],
#                     comment=event["komentarz"],
#                     office=event["biuro"],
#                 )
#                 districts = District.objects.filter(district_code__in=event["teryt"])
#                 meteo.districts.add(*districts)

@shared_task
def move_old_meteo_warnings_to_archive():
    """Function to archive old meteo warnings"""
    logger.info("move_old_meteo_warnings_to_archive")
    try:
        warnings_to_archive = MeteoWarning.objects.filter(valid_to__lt=timezone.now())
        with transaction.atomic():
            for warning in warnings_to_archive:
                archived = MeteoWarningArchive.objects.create(
                    id=warning.id,
                    name_of_event=warning.name_of_event,
                    grade=warning.grade,
                    probability=warning.probability,
                    valid_from=warning.valid_from,
                    valid_to=warning.valid_to,
                    published=warning.published,
                    content=warning.content,
                    comment=warning.comment,
                    office=warning.office,
                )
                archived.districts.add(*warning.districts.all())
                warning.delete()
    except Exception as e:
        logger.error("Could not archive old meteo warnings: {}".format(e))

@worker_ready.connect
def run_at_start(sender, **kwargs):
    with sender.app.connection():
        sender.app.send_task(
            "recruitment_task.tasks.generate_districts",
        )

@shared_task
def get_meteo_warnings():
    """Function that is called every minute to download current meteorological warnings"""
    logger.info("get_meteo_warnings_")
    events = api_request('https://danepubliczne.imgw.pl/api/data/warningsmeteo')
    for event in events:
        try:
            # TODO check to actual
            MeteoWarning.objects.get(id=event["id"])

        except MeteoWarning.DoesNotExist:
            valid_from = parse_safe_datetime(event["obowiazuje_od"])
            valid_to = parse_safe_datetime(event["obowiazuje_do"])
            published = parse_safe_datetime(event["opublikowano"])
            try:
                with transaction.atomic():
                    meteo = MeteoWarning.objects.create(
                        id=event["id"],
                        name_of_event=event["nazwa_zdarzenia"],
                        grade=event["stopien"],
                        probability=event["prawdopodobienstwo"],
                        valid_from=valid_from,
                        valid_to=valid_to,
                        published=published,
                        content=event["tresc"],
                        comment=event["komentarz"],
                        office=event["biuro"],
                    )
                    districts = District.objects.filter(district_code__in=event["teryt"])
                    meteo.districts.add(*districts)
            except DatabaseError as e:
                logger.error("Database error saving warning {}: {}".format(event['id'],e))
            except Exception as e:
                logger.error("Unexpected error saving warning {}: {}".format(event['id'],e))