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
        return MeteoWarning.objects.create(
            name_of_event=name_of_event,
            grade=grade,
            probability=probability,
            valid_from=timezone.now() - valid_from_delta,
            valid_to=timezone.now() - (valid_to_delta or timedelta(days=1)),
            published=timezone.now() - published_delta,
            content=content,
            comment=comment,
            office=office
        )
    return create_warning


@pytest.fixture
def default_event():
    """Default Event fixture"""
    valid_from = (timezone.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    valid_to = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    published = (timezone.now() - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id": "Sk202509152dsffdsdfs02712646",
        "nazwa_zdarzenia": "Test Event",
        "stopien": "A",
        "prawdopodobienstwo": 50,
        "obowiazuje_do": valid_to,
        "obowiazuje_od": valid_from,
        "opublikowano": published,
        "tresc": "Test content",
        "komentarz": "Test comment",
        "biuro": "Test office",
        "teryt": ["3205", "3208", "3213", "2208", "2211", "2212", "2215", "3207", "3209", "3263"]
    }


def create_event_with_params(**kwargs):
    now = timezone.now()
    valid_from = now - kwargs.pop('valid_from_delta', timedelta(days=5))
    valid_to = now - kwargs.pop('valid_to_delta', timedelta(days=1))
    published = now - kwargs.pop('published_delta', timedelta(days=6))

    default_event = {
        "id": "Sk202509152dsffdsdfs02712646",
        "nazwa_zdarzenia": "Test Event",
        "stopien": "A",
        "prawdopodobienstwo": 50,
        "obowiazuje_do": valid_to,
        "obowiazuje_od": valid_from,
        "opublikowano": published,
        "tresc": "Test content",
        "komentarz": "Test comment",
        "biuro": "Test office",
        "teryt": ["3205", "3208", "3213", "2208", "2211", "2212", "2215", "3207", "3209", "3263"]
    }

    default_event.update(kwargs)
    return default_event