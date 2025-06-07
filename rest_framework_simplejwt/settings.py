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
    "TOKEN_FAMILY_ENABLED": False,
    "TOKEN_FAMILY_LIFETIME": timedelta(days=30),
    "TOKEN_FAMILY_CHECK_ON_ACCESS": False,
    "TOKEN_FAMILY_BLACKLIST_ON_REUSE": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "SJWT_CACHE_NAME": "default",
    "CACHE_BLACKLISTED_REFRESH_TOKENS": False,
    "CACHE_BLACKLISTED_FAMILIES": False,
    "CACHE_TTL_BLACKLISTED_REFRESH_TOKENS": 3600,  # time is seconds
    "CACHE_TTL_BLACKLISTED_FAMILIES": 3600,  # time in seconds
    "CACHE_KEY_PREFIX_BLACKLISTED_REFRESH_TOKENS": "sjwt_brt",
    "CACHE_KEY_PREFIX_BLACKLISTED_FAMILIES": "sjwt_btf",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "TOKEN_FAMILY_CLAIM": "family_id",
    "TOKEN_FAMILY_EXPIRATION_CLAIM": "family_exp",
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
    "TOKEN_FAMILY_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenFamilyBlacklistSerializer",
    "CHECK_REVOKE_TOKEN": False,
    "REVOKE_TOKEN_CLAIM": "hash_password",
    "CHECK_USER_IS_ACTIVE": True,
}

IMPORT_STRINGS = (
    "AUTH_TOKEN_CLASSES",
    "JSON_ENCODER",
    "TOKEN_USER_CLASS",
    "USER_AUTHENTICATION_RULE",
)

REMOVED_SETTINGS = (
    "AUTH_HEADER_TYPE",
    "AUTH_TOKEN_CLASS",
    "SECRET_KEY",
    "TOKEN_BACKEND_CLASS",
)


class APISettings(_APISettings):  # pragma: no cover
    def __check_user_settings(self, user_settings: dict[str, Any]) -> dict[str, Any]:
        SETTINGS_DOC = "https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html"

        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    format_lazy(
                        _(
                            "The '{}' setting has been removed. Please refer to '{}' for available settings."
                        ),
                        setting,
                        SETTINGS_DOC,
                    )
                )

        return user_settings


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs) -> None:  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "SIMPLE_JWT":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
