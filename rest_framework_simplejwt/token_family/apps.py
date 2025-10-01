from datetime import timedelta

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.settings import api_settings


class TokenFamilyConfig(AppConfig):
    name = "rest_framework_simplejwt.token_family"
    verbose_name = _("Token Family")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Validate token family settings at startup."""
        try:
            self._validate_family_settings()
        except (ImproperlyConfigured, ImportError) as e:
            raise ImproperlyConfigured(f"Invalid Token Family settings: {e}") from e

    @staticmethod
    def _validate_family_settings() -> None:
        """
        Ensures that required token family settings are properly configured.
        This way we prevent undesired behavior.
        """
        family_claim = api_settings.TOKEN_FAMILY_CLAIM
        if not isinstance(family_claim, str) or not family_claim.strip():
            raise ImproperlyConfigured("TOKEN_FAMILY_CLAIM must be a non-empty string")

        family_exp_claim = api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM
        if not isinstance(family_exp_claim, str) or not family_exp_claim.strip():
            raise ImproperlyConfigured(
                "TOKEN_FAMILY_EXPIRATION_CLAIM must be a non-empty string"
            )

        family_lifetime = api_settings.TOKEN_FAMILY_LIFETIME
        if family_lifetime is not None and not isinstance(family_lifetime, timedelta):
            raise ImproperlyConfigured(
                "TOKEN_FAMILY_LIFETIME must be of type timedelta or None"
            )

        family_enabled = api_settings.TOKEN_FAMILY_ENABLED
        if not isinstance(family_enabled, bool):
            raise ImproperlyConfigured("TOKEN_FAMILY_ENABLED must be of type bool")

        check_on_access = api_settings.TOKEN_FAMILY_CHECK_ON_ACCESS
        if not isinstance(check_on_access, bool):
            raise ImproperlyConfigured(
                "TOKEN_FAMILY_CHECK_ON_ACCESS must be of type bool"
            )

        blacklist_on_reuse = api_settings.TOKEN_FAMILY_BLACKLIST_ON_REUSE
        if not isinstance(blacklist_on_reuse, bool):
            raise ImproperlyConfigured(
                "TOKEN_FAMILY_BLACKLIST_ON_REUSE must be of type bool"
            )

        # Validate TOKEN_FAMILY_BLACKLIST_SERIALIZER
        blacklist_serializer_path = api_settings.TOKEN_FAMILY_BLACKLIST_SERIALIZER
        if (
            not isinstance(blacklist_serializer_path, str)
            or not blacklist_serializer_path.strip()
        ):
            raise ImproperlyConfigured(
                "TOKEN_FAMILY_BLACKLIST_SERIALIZER must be a non-empty string"
            )

        try:
            import_string(blacklist_serializer_path)
        except ImportError as e:
            raise ImportError(
                f"Could not import serializer '{blacklist_serializer_path}': {e}"
            ) from e
