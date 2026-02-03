from calendar import timegm
from datetime import datetime, timezone

from django.conf import settings
from django.utils.functional import lazy
from django.utils.timezone import is_naive, make_aware


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=timezone.utc)

    return dt


def aware_utcnow():
    return datetime.now(timezone.utc)


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return datetime.fromtimestamp(ts, timezone.utc)


def format_lazy(s, *args, **kwargs):
    return s.format(*args, **kwargs)


format_lazy = lazy(format_lazy, str)
