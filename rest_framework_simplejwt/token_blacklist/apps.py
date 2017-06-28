from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TokenBlacklistConfig(AppConfig):
    name = 'rest_framework_simplejwt.token_blacklist'
    verbose_name = _('Token Blacklist')
