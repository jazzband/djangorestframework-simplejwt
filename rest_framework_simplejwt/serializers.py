from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import authenticate
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .exceptions import TokenError
from .state import User, Token


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

        token = Token.for_user(user)

        return {'token': text_type(token)}


class TokenRefreshSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        now = datetime.utcnow()

        try:
            token = Token(attrs['token'])
            # Check that the timestamp in the 'refresh_exp' claim has not
            # passed
            token.check_expiration('refresh_exp', current_time=now)
        except TokenError as e:
            raise serializers.ValidationError(e.args[0])

        # Update the 'exp' claim for this token
        token.update_expiration(from_time=now)

        return {'token': text_type(token)}
