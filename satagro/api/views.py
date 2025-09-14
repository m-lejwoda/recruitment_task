from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from satagro.api.serializers import DistrictSerializer
from satagro.models import District


def create_point(lon, lat):
    try:
        return Point(lon, lat, srid=4326), None
    except Exception as e:
        return None, str(e)


def get_district_with_warnings(point):
    try:
        district = District.objects.filter(
            geom__contains=point
        ).prefetch_related("meteowarning_set").first()
        return district, None
    except Exception as e:
        return None, str(e)


class MeteoWarningsApiView(APIView):
    """Api View for getting meteo warnings base on lon lat"""
    def get(self, request, *args, **kwargs):
        error_lat_lon_response = self.check_lat_and_lon(request)
        if error_lat_lon_response:
            return error_lat_lon_response
        try:
            point, error = create_point(self.lon, self.lat)
            if error:
                return Response({"error": "Invalid coordinates: {}".format(error)}, status=400)
            district, error = get_district_with_warnings(point)
            if error:
                return Response({"error": "Database error: {}".format(error)}, status=500)
            if not district:
                return Response({"error": "Localization is out of Polish Country boundaries"}, status=404)
            serializer = DistrictSerializer(district, context={'lat': self.lat, 'lon': self.lon})
            return Response(serializer.data)
        except Exception:
            return Response({"error": "Something went wrong. Try again."}, status=status.HTTP_400_BAD_REQUEST)

    def check_lat_and_lon(self,request):
        lat_param = request.query_params.get('lat')
        lon_param = request.query_params.get('lon')
        if lat_param is None or lon_param is None:
            return Response({"error": "lon and lat are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.lat = float(lat_param)
            self.lon = float(lon_param)
            return None
        except ValueError:
            return Response(
                {"error": "lon or lat or both are in incorrect format. Remember that both must be numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )

