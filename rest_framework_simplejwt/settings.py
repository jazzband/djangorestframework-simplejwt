from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'SIMPLE_JWT', None)

DEFAULTS = {
    'AUTH_HEADER_TYPE': 'Bearer',

    'USER_ID_FIELD': 'id',
    'PAYLOAD_ID_FIELD': 'user_id',

    'TOKEN_LIFETIME': timedelta(days=1),
    'TOKEN_REFRESH_LIFETIME': timedelta(days=7),

    'SECRET_KEY': settings.SECRET_KEY,

    'TOKEN_CLASS': 'rest_framework_simplejwt.tokens.Token',
}

IMPORT_STRING_SETTINGS = (
    'TOKEN_CLASS',
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRING_SETTINGS)
