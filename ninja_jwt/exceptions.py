from django.utils.translation import gettext_lazy as _
from ninja_extra import exceptions, status


class DetailDictMixin:
    default_detail = ""
    default_code = ""

    def __init__(self, detail=None, code=None) -> None:
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

        super().__init__(detail_dict)


class TokenError(Exception):
    pass


class TokenBackendError(Exception):
    pass


class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    pass


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"


class ValidationError(DetailDictMixin, exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid input.")
    default_code = "invalid"
