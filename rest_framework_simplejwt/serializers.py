from typing import Any, Optional, TypeVar

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from .cache import blacklist_cache
from .exceptions import (
    RefreshTokenBlacklistedError,
    TokenError,
    TokenFamilyNotConfigured,
)
from .models import TokenUser
from .settings import api_settings
from .token_blacklist.models import BlacklistedToken
from .tokens import FamilyMixin, RefreshToken, SlidingToken, Token, UntypedToken

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("style", {})

        kwargs["style"]["input_type"] = "password"
        kwargs["write_only"] = True

        super().__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer):
    username_field = get_user_model().USERNAME_FIELD
    token_class: Optional[type[Token]] = None

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(write_only=True)
        self.fields["password"] = PasswordField()

    def validate(self, attrs: dict[str, Any]) -> dict[Any, Any]:
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        return cls.token_class.for_user(user)  # type: ignore


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class TokenObtainSlidingSerializer(TokenObtainSerializer):
    token_class = SlidingToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        token = self.get_token(self.user)

        data["token"] = str(token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    default_error_messages = {
        "no_active_account": _("No active account found for the given token.")
    }

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = self._get_refresh_token(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id and (
            user := get_user_model().objects.get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        ):
            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

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
            refresh.outstand()

            data["refresh"] = str(refresh)

        return data

    def _get_refresh_token(self, token_str: str) -> RefreshToken:
        """
        Handles refresh token instantiation and family blacklisting if enabled.
        """
        try:
            return self.token_class(token_str)
        except RefreshTokenBlacklistedError as e:
            if (
                api_settings.TOKEN_FAMILY_ENABLED
                and api_settings.TOKEN_FAMILY_BLACKLIST_ON_REUSE
                and "rest_framework_simplejwt.token_family" in settings.INSTALLED_APPS
            ):
                refresh = self.token_class(token=token_str, verify=False)
                family_id = refresh.get_family_id()

                if family_id:
                    refresh.blacklist_family()

            raise e


class TokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()
    token_class = SlidingToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        token = self.token_class(attrs["token"])

        # Check that the timestamp in the "refresh_exp" claim has not
        # passed
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)

        # Update the "exp" and "iat" claims
        token.set_exp()
        token.set_iat()

        return {"token": str(token)}


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, None]) -> dict[Any, Any]:
        token = UntypedToken(attrs["token"])

        if (
            token.get(api_settings.TOKEN_TYPE_CLAIM) == RefreshToken.token_type
            and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti = token.get(api_settings.JTI_CLAIM)
            if (
                blacklist_cache.is_refresh_tokens_cache_enabled
                and blacklist_cache.is_refresh_token_blacklisted(jti)
            ):
                raise ValidationError(_("Token is blacklisted"))

            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise ValidationError(_("Token is blacklisted"))

        if (
            api_settings.TOKEN_FAMILY_ENABLED
            and "rest_framework_simplejwt.token_family" in settings.INSTALLED_APPS
        ):
            FamilyMixin.check_family_expiration(token=token)
            FamilyMixin.check_family_blacklist(token=token)

        return {}


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return {}


class TokenFamilyBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist_family()
        except AttributeError:
            raise TokenFamilyNotConfigured()
        except TokenError as e:
            raise serializers.ValidationError({"refresh": str(e)})

        return {"message": "Token Family blacklisted"}
