import hashlib
import logging
from calendar import timegm
from collections.abc import Callable
from datetime import datetime, timezone

from django.conf import settings
from django.utils.functional import lazy


def get_password_hash(password: str, algorithm: str = "md5") -> str:
    """
    Returns hash of the given password using specified algorithm.
    Defaults to MD5 for backward compatibility.
    """
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        logger.warning(
            f"Hashing algorithm '{algorithm}' not supported by hashlib. Falling back to MD5."
        )
        hash_obj = hashlib.md5()

    hash_obj.update(password.encode())
    return hash_obj.hexdigest().upper()


def get_md5_hash_password(password: str) -> str:
    """
    Legacy wrapper for MD5 hashing.
    """
    return get_password_hash(password, algorithm="md5")


def make_utc(dt: datetime) -> datetime:
    if settings.USE_TZ and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def aware_utcnow() -> datetime:
    dt = datetime.now(tz=timezone.utc)
    if not settings.USE_TZ:
        dt = dt.replace(tzinfo=None)

    return dt


def datetime_to_epoch(dt: datetime) -> int:
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts: float) -> datetime:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if not settings.USE_TZ:
        dt = dt.replace(tzinfo=None)

    return dt


def format_lazy(s: str, *args, **kwargs) -> str:
    return s.format(*args, **kwargs)


format_lazy: Callable = lazy(format_lazy, str)

logger = logging.getLogger("rest_framework_simplejwt")
