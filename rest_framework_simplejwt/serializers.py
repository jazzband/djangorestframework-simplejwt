from typing import Any, Optional, TypeVar

from django.conf import settings
from django.contrib.auth import _clean_credentials, authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.request import Request

from .models import TokenUser
from .settings import api_settings
from .tokens import RefreshToken, SlidingToken, Token, UntypedToken
from .utils import get_md5_hash_password

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)

if api_settings.BLACKLIST_AFTER_ROTATION:
    from .token_blacklist.models import BlacklistedToken


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
            api_settings.ON_LOGIN_FAILED(
                _clean_credentials(attrs), self.context.get("request")
            )
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
            api_settings.ON_LOGIN_SUCCESS(self.user, self.context.get("request"))

        return data


class TokenObtainSlidingSerializer(TokenObtainSerializer):
    token_class = SlidingToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        token = self.get_token(self.user)

        data["token"] = str(token)

        if api_settings.UPDATE_LAST_LOGIN:
            api_settings.ON_LOGIN_SUCCESS(self.user, self.context.get("request"))

        return data


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    default_error_messages = {
        "no_active_account": _("No active account found for the given token."),
        "password_changed": _("The user's password has been changed."),
    }

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id:
            try:
                user = get_user_model().objects.get(
                    **{api_settings.USER_ID_FIELD: user_id}
                )
            except get_user_model().DoesNotExist:
                # This handles the case where the user has been deleted.
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"], "no_active_account"
                )

            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"], "no_active_account"
                )

            if api_settings.CHECK_REVOKE_TOKEN:
                if refresh.payload.get(
                    api_settings.REVOKE_TOKEN_CLAIM
                ) != get_md5_hash_password(user.password):
                    # If the password has changed, we blacklist the token
                    # to prevent any further use.
                    if (
                        "rest_framework_simplejwt.token_blacklist"
                        in settings.INSTALLED_APPS
                    ):
                        try:
                            refresh.blacklist()
                        except AttributeError:
                            pass

                    raise AuthenticationFailed(
                        self.error_messages["password_changed"],
                        code="password_changed",
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


class TokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()
    token_class = SlidingToken

    default_error_messages = {
        "no_active_account": _("No active account found for the given token."),
        "password_changed": _("The user's password has been changed."),
    }

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        token = self.token_class(attrs["token"])
        user_id = token.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id:
            try:
                user = get_user_model().objects.get(
                    **{api_settings.USER_ID_FIELD: user_id}
                )
            except get_user_model().DoesNotExist:
                # This handles the case where the user has been deleted.
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"], "no_active_account"
                )

            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"], "no_active_account"
                )

            if api_settings.CHECK_REVOKE_TOKEN:
                if token.payload.get(
                    api_settings.REVOKE_TOKEN_CLAIM
                ) != get_md5_hash_password(user.password):
                    # If the password has changed, we blacklist the token
                    # to prevent any further use.
                    if (
                        "rest_framework_simplejwt.token_blacklist"
                        in settings.INSTALLED_APPS
                    ):
                        try:
                            token.blacklist()
                        except AttributeError:
                            pass

                    raise AuthenticationFailed(
                        self.error_messages["password_changed"],
                        code="password_changed",
                    )

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
            api_settings.BLACKLIST_AFTER_ROTATION
            and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise ValidationError(_("Token is blacklisted"))

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


def default_on_login_success(user: AuthUser, request: Optional[Request]) -> None:
    update_last_login(None, user)


def default_on_login_failed(credentials: dict, request: Optional[Request]) -> None:
    pass
