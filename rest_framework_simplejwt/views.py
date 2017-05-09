from __future__ import unicode_literals

from rest_framework import generics, status
from rest_framework.response import Response

from . import serializers


class TokenViewBase(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenObtainView(TokenViewBase):
    """
    Takes a set of user credentials and returns a JSON web token to prove the
    authentication of those credentials.
    """
    serializer_class = serializers.TokenObtainSerializer

token_obtain = TokenObtainView.as_view()


class TokenRefreshView(TokenViewBase):
    """
    Takes a JSON web token and returns a new, refreshed version if the token's
    refresh period has not expired.
    """
    serializer_class = serializers.TokenRefreshSerializer

token_refresh = TokenRefreshView.as_view()
