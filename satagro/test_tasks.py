from datetime import timedelta

import pytest

from satagro.models import MeteoWarning, MeteoWarningArchive
from satagro.tasks import move_old_meteo_warnings_to_archive

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
