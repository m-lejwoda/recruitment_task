import logging
from types import SimpleNamespace

from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from satagro.api.views import create_point, check_lat_and_lon
from satagro.helpers import parse_safe_datetime, api_request

logger = logging.getLogger(__name__)
def test_parse_safe_datetime_should_report_none_if_none_given():
    res = parse_safe_datetime(None)
    assert res is None

def test_parse_safe_datetime_should_report_none_if_wrong_date_given():
    res = parse_safe_datetime('sa12324432das')
    assert res is None

def test_parse_safe_datetime_should_report_correct_value_if_date_is_correct():
    res = parse_safe_datetime("2025-09-16 03:00:00")
    res2 = timezone.make_aware(parse_datetime("2025-09-16 03:00:00"))
    assert res == res2
    assert res is not None

# def test_parse_safe_datetime_should_report_correct_value_if_date_is_in_differnt_format():
#     res = parse_safe_datetime("16-09-2025 03:00:00")
#     res2 = timezone.make_aware(parse_datetime("2025-09-16 03:00:00"))
#     assert res == res2
#     assert res is not None

def test_api_request_return_req_when_correct_date_given():
    req = api_request("https://danepubliczne.imgw.pl/api/data/warningsmeteo")
    assert req is not None

def test_api_request_return_none_when_correct_date_without_https_given():
    req = api_request("https://danepubliczne.imgw.pl/api/data/warningsmeteoa")
    assert req is None

"""Test views functions create_point, check_lat_and_lon get_district_with_warnings"""

def test_create_point_if_both_values_are_correct():
    res = create_point(43.554544545, 51.4043433434)
    assert type(res[0]) == Point

def test_create_check_lat_and_lon_if_return_error_when_lat_missing():
    request = SimpleNamespace(query_params={"lon": "21.2432243234"})
    res = check_lat_and_lon(request)
    assert res.status_code == 400
    assert res.data["error"] == "lon and lat are required"

def test_create_check_lat_and_lon_if_return_error_when_value_is_incorrect():
    request = SimpleNamespace(query_params={"lon": "21.2432243234", "lat": "43.24322dfs43234"})
    res = check_lat_and_lon(request)
    assert res.status_code == 400
    assert res.data["error"] == "lon or lat or both are in incorrect format. Remember that both must be numbers."


def test_create_check_lat_and_lon_if_return_correct_values():
    request = SimpleNamespace(query_params={"lon": "21.2432243234", "lat": "43.2432243234"})
    res = check_lat_and_lon(request)
    assert res == {'lat':43.2432243234, 'lon': 21.2432243234}

#TODO get_district_with_warnings