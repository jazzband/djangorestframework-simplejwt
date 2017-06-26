from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.settings import api_settings

User = get_user_model()
AuthToken = api_settings.AUTH_TOKEN_CLASS
token_backend = api_settings.TOKEN_BACKEND_CLASS(api_settings.SECRET_KEY, api_settings.ALGORITHM)
