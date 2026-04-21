from datetime import timedelta
from typing import Any

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.translation import gettext_lazy as _
from rest_framework.settings import APISettings as _APISettings

from .utils import format_lazy

USER_SETTINGS = getattr(settings, "SIMPLE_JWT", None)

DEFAULTS = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "AUDIENCE_VALIDATION": "static",
    "ISSUER": None,
    "ISSUER_CLAIM": "iss",
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "ON_LOGIN_SUCCESS": "rest_framework_simplejwt.serializers.default_on_login_success",
    "ON_LOGIN_FAILED": "rest_framework_simplejwt.serializers.default_on_login_failed",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
    "CHECK_REVOKE_TOKEN": False,
    "REVOKE_TOKEN_CLAIM": "hash_password",
    "CHECK_USER_IS_ACTIVE": True,
}

IMPORT_STRINGS = (
    "AUTH_TOKEN_CLASSES",
    "JSON_ENCODER",
    "TOKEN_USER_CLASS",
    "USER_AUTHENTICATION_RULE",
    "ON_LOGIN_SUCCESS",
    "ON_LOGIN_FAILED",
)

REMOVED_SETTINGS = (
    "AUTH_HEADER_TYPE",
    "AUTH_TOKEN_CLASS",
    "SECRET_KEY",
    "TOKEN_BACKEND_CLASS",
)

AUDIENCE_VALIDATION_MODES = ("static", "dynamic")


class APISettings(_APISettings):  # pragma: no cover
    def _raise_invalid_setting(
        self, message: str, settings_doc: str, *args: Any
    ) -> None:
        raise RuntimeError(
            format_lazy(
                _(message),
                *args,
                settings_doc,
            )
        )

    def _validate_removed_settings(
        self, user_settings: dict[str, Any], settings_doc: str
    ) -> None:
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                self._raise_invalid_setting(
                    "The '{}' setting has been removed. Please refer to '{}' for available settings.",
                    settings_doc,
                    setting,
                )

    def _validate_validation_modes(
        self, user_settings: dict[str, Any], settings_doc: str
    ) -> None:
        audience_validation = user_settings.get("AUDIENCE_VALIDATION")
        if (
            audience_validation is not None
            and audience_validation not in AUDIENCE_VALIDATION_MODES
        ):
            self._raise_invalid_setting(
                "The '{}' setting must be one of {}. Please refer to '{}' for available settings.",
                settings_doc,
                "AUDIENCE_VALIDATION",
                AUDIENCE_VALIDATION_MODES,
            )

    def _validate_issuer_settings(
        self, user_settings: dict[str, Any], settings_doc: str
    ) -> None:
        issuer = user_settings.get("ISSUER")

        if issuer is None:
            return

        if isinstance(issuer, str):
            if issuer.strip():
                return

            self._raise_invalid_setting(
                "The 'ISSUER' setting must be a non-empty string or a list/tuple of non-empty strings. Please refer to '{}' for available settings.",
                settings_doc,
            )

        if not isinstance(issuer, (list, tuple)) or not issuer or any(
            not isinstance(item, str) or not item.strip() for item in issuer
        ):
            self._raise_invalid_setting(
                "The 'ISSUER' setting must be a non-empty string or a list/tuple of non-empty strings. Please refer to '{}' for available settings.",
                settings_doc,
            )

    def __check_user_settings(self, user_settings: dict[str, Any]) -> dict[str, Any]:
        settings_doc = "https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html"

        self._validate_removed_settings(user_settings, settings_doc)
        self._validate_validation_modes(user_settings, settings_doc)
        self._validate_issuer_settings(user_settings, settings_doc)

        return user_settings


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs) -> None:  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "SIMPLE_JWT":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
