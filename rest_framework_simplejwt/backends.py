import jwt
from django.utils.translation import ugettext_lazy as _
from jwt import InvalidTokenError

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


class TokenBackend:
    def __init__(self, algorithm, signing_key=None, verifying_key=None, audience=None, issuer=None):
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(format_lazy(_("Unrecognized algorithm type '{}'"), algorithm))

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.audience = audience
        self.issuer = issuer
        self.verifying_key = self.get_verifying_key(signing_key, verifying_key)

    def encode(self, payload, signing_key=None):
        """
        Returns an encoded token for the given payload dictionary.
        """
        jwt_payload = payload.copy()
        if self.audience is not None:
            jwt_payload['aud'] = self.audience
        if self.issuer is not None:
            jwt_payload['iss'] = self.issuer

        signing_key = signing_key or self.signing_key

        token = jwt.encode(jwt_payload, signing_key, algorithm=self.algorithm)
        return token.decode('utf-8')

    def decode(self, token, verify=True, signing_key=None):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        verifying_key = self.get_verifying_key(
            signing_key, self.verifying_key) if signing_key else self.verifying_key

        try:
            return jwt.decode(token, verifying_key, algorithms=[self.algorithm], verify=verify,
                              audience=self.audience, issuer=self.issuer,
                              options={'verify_aud': self.audience is not None})
        except InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))

    def get_verifying_key(self, signing_key, verifying_key):
        """Return verifying key depending on the algorithm."""
        if self.algorithm.startswith('HS'):
            verifying_key = signing_key or self.signing_key
        else:
            verifying_key = verifying_key
        return verifying_key
