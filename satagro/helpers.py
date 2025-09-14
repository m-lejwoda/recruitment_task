import logging

import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)


def parse_safe_datetime(val):
    try:
        result = timezone.make_aware(parse_datetime(val))
        return result
    except (TypeError, AttributeError):
        return None
def api_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: {}".format(e))
        return None