from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, authentication

from .exceptions import AuthenticationFailed, InvalidToken, TokenError
from .settings import api_settings
from .state import User

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES = set(
    h.encode(HTTP_HEADER_ENCODING)
    for h in AUTH_HEADER_TYPES
)


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(api_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


class JWTTokenUserAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns a stateless user object which is backed by the given validated
        token.
        """
        if api_settings.USER_ID_CLAIM not in validated_token:
            # The TokenUser class assumes tokens will have a recognizable user
            # identifier claim.
            raise InvalidToken(_('Token contained no recognizable user identification'))

        return api_settings.TOKEN_USER_CLASS(validated_token)


def default_user_authentication_rule(user):
    # Prior to Django 1.10, inactive users could be authenticated with the
    # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
    # prevents inactive users from authenticating.  App designers can still
    # allow inactive users to authenticate by opting for the new
    # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
    # users from authenticating to enforce a reasonable policy and provide
    # sensible backwards compatibility with older Django versions.
    return True if user is not None and user.is_active else False
