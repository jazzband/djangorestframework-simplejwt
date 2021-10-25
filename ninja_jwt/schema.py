from typing import Optional

from ninja_schema import ModelSchema, model_validator, Schema
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from pydantic import root_validator

from .settings import api_settings
from .tokens import RefreshToken, SlidingToken, UntypedToken
from . import exceptions
if api_settings.BLACKLIST_AFTER_ROTATION:
    from .token_blacklist.models import BlacklistedToken

user_name_field = get_user_model().USERNAME_FIELD


class TokenObtainSerializer(ModelSchema):
    class Config:
        model = get_user_model()
        include = ['password', user_name_field]

    _user = None

    _default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    @root_validator
    def validate_schema(cls, values):
        authenticate_kwargs = {
            user_name_field: values[user_name_field],
            'password': values['password'],
        }

        cls._user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(cls._user):
            raise exceptions.AuthenticationFailed(
                cls._default_error_messages['no_active_account']
            )

        return values

    def output_schema(self):
        raise NotImplementedError('Must implement `output_schema` method for `TokenObtainSerializer` subclasses')

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class TokenObtainPairOutput(Schema):
    refresh: str
    access: str
    username: str


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    @root_validator
    def validate_schema(cls, values):
        super().validate(values)
        refresh = cls.get_token(cls._user)

        values['refresh'] = str(refresh)
        values['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, cls._user)

        return values

    def output_schema(self):
        return TokenObtainSlidingOutput(**self.dict(exclude={'password'}))


class TokenObtainSlidingOutput(Schema):
    token: str
    username: str


class TokenObtainSlidingSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    @root_validator
    def validate_schema(cls, values):
        super().validate(values)
        token = cls.get_token(cls._user)

        values['token'] = str(token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(cls, cls._user)

        return values

    def output_schema(self):
        return TokenObtainSlidingOutput(**self.dict(exclude={'password'}))


class TokenRefreshSerializer(Schema):
    refresh: str
    access: Optional[str]

    @root_validator
    def validate_schema(cls, values):
        refresh = RefreshToken(values['refresh'])

        data = {'access': str(refresh.access_token)}

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

            data['refresh'] = str(refresh)

        return data


class TokenRefreshSlidingSerializer(Schema):
    token: str

    @root_validator
    def validate_schema(cls, values):
        token = SlidingToken(values['token'])

        # Check that the timestamp in the "refresh_exp" claim has not
        # passed
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)

        # Update the "exp" and "iat" claims
        token.set_exp()
        token.set_iat()

        return {'token': str(token)}


class TokenVerifySerializer(Schema):
    token: str

    @root_validator
    def validate_schema(cls, values):
        token = UntypedToken(values['token'])

        if api_settings.BLACKLIST_AFTER_ROTATION:
            jti = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise exceptions.ValidationError("Token is blacklisted")

        return values


class TokenBlacklistSerializer(Schema):
    refresh: str

    @root_validator
    def validate_schema(cls, values):
        refresh = RefreshToken(values['refresh'])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return values
