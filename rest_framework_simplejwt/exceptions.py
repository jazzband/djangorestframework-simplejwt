from typing import Any, Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class TokenError(Exception):
    pass


class ExpiredTokenError(TokenError):
    pass


class TokenBackendError(Exception):
    pass


class TokenBackendExpiredToken(TokenBackendError):
    pass


class RefreshTokenBlacklistedError(TokenError):
    """Raised when a refresh token is found in the blacklist."""
    pass


class DetailDictMixin:
    default_detail: str
    default_code: str

    def __init__(
        self,
        detail: Union[dict[str, Any], str, None] = None,
        code: Optional[str] = None,
    ) -> None:
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {"detail": self.default_detail, "code": self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict["detail"] = detail

        if code is not None:
            detail_dict["code"] = code

        super().__init__(detail_dict)  # type: ignore


class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    pass


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"


class TokenFamilyNotConfigured(DetailDictMixin, exceptions.APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = _(
        "Token family functionality is not enabled or available. Please check your configuration."
    )
    default_code = "token_family_not_configured"