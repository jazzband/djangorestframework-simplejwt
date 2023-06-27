import hashlib
from calendar import timegm
from datetime import datetime, timezone
from typing import Callable

from django.conf import settings
from django.utils.functional import lazy
from django.utils.timezone import is_naive, make_aware


def get_md5_hash_password(password: str) -> str:
    """
    Returns MD5 hash of the given password
    """
    return hashlib.md5(password.encode()).hexdigest().upper()


def make_utc(dt: datetime) -> datetime:
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=timezone.utc)

    return dt


def aware_utcnow() -> datetime:
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt: datetime) -> int:
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts: float) -> datetime:
    return make_utc(datetime.utcfromtimestamp(ts))


def format_lazy(s: str, *args, **kwargs) -> str:
    return s.format(*args, **kwargs)


format_lazy: Callable = lazy(format_lazy, str)
