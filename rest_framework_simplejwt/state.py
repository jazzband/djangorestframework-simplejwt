from django.contrib.auth import get_user_model

from rest_framework_simplejwt.settings import api_settings

User = get_user_model()
Token = api_settings.TOKEN_CLASS
token_backend = api_settings.TOKEN_BACKEND_CLASS(api_settings.SECRET_KEY, api_settings.ALGORITHM)
