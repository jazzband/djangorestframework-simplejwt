from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'SIMPLE_JWT', None)

DEFAULTS = {
    'AUTH_HEADER_TYPE': 'Bearer',

    'USER_ID_FIELD': 'pk',
    'PAYLOAD_ID_FIELD': 'user_pk',

    'TOKEN_LIFETIME': timedelta(days=7),

    'TOKEN_BACKEND': 'rest_framework_simplejwt.backends.TokenBackend',

    'SECRET_KEY': settings.SECRET_KEY,
}

IMPORT_STRING_SETTINGS = (
    'TOKEN_BACKEND',
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRING_SETTINGS)
