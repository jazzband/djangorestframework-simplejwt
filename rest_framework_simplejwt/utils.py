from calendar import timegm

from django.utils import six
from django.utils.functional import lazy


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def format_lazy(s, *args, **kwargs):
    return s.format(*args, **kwargs)

format_lazy = lazy(format_lazy, six.text_type)
