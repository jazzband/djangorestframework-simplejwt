from django.contrib.auth import get_user_model

from rest_framework_simplejwt.settings import api_settings

User = get_user_model()
Token = api_settings.TOKEN_CLASS
