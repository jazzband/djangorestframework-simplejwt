from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from rest_framework.settings import APISettings

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

IMPORT_STRING_SETTINGS = (
    'AUTH_TOKEN_CLASS',
    'TOKEN_BACKEND_CLASS',
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRING_SETTINGS)
