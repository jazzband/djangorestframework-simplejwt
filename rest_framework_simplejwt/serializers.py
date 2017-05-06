from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import authenticate, get_user_model
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from rest_framework import serializers

USER_ID_FIELD = 'pk'
PAYLOAD_ID_FIELD = 'user_pk'
TOKEN_LIFETIME = timedelta(seconds=300)

SECRET_KEY = 'blah'

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
        user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        if not user:
            raise serializers.ValidationError(
                _('No account found with the given credentials.'),
            )

        if not user.is_active:
            raise serializers.ValidationError(
                _('User is inactive.'),
            )

        payload = self.get_payload(user)

        return {'token': self.get_token(payload)}

    def get_payload(self, user):
        """
        Serializes the given user into a payload object.
        """
        payload = {
            PAYLOAD_ID_FIELD: text_type(getattr(user, USER_ID_FIELD)),
            'exp': datetime.utcnow() + TOKEN_LIFETIME
        }

        return payload

    def get_token(self, payload):
        """
        Converts the given payload object into a JSON web token.
        """
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
