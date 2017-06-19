from datetime import datetime

from django.utils.six import text_type, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from jose.exceptions import JOSEError

from .exceptions import TokenError
from .settings import api_settings
from .utils import datetime_to_epoch


@python_2_unicode_compatible
class Token(object):
    def __init__(self, token=None):
        self.token = token

        if token is not None:
            self.payload = self.decode(token)
        else:
            self.payload = {}

    def __str__(self):
        return self.encode(self.payload)

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, name):
        return self.payload[name]

    def __setitem__(self, name, value):
        self.payload[name] = value

    def __contains__(self, name):
        return name in self.payload

    def update_expiration(self, from_time=None, lifetime=None, claim='exp'):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = datetime.utcnow()

        if lifetime is None:
            lifetime = api_settings.TOKEN_LIFETIME

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    @classmethod
    def encode(cls, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        return jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

    @classmethod
    def decode(cls, token):
        """
        Validates and decodes the given token and returns its payload
        dictionary.  Must raise a TokenError with a user-facing error message
        if validation fails.
        """
        try:
            payload = jwt.decode(token, api_settings.SECRET_KEY, algorithms=['HS256'])
        except JOSEError:
            raise TokenError(_('Token is invalid or expired.'))

        # According to RFC 7519, the 'exp' claim is OPTIONAL:
        # https://tools.ietf.org/html/rfc7519#section-4.1.4

        # As a more sensible default behavior for tokens used in an
        # authorization context, we require expiry
        if 'exp' not in payload:
            raise TokenError(_('Token has no expiration.'))

        return payload

    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = text_type(user_id)

        token = cls()

        token[api_settings.PAYLOAD_ID_FIELD] = user_id

        now = datetime.utcnow()
        token.update_expiration()
        token.update_expiration(
            from_time=now,
            lifetime=api_settings.TOKEN_REFRESH_LIFETIME,
            claim='refresh_exp',
        )

        return token
