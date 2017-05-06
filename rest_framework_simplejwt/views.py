from __future__ import unicode_literals

from rest_framework import generics, status
from rest_framework.response import Response

from . import serializers


class TokenViewBase(generics.GenericAPIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenObtainView(TokenViewBase):
    """
    Takes a set of user credentials and returns a JSON web token to prove the
    authentication of those credentials against some user in the database.
    """
    serializer_class = serializers.TokenObtainSerializer

token_obtain = TokenObtainView.as_view()
