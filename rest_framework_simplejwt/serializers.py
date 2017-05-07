from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from rest_framework import serializers

from .settings import api_settings

User = get_user_model()


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
        # The default authentication backend will also return None when a user
        # is inactive
        user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        if user is None:
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
