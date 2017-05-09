from django.contrib.auth import get_user_model

from .settings import api_settings

User = get_user_model()

token_backend = api_settings.TOKEN_BACKEND()
