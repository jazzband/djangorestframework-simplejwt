from datetime import datetime

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from jose import jwt
from jose.exceptions import JOSEError

from .exceptions import TokenBackendError
from .settings import api_settings
from .utils import datetime_to_epoch


class TokenBackend(object):
    def get_payload_for_user(self, user):
        """
        Returns the payload dictionary for a given user that will be used to
        create a JSON web token after authenticating the user's credentials.
        """
        now = datetime.utcnow()

        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = text_type(user_id)

        exp = now + api_settings.TOKEN_LIFETIME
        refresh_exp = now + api_settings.TOKEN_REFRESH_LIFETIME

        return {
            api_settings.PAYLOAD_ID_FIELD: user_id,
            'exp': datetime_to_epoch(exp),
            'refresh_exp': datetime_to_epoch(refresh_exp),
        }

    def encode(self, payload):
        """
        Returns a JSON web token for the given payload dictionary.
        """
        return jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

    def decode(self, token):
        """
        Verifies the given JSON web token and returns its payload dictionary.
        Must raise a TokenBackendError with a user-facing error message if
        verification fails.
        """
        try:
            payload = jwt.decode(token, api_settings.SECRET_KEY, algorithms=['HS256'])
        except JOSEError:
            raise TokenBackendError(_('Token is invalid or expired.'))

        # According to RFC 7519, the 'exp' claim is OPTIONAL:
        # https://tools.ietf.org/html/rfc7519#section-4.1.4

        # As a more sensible default behavior for tokens used in an
        # authorization context, we require expiry
        if 'exp' not in payload:
            raise TokenBackendError(_('Token has no expiration.'))

        return payload
