from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

AUTH_HEADER_TYPE = 'Bearer'
AUTH_HEADER_TYPE_BYTES = AUTH_HEADER_TYPE.encode('utf-8')

USER_ID_FIELD = 'pk'
PAYLOAD_ID_FIELD = 'user_pk'
SECRET_KEY = 'blah'

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        header = self.get_header(request)
        token = self.get_token(header)
        payload = self.get_payload(token)
        user_id = self.get_user_id(payload)

        return (self.get_user(user_id), None)

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPE,
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        return get_authorization_header(request)

    def get_token(self, header):
        parts = header.split()

        if not parts or parts[0] != AUTH_HEADER_TYPE_BYTES:
            return None

        if len(parts) == 1:
            raise AuthenticationFailed(_('No token provided.'))
        elif len(parts) > 2:
            raise AuthenticationFailed(_('Token should not contain spaces.'))

        return parts[1]

    def get_payload(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except TypeError:
            raise AuthenticationFailed(_('Token was invalid.'))

    def get_user_id(self, payload):
        try:
            return payload[PAYLOAD_ID_FIELD]
        except KeyError:
            raise AuthenticationFailed(_('Token contained no user identification.'))

    def get_user(self, user_id):
        try:
            user = User.objects.get(**{USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive.'))

        return user
