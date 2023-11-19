import importlib
from datetime import timedelta
from typing import Dict
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from ninja import Schema
from ninja_extra import api_controller
from ninja_extra.testing import TestClient
from pydantic import Field

from ninja_jwt import controller
from ninja_jwt.schema import (
    TokenBlacklistInputSchema,
    TokenObtainInputSchemaBase,
    TokenObtainSlidingInputSchema,
    TokenRefreshInputSchema,
    TokenRefreshSlidingInputSchema,
    TokenRefreshSlidingOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings
from ninja_jwt.tokens import AccessToken, RefreshToken, SlidingToken
from ninja_jwt.utils import aware_utcnow, datetime_from_epoch, datetime_to_epoch

User = get_user_model()


class MyNewObtainPairTokenSchemaOutput(Schema):
    refresh: str
    access: str
    first_name: str
    last_name: str


class MyNewObtainTokenSlidingSchemaOutput(Schema):
    token: str
    first_name: str
    last_name: str


class MyNewObtainPairSchemaInput(TokenObtainInputSchemaBase):
    @classmethod
    def get_response_schema(cls):
        return MyNewObtainPairTokenSchemaOutput

    @classmethod
    def get_token(cls, user) -> Dict:
        values = {}
        refresh = RefreshToken.for_user(user)
        values["refresh"] = str(refresh)
        values["access"] = str(refresh.access_token)
        values.update(
            first_name=user.first_name, last_name=user.last_name
        )  # this will be needed when creating output schema
        return values


class MyNewObtainTokenSlidingSchemaInput(TokenObtainSlidingInputSchema):
    my_extra_field: str

    def check_user_authentication_rule(self) -> bool:
        return api_settings.USER_AUTHENTICATION_RULE(self._user)

    @classmethod
    def get_response_schema(cls):
        return MyNewObtainTokenSlidingSchemaOutput

    def to_response_schema(self):
        return MyNewObtainTokenSlidingSchemaOutput(
            first_name=self._user.first_name,
            last_name=self._user.last_name,
            **self.get_response_schema_init_kwargs(),
        )


class MyTokenRefreshSlidingOutputSchema(TokenRefreshSlidingOutputSchema):
    ninja_jwt: str = Field(default="Ninja JWT")


class MyTokenRefreshInputSchema(TokenRefreshInputSchema):
    pass


class MyTokenRefreshSlidingInputSchema(TokenRefreshSlidingInputSchema):
    @classmethod
    def get_response_schema(cls):
        return MyTokenRefreshSlidingOutputSchema


class MyTokenVerifyInputSchema(TokenVerifyInputSchema):
    pass


class MyTokenBlacklistInputSchema(TokenBlacklistInputSchema):
    pass


class InvalidTokenSchema(Schema):
    whatever: str


@pytest.mark.django_db
class TestTokenObtainPairViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="John",
            last_name="Doe",
        )

    def test_success(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_PAIR_INPUT_SCHEMA",
                "tests.test_custom_schema.MyNewObtainPairSchemaInput",
            )

            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTDefaultController)
            res = client.post(
                "/pair",
                json={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
                content_type="application/json",
            )

        assert res.status_code == 200
        data = res.json()
        assert "access" in data
        assert "refresh" in data

        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"


@pytest.mark.django_db
class TestTokenRefreshViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_refresh_works_fine(self, monkeypatch):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA",
                "tests.test_custom_schema.MyTokenRefreshInputSchema",
            )
            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTDefaultController)
            with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
                fake_aware_utcnow.return_value = now

                res = client.post(
                    "/refresh",
                    json={"refresh": str(refresh)},
                    content_type="application/json",
                )

        assert res.status_code == 200
        data = res.json()
        access = AccessToken(data["access"])

        assert refresh["test_claim"] == access["test_claim"]
        assert access["exp"] == datetime_to_epoch(
            now + api_settings.ACCESS_TOKEN_LIFETIME
        )


@pytest.mark.django_db
class TestTokenObtainSlidingViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="John",
            last_name="Doe",
        )

    def test_incomplete_data(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA",
                "tests.test_custom_schema.MyNewObtainTokenSlidingSchemaInput",
            )
            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTSlidingController)
            res = client.post(
                "/sliding",
                json={
                    User.USERNAME_FIELD: self.username,
                    "password": "test_password",
                },
                content_type="application/json",
            )
        assert res.status_code == 422
        data = res.json()
        assert data == {
            "detail": [
                {
                    "loc": ["body", "user_token", "my_extra_field"],
                    "msg": "Field required",
                    "type": "missing",
                }
            ]
        }

    def test_success(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA",
                "tests.test_custom_schema.MyNewObtainTokenSlidingSchemaInput",
            )
            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTSlidingController)
            res = client.post(
                "/sliding",
                json={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                    "my_extra_field": "some_data",
                },
                content_type="application/json",
            )

        assert res.status_code == 200
        data = res.json()

        assert "token" in data
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"


@pytest.mark.django_db
class TestTokenRefreshSlidingViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_update_token_exp_claim_if_everything_ok(self, monkeypatch):
        now = aware_utcnow()

        token = SlidingToken()
        exp = now + api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1)
        token.set_exp(
            from_time=now,
            lifetime=api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1),
        )
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA",
                "tests.test_custom_schema.MyTokenRefreshSlidingInputSchema",
            )
            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTSlidingController)
            # View returns 200
            res = client.post(
                "/sliding/refresh",
                json={"token": str(token)},
                content_type="application/json",
            )
        assert res.status_code == 200
        data = res.json()
        assert data["ninja_jwt"] == "Ninja JWT"
        # Expiration claim has moved into future
        new_token = SlidingToken(data["token"])
        new_exp = datetime_from_epoch(new_token["exp"])

        assert exp < new_exp


@pytest.mark.django_db
class TestTokenVerifyViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_return_200_if_everything_okay(self, monkeypatch):
        token = RefreshToken()
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_VERIFY_INPUT_SCHEMA",
                "tests.test_custom_schema.MyTokenVerifyInputSchema",
            )
            importlib.reload(controller)
            client = TestClient(controller.NinjaJWTDefaultController)
            res = client.post(
                "/verify", json={"token": str(token)}, content_type="application/json"
            )
        assert res.status_code == 200
        assert res.json() == {}


@pytest.mark.django_db
class TestTokenBlacklistViewCustomSchema:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_return_if_everything_ok(self, monkeypatch):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # View returns 200
        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_BLACKLIST_INPUT_SCHEMA",
                "tests.test_custom_schema.MyTokenBlacklistInputSchema",
            )
            importlib.reload(controller)
            client = TestClient(api_controller()(controller.TokenBlackListController))
            with patch("ninja_jwt.tokens.aware_utcnow") as fake_aware_utcnow:
                fake_aware_utcnow.return_value = now

                res = client.post(
                    "/blacklist",
                    json={"refresh": str(refresh)},
                    content_type="application/json",
                )

        assert res.status_code == 200

        assert res.json() == {}


importlib.reload(controller)


class TestSchemaControlExceptions:
    def test_verify_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_VERIFY_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_VERIFY_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.InputSchemaMixin'>`"
            )

    def test_blacklist_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_BLACKLIST_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_BLACKLIST_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.InputSchemaMixin'>`"
            )

    def test_obtain_pair_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_PAIR_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_OBTAIN_PAIR_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.TokenInputSchemaMixin'>`"
            )

    def test_obtain_pair_refresh_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.InputSchemaMixin'>`"
            )

    def test_sliding_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.TokenInputSchemaMixin'>`"
            )

    def test_sliding_refresh_schema_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(
                api_settings,
                "TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA",
                "tests.test_custom_schema.InvalidTokenSchema",
            )
            with pytest.raises(Exception) as ex:
                SchemaControl(api_settings)
            assert (
                str(ex.value)
                == "TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA type must inherit from `<class 'ninja_jwt.schema.InputSchemaMixin'>`"
            )
