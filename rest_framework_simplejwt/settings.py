from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.translation import ugettext_lazy as _
from rest_framework.settings import APISettings as _APISettings

from .utils import format_lazy

USER_SETTINGS = getattr(settings, 'SIMPLE_JWT', None)

DEFAULTS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    'SECRET_KEY': settings.SECRET_KEY,

    'AUTH_HEADER_TYPE': 'Bearer',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASS': 'rest_framework_simplejwt.tokens.AccessToken',
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # Undocumented settings.  Changing these may lead to unexpected behavior.
    # Make sure you know what you're doing.  These might become part of the
    # public API eventually but that would require some adjustments and better
    # documentation.
    'TOKEN_BACKEND_CLASS': 'rest_framework_simplejwt.backends.PyJWTBackend',
    'ALGORITHM': 'HS256',
}

IMPORT_STRINGS = (
    'AUTH_TOKEN_CLASS',
    'TOKEN_BACKEND_CLASS',
)

REMOVED_SETTINGS = tuple()


class APISettings(_APISettings):
    def __check_user_settings(self, user_settings):
        SETTINGS_DOC = 'https://github.com/davesque/django-rest-framework-simplejwt#settings'

        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(format_lazy(
                    _("The '{}' setting has been removed. Please refer to '{}' for available settings."),
                    setting, SETTINGS_DOC,
                ))

        return user_settings

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    global api_settings

    setting, value = kwargs['setting'], kwargs['value']

    if setting == 'SIMPLE_JWT':
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)

setting_changed.connect(reload_api_settings)
