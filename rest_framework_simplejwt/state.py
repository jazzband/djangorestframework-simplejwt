from .backends import TokenBackend
from .settings import api_settings

token_backend = TokenBackend(
    api_settings.ALGORITHM,
    api_settings.SIGNING_KEY,
    api_settings.VERIFYING_KEY,
    api_settings.AUDIENCE if api_settings.AUDIENCE_VALIDATION == "static" else None,
    api_settings.ISSUER if isinstance(api_settings.ISSUER, str) else None,
    api_settings.JWK_URL,
    api_settings.LEEWAY,
    api_settings.JSON_ENCODER,
)
