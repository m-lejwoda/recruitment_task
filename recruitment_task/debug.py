import os

import django
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point, GEOSGeometry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recruitment_task.settings")
django.setup()
from satagro.tasks import generate_districts, get_meteo_warnings

"""Here is playground to test app functionalities"""


def test_functionality():
    with open('./plik_testowy.txt') as f:
        for line in f:
            print(line)


def test_gml_functionality():
    ds = DataSource("./pgr.gml")
    layer = ds[0]
    print(layer.srs.name)  # np. WGS 84 / EPSG:4326
    print(layer.srs.wkt)
    lat, lon = 52.559973222669726, 16.43304832145737
    point = Point(lon, lat, srid=4326)
    for feature in layer:
        polygon = GEOSGeometry(feature.geom.wkt)
        polygon.srid = layer.srs.srid
        polygon.transform(4326)
        # for i in feature.fields:
        #     print(i, feature[i])
        # print(feature["JPT_KOD_JE"])
        # print(feature["JPT_NAZWA_"])
        # print(feature.geom)
        # if polygon.contains(point):
        #     print("contain")
        # else:
        #     print("not contain")
        # geom = feature.geom
        # name = feature.get("name")
        # print("geom", geom)
        # print("name", name)
    # print(layer)


# test_functionality()
# test_gml_functionality()


# generate_districts()
get_meteo_warnings()
# move_old_meteo_warnings_to_archive()
# mw = MeteoWorker()
# parse_safe_datetime("2025-09-14 18:00:00")
# mw.parse_safe_datetime(None)
# mw.parse_safe_datetime("sadasdasdasdadsa")
# api_request("https://danepubliczne.imgw.pl/api/data/warningsmeteo")
# api_request("sagfdgsddgf")
# get_meteo_warnings()
# move_old_meteo_warnings_to_archive()
