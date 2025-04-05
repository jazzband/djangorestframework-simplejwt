import logging
import typing as t
from calendar import timegm
from datetime import datetime
from functools import wraps
from importlib import import_module

from django.conf import settings
from django.utils.functional import lazy

from ninja_jwt import exceptions

try:
    from datetime import timezone
except ImportError:
    from django.utils import timezone


logger = logging.getLogger("django")


def token_error(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.TokenError as tex:
            raise exceptions.InvalidToken(str(tex)) from tex
        except Exception as ex:
            logger.error(f"{func} raised exception: {str(ex)}")
            raise ex

    return _wrap


def import_callable(path_or_callable):
    if callable(path_or_callable):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, str)
        package, attr = path_or_callable.rsplit(".", 1)
        packages = import_module(package)
        return getattr(packages, attr)


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


format_lazy: t.Callable = lazy(format_lazy, str)
