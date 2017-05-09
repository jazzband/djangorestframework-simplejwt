from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six import text_type
from jose import jwt
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.settings import api_settings

from .utils import override_api_settings

User = get_user_model()


class TestTokenObtainSerializer(TestCase):
    def setUp(self):
        self.token_backend = TokenBackend()

        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_get_payload_for_user(self):
        # Should return a dict with the expected keys and values
        payload = self.token_backend.get_payload_for_user(self.user)

        self.assertEqual(
            payload[api_settings.PAYLOAD_ID_FIELD],
            text_type(getattr(self.user, api_settings.USER_ID_FIELD)),
        )

        self.assertIn('exp', payload)
        self.assertTrue(isinstance(payload['exp'], int))

        self.assertIn('refresh_exp', payload)
        self.assertTrue(isinstance(payload['refresh_exp'], int))

    def test_encode(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': datetime(year=2000, month=1, day=1)}

        with override_api_settings(SECRET_KEY='not_secret'):
            token = self.token_backend.encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs',
            ),
        )

    def test_decode(self):
        # No expiry tokens should cause exception
        payload = {'foo': 'bar'}
        no_exp_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(TokenBackendError):
            self.token_backend.decode(no_exp_token)

        # Expired tokens should cause exception
        payload['exp'] = datetime.utcnow() - timedelta(seconds=1)
        expired_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(TokenBackendError):
            self.token_backend.decode(expired_token)

        # Token with invalid signature should cause exception
        payload['exp'] = datetime.utcnow() + timedelta(days=1)
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        payload['foo'] = 'baz'
        other_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        incorrect_payload = other_token.rsplit('.', 1)[0]
        correct_sig = token.rsplit('.', 1)[-1]
        invalid_token = incorrect_payload + '.' + correct_sig

        with self.assertRaises(TokenBackendError):
            self.token_backend.decode(invalid_token)

        # Otherwise, should return data payload for token
        self.assertEqual(self.token_backend.decode(other_token), payload)
