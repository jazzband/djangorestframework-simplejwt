from datetime import datetime, timedelta
from unittest.mock import patch

from django.test.utils import override_settings
from django.utils import timezone

from ninja_jwt.utils import (
    aware_utcnow,
    datetime_from_epoch,
    datetime_to_epoch,
    format_lazy,
    make_utc,
)


class TestMakeUtc:
    def test_it_should_return_the_correct_values(self):
        # It should make a naive datetime into an aware, utc datetime if django
        # is configured to use timezones and the datetime doesn't already have
        # a timezone

        # Naive datetime
        dt = datetime(year=1970, month=12, day=1)

        with override_settings(USE_TZ=False):
            dt = make_utc(dt)
            assert timezone.is_naive(dt)

        with override_settings(USE_TZ=True):
            dt = make_utc(dt)
            assert timezone.is_aware(dt)
            assert dt.utcoffset() == timedelta(seconds=0)


class TestAwareUtcnow:
    def test_it_should_return_the_correct_value(self):
        now = datetime.utcnow()

        with patch("ninja_jwt.utils.datetime") as fake_datetime:
            fake_datetime.utcnow.return_value = now

            # Should return aware utcnow if USE_TZ == True
            with override_settings(USE_TZ=True):
                assert timezone.make_aware(now, timezone=timezone.utc) == aware_utcnow()

            # Should return naive utcnow if USE_TZ == False
            with override_settings(USE_TZ=False):
                assert now == aware_utcnow()


class TestDatetimeToEpoch:
    def assertEqual(self, value_1, value_2):
        assert value_1 == value_2

    def test_it_should_return_the_correct_values(self):
        self.assertEqual(datetime_to_epoch(datetime(year=1970, month=1, day=1)), 0)
        self.assertEqual(
            datetime_to_epoch(datetime(year=1970, month=1, day=1, second=1)), 1
        )
        self.assertEqual(
            datetime_to_epoch(datetime(year=2000, month=1, day=1)), 946684800
        )


class TestDatetimeFromEpoch:
    def assertEqual(self, value_1, value_2):
        assert value_1 == value_2

    def test_it_should_return_the_correct_values(self):
        with override_settings(USE_TZ=False):
            assert datetime_from_epoch(0) == datetime(year=1970, month=1, day=1)
            assert datetime_from_epoch(1) == datetime(
                year=1970, month=1, day=1, second=1
            )
            assert datetime_from_epoch(946684800) == datetime(year=2000, month=1, day=1)

        with override_settings(USE_TZ=True):
            self.assertEqual(
                datetime_from_epoch(0), make_utc(datetime(year=1970, month=1, day=1))
            )
            self.assertEqual(
                datetime_from_epoch(1),
                make_utc(datetime(year=1970, month=1, day=1, second=1)),
            )
            self.assertEqual(
                datetime_from_epoch(946684800),
                make_utc(datetime(year=2000, month=1, day=1)),
            )


class TestFormatLazy:
    def test_it_should_work(self):
        obj = format_lazy("{} {}", "arst", "zxcv")

        assert not isinstance(obj, str)
        assert str(obj) == "arst zxcv"
