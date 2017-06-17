from __future__ import unicode_literals

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework.exceptions import AuthenticationFailed

from .exceptions import TokenBackendError
from .models import TokenUser
from .settings import api_settings
from .state import User, token_backend

AUTH_HEADER_TYPE_BYTES = api_settings.AUTH_HEADER_TYPE.encode(HTTP_HEADER_ENCODING)


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

        return (self.get_user(payload), None)

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            api_settings.AUTH_HEADER_TYPE,
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
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
        Validates a JSON web token and extracts a data payload from it.
        """
        try:
            return token_backend.decode(token)
        except TokenBackendError as e:
            raise AuthenticationFailed(e.args[0])

    def get_user(self, payload):
        """
        Attempts to find and return a user using the given token payload.
        """
        try:
            user_id = payload[api_settings.PAYLOAD_ID_FIELD]
        except KeyError:
            raise AuthenticationFailed(_('Token contained no recognizable user identification.'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive.'))

        return user


class JWTTokenUserAuthentication(JWTAuthentication):
    def get_user(self, payload):
        """
        Returns a user for the given token payload.
        """
        if api_settings.PAYLOAD_ID_FIELD not in payload:
            # The TokenUser class assumes token payloads will have a
            # recognizable user identifier claim.
            raise AuthenticationFailed(_('Token contained no recognizable user identification.'))

        return TokenUser(payload)
