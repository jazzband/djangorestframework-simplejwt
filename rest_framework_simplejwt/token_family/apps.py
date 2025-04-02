from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TokenFamilyConfig(AppConfig):
    name = "rest_framework_simplejwt.token_family"
    verbose_name = _("Token Family")
    default_auto_field = "django.db.models.BigAutoField"