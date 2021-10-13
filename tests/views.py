from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt import authentication


class TestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        return Response({"foo": "bar"})


test_view = TestView.as_view()
