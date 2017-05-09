from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .exceptions import TokenBackendError
from .settings import api_settings
from .state import User, token_backend
from .utils import datetime_to_epoch


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
        # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
        # prevents inactive users from authenticating.  App designers can still
        # allow inactive users to authenticate by opting for the new
        # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
        # users from authenticating to enforce a reasonable policy and provide
        # sensible backwards compatibility with older Django versions.
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                _('No active account found with the given credentials.'),
            )

        payload = token_backend.get_payload_for_user(user)

        return {'token': token_backend.encode(payload)}


class TokenRefreshSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            payload = token_backend.decode(attrs['token'])
        except TokenBackendError as e:
            raise serializers.ValidationError(e.args[0])

        # Ensure this token has a refresh expiration claim
        if 'refresh_exp' not in payload:
            raise serializers.ValidationError(_('Token has no refresh expiration claim.'))

        now = datetime.utcnow()

        # Get the refresh expiration timestamp and check if the refresh period
        # for this token has expired
        refresh_exp = datetime.utcfromtimestamp(payload['refresh_exp'])
        if refresh_exp < now:
            raise serializers.ValidationError(_('Token refresh period has expired.'))

        # Update the expiration timestamp for this token
        exp = now + api_settings.TOKEN_LIFETIME
        payload.update({'exp': datetime_to_epoch(exp)})

        return {'token': token_backend.encode(payload)}
