from __future__ import unicode_literals

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six.moves import reload_module
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings

from .utils import override_api_settings

User = get_user_model()
AuthToken = api_settings.AUTH_TOKEN_CLASSES[0]


class TestJWTAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.backend = authentication.JWTAuthentication()

        self.fake_token = b'TokenMcTokenface'
        self.fake_header = b'Bearer ' + self.fake_token

    def test_get_header(self):
        # Should return None if no authorization header
        request = self.factory.get('/test-url/')
        self.assertIsNone(self.backend.get_header(request))

        # Should pull correct header off request
        request = self.factory.get('/test-url/', HTTP_AUTHORIZATION=self.fake_header)
        self.assertEqual(self.backend.get_header(request), self.fake_header)

        # Should work for unicode headers
        request = self.factory.get('/test-url/', HTTP_AUTHORIZATION=self.fake_header.decode('utf-8'))
        self.assertEqual(self.backend.get_header(request), self.fake_header)

    def test_get_raw_token(self):
        # Should return None if header lacks correct type keyword
        with override_api_settings(AUTH_HEADER_TYPE='JWT'):
            reload_module(authentication)
            self.assertIsNone(self.backend.get_raw_token(self.fake_header))
        reload_module(authentication)

        # Should raise error if header is malformed
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_raw_token(b'Bearer one two')

        with self.assertRaises(AuthenticationFailed):
            self.backend.get_raw_token(b'Bearer')

        # Otherwise, should return unvalidated token in header
        self.assertEqual(self.backend.get_raw_token(self.fake_header), self.fake_token)

    def test_get_validated_token(self):
        # Should raise AuthenticationFailed if token not valid
        token = AuthToken()
        token.set_exp(lifetime=-timedelta(days=1))
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_validated_token(str(token))

        # Otherwise, should return validated token
        token.set_exp()
        self.assertEqual(self.backend.get_validated_token(str(token)).payload, token.payload)

    def test_get_user(self):
        payload = {'some_other_id': 'foo'}

        # Should raise error if no recognizable user identification
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Should raise exception if user not found
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u = User.objects.create_user(username='markhamill')
        u.is_active = False
        u.save()

        payload[api_settings.USER_ID_CLAIM] = getattr(u, api_settings.USER_ID_FIELD)

        # Should raise exception if user is inactive
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u.is_active = True
        u.save()

        # Otherwise, should return correct user
        self.assertEqual(self.backend.get_user(payload).id, u.id)


class TestJWTTokenUserAuthentication(TestCase):
    def setUp(self):
        self.backend = authentication.JWTTokenUserAuthentication()

    def test_get_user(self):
        payload = {'some_other_id': 'foo'}

        # Should raise error if no recognizable user identification
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Otherwise, should return a token user object
        user = self.backend.get_user(payload)

        self.assertIsInstance(user, TokenUser)
        self.assertEqual(user.id, 42)
