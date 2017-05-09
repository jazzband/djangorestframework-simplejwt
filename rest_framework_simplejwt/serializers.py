from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import authenticate
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from rest_framework import serializers

from .settings import api_settings
from .state import User


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super(PasswordField, self).__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super(TokenObtainSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        # Prior to Django 1.10, inactive users could be authenticated with the
        # default `ModelBackend`.  As of Django 1.10, the default
        # `ModelBackend` prevents inactive users from authenticating.  App
        # designers can still allow inactive users to authenticate by opting
        # for the new `AllowAllUsersModelBackend`.  However, we explicitly
        # prevent inactive users from authenticating to enforce a reasonable
        # policy and provide sensible backwards compatibility with older Django
        # versions.
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                _('No active account found with the given credentials.'),
            )

        payload = self.get_payload(user)

        return {'token': self.get_token(payload)}

    def get_payload(self, user):
        """
        Serializes the given user into a payload object.
        """
        payload = {
            api_settings.PAYLOAD_ID_FIELD: text_type(getattr(user, api_settings.USER_ID_FIELD)),
            'exp': datetime.utcnow() + api_settings.TOKEN_LIFETIME
        }

        return payload

    def get_token(self, payload):
        """
        Converts the given payload object into a JSON web token.
        """
        return jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
