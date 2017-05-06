from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework.exceptions import AuthenticationFailed

from .settings import api_settings

AUTH_HEADER_TYPE_BYTES = api_settings.AUTH_HEADER_TYPE.encode('utf-8')

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        token = self.get_token(header)
        if token is None:
            return None

        payload = self.get_payload(token)
        user_id = self.get_user_id(payload)

        return (self.get_user(user_id), None)

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            api_settings.AUTH_HEADER_TYPE,
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts a header containing a JSON web token from the given request.
        """
        header = request.META.get('HTTP_AUTHORIZATION')

        if isinstance(header, text_type):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_token(self, header):
        """
        Extracts a JSON web token from the given header.
        """
        parts = header.split()

        if parts[0] != AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values.'),
            )

        return parts[1]

    def get_payload(self, token):
        """
        Extracts a data payload from the given JSON web token.
        """
        try:
            return jwt.decode(token, api_settings.SECRET_KEY, algorithms=['HS256'])
        except TypeError:
            raise AuthenticationFailed(_('Token is invalid.'))

    def get_user_id(self, payload):
        """
        Extracts a recognizable user identifier from the given data payload
        object.
        """
        try:
            return payload[api_settings.PAYLOAD_ID_FIELD]
        except KeyError:
            raise AuthenticationFailed(_('Token contained no recognizable user identification.'))

    def get_user(self, user_id):
        """
        Attempts to find and return a user record with the given user
        identifier.
        """
        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive.'))

        return user
