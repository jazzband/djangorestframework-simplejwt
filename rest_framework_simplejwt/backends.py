from __future__ import unicode_literals

import jwt
from django.utils.translation import ugettext_lazy as _
from jwt import InvalidTokenError

from .exceptions import TokenBackendError
from .settings import api_settings
from .utils import format_lazy

ALLOWED_ALGORITHMS = (
    'HS256',
    'HS384',
    'HS512',
    'RS256',
    'RS384',
    'RS512',
)


class TokenBackend(object):
    def __init__(self, algorithm, signing_key=None, verifying_key=None, secret_key=None, get_user_secret_key=None):
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(format_lazy(_("Unrecognized algorithm type '{}'"), algorithm))

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        self.secret_key = secret_key
        self.get_user_secret_key = get_user_secret_key

    def get_secret_key(self, payload):
        if self.get_user_secret_key:
            return self.get_user_secret_key(payload[api_settings.USER_ID_FIELD])
        return self.secret_key

    def get_signing_key(self, payload):
        return self.signing_key or self.get_secret_key(payload)

    def get_verifying_key(self, payload):
        return self.verifying_key or self.get_secret_key(payload)

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        signing_key = self.get_signing_key(payload)
        token = jwt.encode(payload, signing_key, algorithm=self.algorithm)
        return token.decode('utf-8')

    def decode(self, token, verify=True):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            unverified_payload = jwt.decode(token, None, False)
            verifying_key = self.get_verifying_key(unverified_payload)
            return jwt.decode(token, verifying_key, algorithms=[self.algorithm], verify=verify)
        except InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))
