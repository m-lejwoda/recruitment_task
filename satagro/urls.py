from django.urls import path

from satagro.api.views import MeteoWarningsApiView

urlpatterns = [
    path('meteo_warnings/', MeteoWarningsApiView.as_view(), name='meteo_warnings'),
]
