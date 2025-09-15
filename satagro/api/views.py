from django.contrib.gis.geos import Point
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from satagro.api.serializers import DistrictSerializer
from satagro.models import District, MeteoWarning


def create_point(lon, lat):
    """Function to create a Point object in WGS84 projection"""
    try:
        return Point(lon, lat, srid=4326), None
    except Exception as e:
        return None, str(e)


def get_district_with_warnings(point: Point):
    """Function to get all districts with warnings. valid_to__gte is optional because i have worker which runs every hour and removing old records."""
    try:
        district = District.objects.filter(
            geom__contains=point
        ).prefetch_related(
            Prefetch("meteowarning_set",
                     queryset=MeteoWarning.objects.filter(valid_to__gte=timezone.now()))
        ).first()
        return district, None
    except Exception as e:
        return None, str(e)


def check_lat_and_lon(request):
    """Check if lat and lon are valid"""
    lat_param = request.query_params.get('lat')
    lon_param = request.query_params.get('lon')
    if lat_param is None or lon_param is None:
        return Response({"error": "lon and lat are required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        lat = float(lat_param)
        lon = float(lon_param)
        return {"lat": lat, "lon": lon}
    except ValueError:
        return Response(
            {"error": "lon or lat or both are in incorrect format. Remember that both must be numbers."},
            status=status.HTTP_400_BAD_REQUEST
        )


class MeteoWarningsApiView(APIView):
    """Api View for getting meteo warnings base on lon lat"""
    def get(self, request, *args, **kwargs):
        result = check_lat_and_lon(request)
        if "error" in result:
            return result["error"]
        lat, lon = result["lat"], result["lon"]
        try:
            point, error = create_point(lon, lat)
            if error:
                return Response({"error": "Invalid coordinates: {}".format(error)}, status=400)
            district, error = get_district_with_warnings(point)
            if error:
                return Response({"error": "Database error: {}".format(error)}, status=500)
            if not district:
                return Response({"error": "Localization is out of Polish Country boundaries"}, status=404)
            serializer = DistrictSerializer(district, context={'lon': lon, 'lat': lat})
            return Response(serializer.data)
        except Exception:
            return Response({"error": "Something went wrong. Try again."}, status=status.HTTP_400_BAD_REQUEST)

