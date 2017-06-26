from __future__ import unicode_literals

from datetime import datetime
from unittest import TestCase

from django.utils import six
from rest_framework_simplejwt.utils import datetime_to_epoch, format_lazy


class TestDatetimeToEpoch(TestCase):
    def test_it_should_return_the_correct_values(self):
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1)), 0)
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1, second=1)), 1)
        self.assertEqual(datetime_to_epoch(datetime(year=2000, month=1, day=1)), 946684800)


class TestFormatLazy(TestCase):
    def test_it_should_work(self):
        obj = format_lazy('{} {}', 'arst', 'zxcv')

        self.assertNotIsInstance(obj, str)
        self.assertEqual(six.text_type(obj), 'arst zxcv')
