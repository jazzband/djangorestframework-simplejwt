from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .exceptions import TokenBackendError
from .utils import format_lazy

ALLOWED_ALGORITHMS = (
    'HS256',
)


class TokenBackend(object):
    def __init__(self, secret, algorithm):
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(format_lazy(_("Unrecognized algorithm type '{}'"), algorithm))

        self.secret = secret
        self.algorithm = algorithm

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        raise NotImplementedError  # pragma: no cover

    def decode(self, token):
        """
        Performs a low-level validation of the given base64 encoded token and
        returns its payload dictionary.

        Raises a `TokenBackendError` if the token is malformed or if its
        signature check fails.
        """
        raise NotImplementedError  # pragma: no cover


class PythonJOSEBackend(TokenBackend):
    def __init__(self, *args, **kwargs):
        super(PythonJOSEBackend, self).__init__(*args, **kwargs)

        from jose import jwt
        from jose.exceptions import JOSEError

        self.jwt = jwt
        self.JOSEError = JOSEError

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        return self.jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token):
        """
        Performs a low-level validation of the given token and returns its
        payload dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return self.jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except self.JOSEError:
            raise TokenBackendError(_('Token is invalid or expired'))


class PyJWTBackend(TokenBackend):
    def __init__(self, *args, **kwargs):
        super(PyJWTBackend, self).__init__(*args, **kwargs)

        import jwt

        self.jwt = jwt
        self.InvalidTokenError = jwt.InvalidTokenError

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        return self.jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token):
        """
        Performs a low-level validation of the given token and returns its
        payload dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return self.jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except self.InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))
