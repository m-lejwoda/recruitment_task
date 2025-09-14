from rest_framework import serializers

from satagro.models import MeteoWarning, District


class MeteoWarningSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    valid_to = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    published = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    class Meta:
        model = MeteoWarning
        fields = ['id', 'name_of_event', 'valid_from', 'valid_to', 'published', 'content', 'comment','office', 'grade']

class DistrictSerializer(serializers.ModelSerializer):
    warnings = MeteoWarningSerializer(source="meteowarning_set", many=True, read_only=True)
    lon = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()


    class Meta:
        model = District
        fields = ['district_code', 'name', 'lon', 'lat', 'warnings']

    def get_lon(self, obj):
        return self.context.get('lon')

    def get_lat(self, obj):
        return self.context.get('lat')

