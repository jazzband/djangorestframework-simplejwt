from datetime import datetime
from unittest import TestCase

from rest_framework_simplejwt.utils import datetime_to_epoch


class TestDatetimeToEpoch(TestCase):
    def test_it_should_return_the_correct_values(self):
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1)), 0)
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1, second=1)), 1)
        self.assertEqual(datetime_to_epoch(datetime(year=2000, month=1, day=1)), 946684800)
