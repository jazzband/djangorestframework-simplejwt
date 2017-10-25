from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from jwt import InvalidTokenError
import jwt

from .exceptions import TokenBackendError
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
    def __init__(self, algorithm, signing_key=None, verifying_key=None):
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(format_lazy(_("Unrecognized algorithm type '{}'"), algorithm))

        self.algorithm = algorithm
        self.signing_key = signing_key
        if algorithm.startswith('HS'):
            self.verifying_key = signing_key
        else:
            self.verifying_key = verifying_key

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        token = jwt.encode(payload, self.signing_key, algorithm=self.algorithm)
        return token.decode('utf-8')

    def decode(self, token, verify=True):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return jwt.decode(token, self.verifying_key, algorithms=[self.algorithm], verify=verify)
        except InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))
