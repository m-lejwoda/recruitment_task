from django.contrib import admin

from satagro.models import District, MeteoWarning, MeteoWarningArchive

admin.site.register(District)
admin.site.register(MeteoWarning)
admin.site.register(MeteoWarningArchive)