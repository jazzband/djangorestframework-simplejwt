import jwt
from django.utils.translation import gettext_lazy as _
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
    def __init__(self, algorithm, signing_key=None, verifying_key=None, audience=None, issuer=None, key_id=None):
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(format_lazy(_("Unrecognized algorithm type '{}'"), algorithm))

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.audience = audience
        self.issuer = issuer
        self.key_id = None
        if algorithm.startswith('HS'):
            self.verifying_key = signing_key
        else:
            self.verifying_key = verifying_key
            # key_id should be used only with asymmetric encryption keys
            self.key_id = key_id

    def encode(self, payload):
        """
        Returns an encoded token for the given payload dictionary.
        """
        jwt_payload = payload.copy()
        if self.audience is not None and jwt_payload.get('aud') is None:
            jwt_payload['aud'] = self.audience
        if self.issuer is not None and jwt_payload.get('iss') is None:
            jwt_payload['iss'] = self.issuer

        jwt_headers = {}
        if self.key_id is not None:
            jwt_headers['kid'] = str(self.key_id(self.verifying_key))

        token = jwt.encode(jwt_payload, self.signing_key, algorithm=self.algorithm, headers=jwt_headers)
        return token.decode('utf-8')

    def decode(self, token, verify=True):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return jwt.decode(token, self.verifying_key, algorithms=[self.algorithm], verify=verify,
                              audience=self.audience, issuer=self.issuer,
                              options={'verify_aud': self.audience is not None})
        except InvalidTokenError:
            raise TokenBackendError(_('Token is invalid or expired'))
