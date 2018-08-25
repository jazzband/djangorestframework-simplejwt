from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.settings import api_settings


class APIJWTClient(APIClient):
    def login(self, url="/api/token/", get_response=False, token="access", auth_header_type=0, **credentials):
        """
        :param url: default is "/api/token/", can get string or a django reverse() method to specify login url.
        :param get_response: default is False, if True response object will be returned too.
        :param token: default is "access", specify response data token key.
        :param auth_header_type: default is 0, will specify which header to use for setting Authorization header.
            also can get string for custom header.
        :param credentials: HTTP headers and other data.
        :return: True if login is possible, else False, Also set will set Authorization header based on First element
            in api_settings.AUTH_HEADER_TYPES.
            if "get_response" is set to True, additionally will return response object too.
        """
        auth_header_type = auth_header_type if auth_header_type < len(api_settings.AUTH_HEADER_TYPES) else 0
        response = self.post(url, credentials, format='json')
        if response.status_code == status.HTTP_200_OK:
            self.credentials(
                HTTP_AUTHORIZATION="{0} {1}".format(
                    api_settings.AUTH_HEADER_TYPES[auth_header_type] if isinstance(auth_header_type, int) else auth_header_type,
                    response.data[token]))
            return (True, response) if get_response else True
        else:
            return (False, response) if get_response else False


class APIJWTTestCase(APITestCase):
    client_class = APIJWTClient
