from typing import Dict, Optional, Type, cast

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractUser, update_last_login
from django.utils.translation import gettext_lazy as _
from ninja_schema import ModelSchema, Schema
from pydantic import root_validator

from ninja_jwt.utils import token_error

from . import exceptions
from .settings import api_settings
from .tokens import RefreshToken, SlidingToken, Token, UntypedToken

if api_settings.BLACKLIST_AFTER_ROTATION:
    from .token_blacklist.models import BlacklistedToken

user_name_field = get_user_model().USERNAME_FIELD  # type: ignore


class AuthUserSchema(ModelSchema):
    class Config:
        model = get_user_model()
        include = [user_name_field]


class TokenObtainSerializer(ModelSchema):
    class Config:
        model = get_user_model()
        include = ["password", user_name_field]

    _user: Optional[Type[AbstractUser]] = None

    _default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    @root_validator(pre=True)
    def validate_inputs(cls, values: Dict) -> dict:
        if user_name_field not in values and "password" not in values:
            raise exceptions.ValidationError(
                {
                    user_name_field: f"{user_name_field} is required",
                    "password": "password is required",
                }
            )

        if not values.get(user_name_field):
            raise exceptions.ValidationError(
                {user_name_field: f"{user_name_field} is required"}
            )

        if not values.get("password"):
            raise exceptions.ValidationError({"password": "password is required"})

        cls._user = authenticate(**values)

        if not api_settings.USER_AUTHENTICATION_RULE(cls._user):
            raise exceptions.AuthenticationFailed(
                cls._default_error_messages["no_active_account"]
            )

        return values

    def output_schema(self) -> Type[Schema]:
        raise NotImplementedError(
            "Must implement `output_schema` method for `TokenObtainSerializer` subclasses"
        )

    @classmethod
    def get_token(cls, user: Type[AbstractUser]) -> Type[Token]:
        raise NotImplementedError(
            "Must implement `get_token` method for `TokenObtainSerializer` subclasses"
        )


class TokenObtainPairOutput(AuthUserSchema):
    refresh: str
    access: str


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user: Type[AbstractUser]) -> Type[Token]:
        return RefreshToken.for_user(user)

    @root_validator
    def validate_schema(cls, values: Dict) -> dict:
        refresh = cls.get_token(cls._user)
        refresh = cast(RefreshToken, refresh)

        values["refresh"] = str(refresh)
        values["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, cls._user)

        return values

    def output_schema(self):
        return TokenObtainPairOutput(**self.dict(exclude={"password"}))


class TokenObtainSlidingOutput(AuthUserSchema):
    token: str


class TokenObtainSlidingSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user: Type[AbstractUser]) -> Type[Token]:
        return SlidingToken.for_user(user)

    @root_validator
    def validate_schema(cls, values: Dict) -> dict:
        token = cls.get_token(cls._user)

        values["token"] = str(token)

        if api_settings.UPDATE_LAST_LOGIN and cls._user:
            update_last_login(cls, cls._user)

        return values

    def output_schema(self):
        return TokenObtainSlidingOutput(**self.dict(exclude={"password"}))


class TokenRefreshSchema(Schema):
    refresh: str

    @root_validator
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("refresh"):
            raise exceptions.ValidationError({"refresh": "token is required"})
        return values


class TokenRefreshSerializer(Schema):
    refresh: str
    access: Optional[str]

    @root_validator
    @token_error
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("refresh"):
            raise exceptions.ValidationError({"refresh": "refresh token is required"})

        refresh = RefreshToken(values["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data


class TokenRefreshSlidingSchema(Schema):
    token: str

    @root_validator
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("token"):
            raise exceptions.ValidationError({"token": "token is required"})
        return values


class TokenRefreshSlidingSerializer(Schema):
    token: str

    @root_validator
    @token_error
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("token"):
            raise exceptions.ValidationError({"token": "token is required"})

        token = SlidingToken(values["token"])

        # Check that the timestamp in the "refresh_exp" claim has not
        # passed
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)

        # Update the "exp" and "iat" claims
        token.set_exp()
        token.set_iat()

        return {"token": str(token)}


class TokenVerifySerializer(Schema):
    token: str

    @root_validator
    @token_error
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("token"):
            raise exceptions.ValidationError({"token": "token is required"})
        token = UntypedToken(values["token"])

        if (
            api_settings.BLACKLIST_AFTER_ROTATION
            and "ninja_jwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise exceptions.ValidationError("Token is blacklisted")

        return values


class TokenBlacklistSerializer(Schema):
    refresh: str

    @root_validator
    @token_error
    def validate_schema(cls, values: Dict) -> dict:
        if not values.get("refresh"):
            raise exceptions.ValidationError({"refresh": "refresh token is required"})
        refresh = RefreshToken(values["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return values
