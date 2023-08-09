from typing import Any, Type

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from ninja_extra.security import AsyncHttpBearer, HttpBearer

from .exceptions import AuthenticationFailed, InvalidToken, TokenError
from .settings import api_settings
from .tokens import Token


class JWTBaseAuthentication:
    def __init__(self) -> None:
        super().__init__()
        self.user_model = get_user_model()

    @classmethod
    def get_validated_token(cls, raw_token) -> Type[Token]:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    def get_user(self, validated_token) -> Type[AbstractUser]:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as e:
            raise InvalidToken(
                _("Token contained no recognizable user identification")
            ) from e

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist as e:
            raise AuthenticationFailed(_("User not found")) from e

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"))

        return user

    def jwt_authenticate(self, request: HttpRequest, token: str) -> Type[AbstractUser]:
        request.user = AnonymousUser()
        validated_token = self.get_validated_token(token)
        user = self.get_user(validated_token)
        request.user = user
        return user


class JWTAuth(JWTBaseAuthentication, HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Any:
        return self.jwt_authenticate(request, token)


class JWTStatelessUserAuthentication(JWTBaseAuthentication, HttpBearer):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header without performing a database lookup to obtain a user instance.
    """

    def authenticate(self, request: HttpRequest, token: str) -> Any:
        return self.jwt_authenticate(request, token)

    def get_user(self, validated_token: Any) -> Type[AbstractUser]:
        """
        Returns a stateless user object which is backed by the given validated
        token.
        """
        if api_settings.USER_ID_CLAIM not in validated_token:
            # The TokenUser class assumes tokens will have a recognizable user
            # identifier claim.
            raise InvalidToken(_("Token contained no recognizable user identification"))

        return api_settings.TOKEN_USER_CLASS(validated_token)


JWTTokenUserAuth = JWTStatelessUserAuthentication


def default_user_authentication_rule(user) -> bool:
    # Prior to Django 1.10, inactive users could be authenticated with the
    # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
    # prevents inactive users from authenticating.  App designers can still
    # allow inactive users to authenticate by opting for the new
    # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
    # users from authenticating to enforce a reasonable policy and provide
    # sensible backwards compatibility with older Django versions.
    return user is not None and user.is_active


if not django.VERSION < (3, 1):
    from asgiref.sync import sync_to_async

    class AsyncJWTBaseAuthentication(JWTBaseAuthentication):
        async def async_jwt_authenticate(
            self, request: HttpRequest, token: str
        ) -> Type[AbstractUser]:
            request.user = AnonymousUser()
            get_validated_token = sync_to_async(self.get_validated_token)
            validated_token = await get_validated_token(token)
            get_user = sync_to_async(self.get_user)
            user = await get_user(validated_token)
            request.user = user
            return user

    class AsyncJWTAuth(AsyncJWTBaseAuthentication, JWTAuth, AsyncHttpBearer):
        async def authenticate(self, request: HttpRequest, token: str) -> Any:
            return await self.async_jwt_authenticate(request, token)

    class AsyncJWTTokenUserAuth(
        AsyncJWTBaseAuthentication, JWTTokenUserAuth, AsyncHttpBearer
    ):
        async def authenticate(self, request: HttpRequest, token: str) -> Any:
            return await self.async_jwt_authenticate(request, token)
