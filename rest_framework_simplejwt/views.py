from rest_framework import generics, status
from rest_framework.response import Response

from . import serializers
from .authentication import AUTH_HEADER_TYPES
from .exceptions import InvalidToken, TokenError
from .settings import api_settings
from .tokens import RefreshToken, UntypedToken
from .utils import datetime_from_epoch


class TokenViewBase(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None

    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = serializers.TokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = serializers.TokenRefreshSerializer


token_refresh = TokenRefreshView.as_view()


class TokenObtainSlidingView(TokenViewBase):
    """
    Takes a set of user credentials and returns a sliding JSON web token to
    prove the authentication of those credentials.
    """
    serializer_class = serializers.TokenObtainSlidingSerializer


token_obtain_sliding = TokenObtainSlidingView.as_view()


class TokenRefreshSlidingView(TokenViewBase):
    """
    Takes a sliding JSON web token and returns a new, refreshed version if the
    token's refresh period has not expired.
    """
    serializer_class = serializers.TokenRefreshSlidingSerializer


token_refresh_sliding = TokenRefreshSlidingView.as_view()


class TokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """
    serializer_class = serializers.TokenVerifySerializer


token_verify = TokenVerifyView.as_view()


##
## Views for cookie based token (only refresh token in cookie)
##

class TokenCookieBaseView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None

    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )


class TokenPairCookieBaseView(TokenCookieBaseView):
    def use_serializer(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        validated_data = serializer.validated_data
        
        if 'refresh' in validated_data:
            refresh_token = RefreshToken(validated_data.pop('refresh'))
        else:
            refresh_token = None

        response = Response(validated_data, status=status.HTTP_200_OK)

        if not refresh_token == None:
            response.set_cookie(
                key = 'refresh',
                value = str(refresh_token),
                expires = datetime_from_epoch(refresh_token.payload['exp']),
                path = api_settings.TOKEN_COOKIE_PATH,
                domain = api_settings.TOKEN_COOKIE_DOMAIN,
                samesite = api_settings.TOKEN_COOKIE_SAMESITE,
                secure = api_settings.TOKEN_COOKIE_SECURE,
                httponly = True
                )
        
        return response


class TokenObtainPairCookieView(TokenPairCookieBaseView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.

    Refresh token is sent via httponly cookie. This view needs CSRF protection.
    """

    serializer_class = serializers.TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)

        return self.use_serializer(serializer)


token_obtain_pair_cookie = TokenObtainPairCookieView.as_view()


class TokenRefreshCookieView(TokenPairCookieBaseView):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.

    If refresh token is rotated, it is sent via httponly cookie. This view needs CSRF protection.
    """
    serializer_class = serializers.TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            refresh = request.COOKIES['refresh']
        except KeyError:
            refresh = ''
        
        serializer = self.get_serializer(data = {'refresh': refresh})

        return self.use_serializer(serializer)


token_refresh_cookie = TokenRefreshCookieView.as_view()


class TokenVerifyCookieView(TokenCookieBaseView):
    """
    Takes a token residing in a cookie and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """
    def post(self, request, *args, **kwargs):
        try:
            refresh = request.COOKIES['refresh']
        except KeyError:
            refresh = ''

        serializer = serializers.TokenVerifySerializer(data = {'token': refresh})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


token_verify_cookie = TokenVerifyCookieView.as_view()