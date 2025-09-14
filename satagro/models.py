from django.contrib.gis.db.models import MultiPolygonField
from django.core.validators import MinLengthValidator
from django.db import models

class District(models.Model):
    id = models.IntegerField() #JPT_ID
    district_code = models.CharField(max_length=4, primary_key=True) #JPT_KOD_JE
    name = models.CharField(max_length=100) #JPT_NAZWA_
    type = models.CharField(max_length=100) #JPT_SJR_KO
    version_from = models.DateTimeField(null=True, default=None) #WERSJA_OD
    version_to = models.DateTimeField(null=True, default=None) #WERSJA_DO
    valid_from = models.DateTimeField(null=True, default=None) #WAZNY_OD
    valid_to = models.DateTimeField(null=True, default=None) #WAZNY_DO
    regon = models.CharField(max_length=14,
                             null=True,
                             validators=[MinLengthValidator(7)]) #REGON
    geom = MultiPolygonField(srid=4326, spatial_index=True) #geom

    def __str__(self):
        return "{} - {}".format(self.name, self.district_code)


class MeteoWarning(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name_of_event = models.CharField(max_length=100)
    grade = models.CharField(max_length=3)
    probability = models.CharField(max_length=3)
    valid_from = models.DateTimeField(null=True, default=None)
    valid_to = models.DateTimeField(null=True, default=None)
    published = models.DateTimeField(null=True, default=None)
    content = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    office = models.CharField(max_length=255, blank=True)
    districts = models.ManyToManyField(District, blank=True)
    def __str__(self):
        return "{} - {}".format(self.name_of_event, self.id)


class MeteoWarningArchive(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name_of_event = models.CharField(max_length=100)
    grade = models.CharField(max_length=3)
    probability = models.CharField(max_length=3)
    valid_from = models.DateTimeField(null=True, default=None)
    valid_to = models.DateTimeField(null=True, default=None)
    published = models.DateTimeField(null=True, default=None)
    content = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    office = models.CharField(max_length=255, blank=True)
    districts = models.ManyToManyField(District, blank=True)

    def __str__(self):
        return "{} - {}".format(self.name_of_event, self.id)




