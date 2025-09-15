from datetime import timedelta

import pytest

from satagro.api.views import create_point, get_district_with_warnings
from satagro.conftest import create_event_with_params
from satagro.models import MeteoWarning, MeteoWarningArchive, District
from satagro.tasks import move_old_meteo_warnings_to_archive, generate_districts, create_warning, update_warning


@pytest.fixture(scope="session", autouse=True)
def setup_districts(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        generate_districts()

@pytest.mark.django_db
def test_how_many_districts_in_db(setup_districts):
    districts = District.objects.all()
    assert len(districts) == 380

@pytest.mark.django_db
def test_if_point_is_in_poznanski_district(setup_districts):
    point = create_point(17.008185553339786,52.56698693108296)
    res = get_district_with_warnings(point)
    assert type(res[0]) == District
    assert res[0].name == "powiat poznański"

@pytest.mark.django_db
def test_if_point_is_good_but_out_of_polish_country_bounds(setup_districts):
    point = create_point(0,0)
    res = get_district_with_warnings(point)
    assert res[0] is None


"""Meteo Warning Archive"""
def test_archiving_normal(warning_factory):
    warning = warning_factory(valid_to_delta=timedelta(days=1))
    move_old_meteo_warnings_to_archive()
    archived = MeteoWarningArchive.objects.get(id=warning.id)
    assert archived.name_of_event == "Test Event"
    with pytest.raises(MeteoWarning.DoesNotExist):
        MeteoWarning.objects.get(id=warning.id)


def test_archiving_minute_after(warning_factory):
    warning = warning_factory(valid_to_delta=timedelta(minutes=1))
    move_old_meteo_warnings_to_archive()
    archived = MeteoWarningArchive.objects.get(id=warning.id)
    assert archived.name_of_event == "Test Event"
    with pytest.raises(MeteoWarning.DoesNotExist):
        MeteoWarning.objects.get(id=warning.id)

@pytest.mark.django_db
def test_create_warning_if_creates_correctly():
    event = create_event_with_params(
        valid_to_delta=timedelta(minutes=1),
        nazwa_zdarzenia="Custom Event"
    )
    create_warning(event)
    assert len(MeteoWarning.objects.all()) == 1

@pytest.mark.django_db
def test_update_warning_if_updates_correctly():
    event = create_event_with_params(
        valid_to_delta=timedelta(minutes=1),
        nazwa_zdarzenia="Custom Event"
    )
    create_warning(event)
    assert MeteoWarning.objects.filter(id=event['id']).first().name_of_event == "Custom Event"
    meteo_warning = MeteoWarning.objects.get(id=event['id'])
    event['nazwa_zdarzenia'] = "Custom"
    update_warning(meteo_warning, event)
    assert len(MeteoWarning.objects.all()) == 1
    assert MeteoWarning.objects.filter(id=event['id']).first().name_of_event == "Custom"
