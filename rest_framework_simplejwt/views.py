from datetime import datetime

from django.middleware import csrf
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers
from .authentication import AUTH_HEADER_TYPES
from .exceptions import InvalidToken, TokenError


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

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        if api_settings.AUTH_COOKIE:
            csrf.get_token(self.request)
            response = self.set_auth_cookies(response, serializer.validated_data)

        return response

    def set_auth_cookies(self, response, data):
        return response


class TokenRefreshViewBase(TokenViewBase):
    def extract_token_from_cookie(self, request):
        return request

    def post(self, request, *args, **kwargs):
        if api_settings.AUTH_COOKIE:
            request = self.extract_token_from_cookie(request)
        return super().post(request, *args, **kwargs)


class TokenCookieViewMixin:
    def extract_token_from_cookie(self, request):
        """Extracts token from cookie and sets it in request.data as it would be sent by the user"""
        if not request.data:
            token = request.COOKIES.get('{}_refresh'.format(api_settings.AUTH_COOKIE))
            if not token:
                raise NotAuthenticated(detail=_('Refresh cookie not set. Try to authenticate first.'))
            else:
                request.data['refresh'] = token
        return request

    def set_auth_cookies(self, response, data):
        expires = self.get_refresh_token_expiration()
        response.set_cookie(
            api_settings.AUTH_COOKIE, data['access'],
            expires=expires,
            domain=api_settings.AUTH_COOKIE_DOMAIN,
            path=api_settings.AUTH_COOKIE_PATH,
            secure=api_settings.AUTH_COOKIE_SECURE or None,
            httponly=True,
            samesite=api_settings.AUTH_COOKIE_SAMESITE,
        )
        if 'refresh' in data:
            response.set_cookie(
                '{}_refresh'.format(api_settings.AUTH_COOKIE), data['refresh'],
                expires=expires,
                domain=None,
                path=reverse('token_refresh'),
                secure=api_settings.AUTH_COOKIE_SECURE or None,
                httponly=True,
                samesite='Strict',
            )
        return response

    def get_refresh_token_expiration(self):
        return datetime.now() + api_settings.REFRESH_TOKEN_LIFETIME


class TokenObtainPairView(TokenCookieViewMixin, TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = serializers.TokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()


class TokenRefreshView(TokenCookieViewMixin, TokenRefreshViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = serializers.TokenRefreshSerializer

    def get_refresh_token_expiration(self):
        if api_settings.ROTATE_REFRESH_TOKENS:
            return super().get_refresh_token_expiration()
        token = RefreshToken(self.request.data['refresh'])
        return datetime.fromtimestamp(token.payload['exp'])


token_refresh = TokenRefreshView.as_view()


class SlidingTokenCookieViewMixin:
    def extract_token_from_cookie(self, request):
        """Extracts token from cookie and sets it in request.data as it would be sent by the user"""
        if not request.data:
            token = request.COOKIES.get(api_settings.AUTH_COOKIE)
            if not token:
                raise NotAuthenticated(detail=_('Refresh cookie not set. Try to authenticate first.'))
            else:
                request.data['token'] = token
        return request

    def set_auth_cookies(self, response, data):
        response.set_cookie(
            api_settings.AUTH_COOKIE, data['token'],
            expires=datetime.now() + api_settings.REFRESH_TOKEN_LIFETIME,
            domain=api_settings.AUTH_COOKIE_DOMAIN,
            path=api_settings.AUTH_COOKIE_PATH,
            secure=api_settings.AUTH_COOKIE_SECURE or None,
            httponly=True,
            samesite=api_settings.AUTH_COOKIE_SAMESITE,
        )
        return response


class TokenObtainSlidingView(SlidingTokenCookieViewMixin, TokenViewBase):
    """
    Takes a set of user credentials and returns a sliding JSON web token to
    prove the authentication of those credentials.
    """
    serializer_class = serializers.TokenObtainSlidingSerializer


token_obtain_sliding = TokenObtainSlidingView.as_view()


class TokenRefreshSlidingView(SlidingTokenCookieViewMixin, TokenRefreshViewBase):
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


class TokenCookieDeleteView(APIView):
    """
    Deletes httpOnly auth cookies.
    Used as logout view while using AUTH_COOKIE
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        response = Response({})

        if api_settings.AUTH_COOKIE:
            self.delete_auth_cookies(response)

        return response

    def delete_auth_cookies(self, response):
        response.delete_cookie(
            api_settings.AUTH_COOKIE,
            domain=api_settings.AUTH_COOKIE_DOMAIN,
            path=api_settings.AUTH_COOKIE_PATH
        )
        response.delete_cookie(
            '{}_refresh'.format(api_settings.AUTH_COOKIE),
            domain=None,
            path=reverse('token_refresh'),
        )


token_delete = TokenCookieDeleteView.as_view()
