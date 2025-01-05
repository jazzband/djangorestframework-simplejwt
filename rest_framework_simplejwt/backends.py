import json
from collections.abc import Iterable
from datetime import timedelta
from typing import Any, Dict, Optional, Type, Union

import jwt
from django.utils.translation import gettext_lazy as _
from jwt import InvalidAlgorithmError, InvalidTokenError, algorithms

from .exceptions import TokenBackendError
from .tokens import Token
from .utils import format_lazy

try:
    from jwt import PyJWKClient, PyJWKClientError

    JWK_CLIENT_AVAILABLE = True
except ImportError:
    JWK_CLIENT_AVAILABLE = False

ALLOWED_ALGORITHMS = {
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
}.union(algorithms.requires_cryptography)


class TokenBackend:
    def __init__(
        self,
        algorithm: str,
        signing_key: Optional[str] = None,
        verifying_key: str = "",
        audience: Union[str, Iterable, None] = None,
        issuer: Optional[str] = None,
        jwk_url: Optional[str] = None,
        leeway: Union[float, int, timedelta, None] = None,
        json_encoder: Optional[Type[json.JSONEncoder]] = None,
    ) -> None:
        self._validate_algorithm(algorithm)

        self.algorithm = algorithm
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        self.audience = audience
        self.issuer = issuer

        if JWK_CLIENT_AVAILABLE:
            self.jwks_client = PyJWKClient(jwk_url) if jwk_url else None
        else:
            self.jwks_client = None

        self.leeway = leeway
        self.json_encoder = json_encoder

    def _validate_algorithm(self, algorithm: str) -> None:
        """
        Ensure that the nominated algorithm is recognized, and that cryptography is installed for those
        algorithms that require it
        """
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(
                format_lazy(_("Unrecognized algorithm type '{}'"), algorithm)
            )

        if algorithm in algorithms.requires_cryptography and not algorithms.has_crypto:
            raise TokenBackendError(
                format_lazy(
                    _("You must have cryptography installed to use {}."), algorithm
                )
            )

    def get_leeway(self) -> timedelta:
        if self.leeway is None:
            return timedelta(seconds=0)
        elif isinstance(self.leeway, (int, float)):
            return timedelta(seconds=self.leeway)
        elif isinstance(self.leeway, timedelta):
            return self.leeway
        else:
            raise TokenBackendError(
                format_lazy(
                    _(
                        "Unrecognized type '{}', 'leeway' must be of type int, float or timedelta."
                    ),
                    type(self.leeway),
                )
            )

    def get_verifying_key(self, token: Token) -> Optional[str]:
        if self.algorithm.startswith("HS"):
            return self.signing_key

        if self.jwks_client:
            try:
                return self.jwks_client.get_signing_key_from_jwt(token).key
            except PyJWKClientError as ex:
                raise TokenBackendError(_("Token is invalid or expired")) from ex

        return self.verifying_key

    def encode(self, payload: Dict[str, Any]) -> str:
        """
        Returns an encoded token for the given payload dictionary.
        """
        jwt_payload = payload.copy()
        if self.audience is not None:
            jwt_payload["aud"] = self.audience
        if self.issuer is not None:
            jwt_payload["iss"] = self.issuer

        token = jwt.encode(
            jwt_payload,
            self.signing_key,
            algorithm=self.algorithm,
            json_encoder=self.json_encoder,
        )
        if isinstance(token, bytes):
            # For PyJWT <= 1.7.1
            return token.decode("utf-8")
        # For PyJWT >= 2.0.0a1
        return token

    def decode(self, token: Token, verify: bool = True) -> Dict[str, Any]:
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        try:
            return jwt.decode(
                token,
                self.get_verifying_key(token),
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.get_leeway(),
                options={
                    "verify_aud": self.audience is not None,
                    "verify_signature": verify,
                },
            )
        except InvalidAlgorithmError as ex:
            raise TokenBackendError(_("Invalid algorithm specified")) from ex
        except InvalidTokenError as ex:
            raise TokenBackendError(_("Token is invalid or expired")) from ex
