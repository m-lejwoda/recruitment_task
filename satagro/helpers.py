import logging

import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)


def parse_safe_datetime(val):
    """Parse safe datetime string"""
    try:
        result = timezone.make_aware(parse_datetime(val))
        return result
    except (TypeError, AttributeError):
        return None
def api_request(url):
    """Simple Api request"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: {}".format(e))
        return None

def warning_has_changed(existing_warning, event) -> bool:
    """Compare data if smth was updated"""
    name_of_event = event.get("nazwa_zdarzenia")
    grade = event.get("stopien")
    probability = event.get("prawdopodobienstwo")
    valid_from = parse_safe_datetime(event.get("obowiazuje_od"))
    valid_to = parse_safe_datetime(event.get("obowiazuje_do"))
    published = parse_safe_datetime(event.get("opublikowano"))
    content = event.get("tresc", "")
    comment = event.get("komentarz", "")
    office = event.get("biuro", "")

    current_districts = set(existing_warning.districts.values_list('district_code', flat=True))
    new_districts = set(event.get("teryt", []))
    return (
        existing_warning.name_of_event != name_of_event or
        existing_warning.grade != grade or
        existing_warning.probability != probability or
        existing_warning.valid_from != valid_from or
        existing_warning.valid_to != valid_to or
        existing_warning.published != published or
        existing_warning.content != content or
        existing_warning.comment != comment or
        existing_warning.office != office or
        current_districts != new_districts
    )
