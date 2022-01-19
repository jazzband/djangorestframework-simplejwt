from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from ninja_jwt.settings import api_settings
from ninja_jwt.tokens import AccessToken, RefreshToken, SlidingToken
from ninja_jwt.utils import aware_utcnow, datetime_from_epoch, datetime_to_epoch

from .utils import APIViewTestCase

User = get_user_model()


@pytest.mark.django_db
class TestTokenObtainPairView(APIViewTestCase):
    view_name = "jwt:token_obtain_pair"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert User.USERNAME_FIELD in res.data
        assert "password" in res.data

        res = self.view_post(
            data={User.USERNAME_FIELD: self.username}, content_type="application/json"
        )
        assert res.status_code == 400
        assert "password" in res.data

        res = self.view_post(
            data={"password": self.password}, content_type="application/json"
        )
        assert res.status_code == 400
        assert User.USERNAME_FIELD in res.data

    def test_credentials_wrong(self):
        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": "test_user",
            },
            content_type="application/json",
        )
        assert res.status_code == 401
        assert "detail" in res.data

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert res.status_code == 401
        assert "detail" in res.data

    def test_success(self):
        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert res.status_code == 200
        assert "access" in res.data
        assert "refresh" in res.data

    def test_update_last_login(self, monkeypatch):
        self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )

        # verify last_login is not updated
        user = User.objects.get(username=self.username)
        assert user.last_login is None

        # verify last_login is updated
        with monkeypatch.context() as m:
            m.setattr(api_settings, "UPDATE_LAST_LOGIN", True)
            self.view_post(
                data={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
                content_type="application/json",
            )
            user = User.objects.get(username=self.username)
            assert user.last_login is not None
            assert timezone.now() >= user.last_login


@pytest.mark.django_db
class TestTokenRefreshView(APIViewTestCase):
    view_name = "jwt:token_refresh"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert "refresh" in res.data

    def test_it_should_return_401_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        res = self.view_post(
            data={"refresh": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(
            data={"refresh": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_return_access_token_if_everything_ok(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now

            res = self.view_post(
                data={"refresh": str(refresh)}, content_type="application/json"
            )

        assert res.status_code == 200

        access = AccessToken(res.data["access"])

        assert refresh["test_claim"] == access["test_claim"]
        assert access["exp"] == datetime_to_epoch(
            now + api_settings.ACCESS_TOKEN_LIFETIME
        )


@pytest.mark.django_db
class TestTokenObtainSlidingView(APIViewTestCase):
    view_name = "jwt:token_obtain_sliding"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert User.USERNAME_FIELD in res.data
        assert "password" in res.data

        res = self.view_post(
            data={User.USERNAME_FIELD: self.username}, content_type="application/json"
        )
        assert res.status_code == 400
        assert "password" in res.data

        res = self.view_post(
            data={"password": self.password}, content_type="application/json"
        )
        assert res.status_code == 400
        assert User.USERNAME_FIELD in res.data

    def test_credentials_wrong(self):
        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": "test_user",
            },
            content_type="application/json",
        )
        assert res.status_code == 401
        assert "detail" in res.data

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert res.status_code == 401
        assert "detail" in res.data

    def test_success(self):
        res = self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )
        assert res.status_code == 200
        assert "token" in res.data

    def test_update_last_login(self, monkeypatch):
        self.view_post(
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
            content_type="application/json",
        )

        # verify last_login is not updated
        user = User.objects.get(username=self.username)
        assert user.last_login is None

        # verify last_login is updated
        with monkeypatch.context() as m:
            m.setattr(api_settings, "UPDATE_LAST_LOGIN", True)
            self.view_post(
                data={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
                content_type="application/json",
            )
            user = User.objects.get(username=self.username)
            assert user.last_login is not None
            assert timezone.now() >= user.last_login


@pytest.mark.django_db
class TestTokenRefreshSlidingView(APIViewTestCase):
    view_name = "jwt:token_refresh_sliding"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert "token" in res.data

    def test_it_should_return_401_if_token_invalid(self):
        token = SlidingToken()
        del token["exp"]

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_return_401_if_token_has_no_refresh_exp_claim(self):
        token = SlidingToken()
        del token[api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM]

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_return_401_if_token_has_refresh_period_expired(self):
        token = SlidingToken()
        token.set_exp(
            api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM, lifetime=-timedelta(seconds=1)
        )

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_update_token_exp_claim_if_everything_ok(self):
        now = aware_utcnow()

        token = SlidingToken()
        exp = now + api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1)
        token.set_exp(
            from_time=now,
            lifetime=api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1),
        )

        # View returns 200
        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 200

        # Expiration claim has moved into future
        new_token = SlidingToken(res.data["token"])
        new_exp = datetime_from_epoch(new_token["exp"])

        assert exp < new_exp


@pytest.mark.django_db
class TestTokenVerifyView(APIViewTestCase):
    view_name = "jwt:token_verify"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert "token" in res.data

    def test_it_should_return_401_if_token_invalid(self):
        token = SlidingToken()
        del token["exp"]

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_return_200_if_everything_okay(self):
        token = RefreshToken()

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 200
        assert len(res.data) == 0

    def test_it_should_ignore_token_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "fake_type"

        res = self.view_post(
            data={"token": str(token)}, content_type="application/json"
        )
        assert res.status_code == 200
        assert len(res.data) == 0


@pytest.mark.django_db
class TestTokenBlacklistView(APIViewTestCase):
    view_name = "jwt:token_blacklist"

    @pytest.fixture(autouse=True)
    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={}, content_type="application/json")
        assert res.status_code == 400
        assert "refresh" in res.data

    def test_it_should_return_401_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        res = self.view_post(
            data={"refresh": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(
            data={"refresh": str(token)}, content_type="application/json"
        )
        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"

    def test_it_should_return_if_everything_ok(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now

            res = self.view_post(
                data={"refresh": str(refresh)}, content_type="application/json"
            )

        assert res.status_code == 200

        assert res.data == {}

    def test_it_should_return_401_if_token_is_blacklisted(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now

            res = self.view_post(
                data={"refresh": str(refresh)}, content_type="application/json"
            )

        assert res.status_code == 200

        self.view_name = "jwt:token_refresh"
        res = self.view_post(
            data={"refresh": str(refresh)}, content_type="application/json"
        )
        # make sure other tests are not affected
        del self.view_name

        assert res.status_code == 401
        assert res.data["code"] == "token_not_valid"
