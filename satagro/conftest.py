from datetime import timedelta

import pytest
from django.utils import timezone

from satagro.models import MeteoWarning


@pytest.fixture
def warning_factory(db):
    """MeteoWarning factory"""
    def create_warning(
        valid_to_delta=None,
        name_of_event="Test Event",
        grade="A",
        probability=50,
        valid_from_delta=timedelta(days=5),
        published_delta=timedelta(days=6),
        content="Test content",
        comment="Test comment",
        office="Test office"
    ):
        now = timezone.now()
        return MeteoWarning.objects.create(
            name_of_event=name_of_event,
            grade=grade,
            probability=probability,
            valid_from=now - valid_from_delta,
            valid_to=now - (valid_to_delta or timedelta(days=1)),
            published=now - published_delta,
            content=content,
            comment=comment,
            office=office
        )
    return create_warning