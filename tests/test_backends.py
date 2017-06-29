from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from jose import jwt
from rest_framework_simplejwt.backends import PythonJOSEBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.utils import make_utc


class TestPythonJOSEBackend(TestCase):
    def setUp(self):
        self.secret = 'not_secret'
        self.token_backend = PythonJOSEBackend(self.secret, 'HS256')

    def test_init(self):
        # Should reject unknown algorithms
        with self.assertRaises(TokenBackendError):
            PythonJOSEBackend('not_secret', 'HS512')

        with self.assertRaises(TokenBackendError):
            PythonJOSEBackend('not_secret', 'oienarst oieanrsto i')

        PythonJOSEBackend('not_secret', 'HS256')

    def test_encode(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': make_utc(datetime(year=2000, month=1, day=1))}

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
        # No expiry tokens cause no exception
        payload = {'foo': 'bar'}
        no_exp_token = jwt.encode(payload, self.secret, algorithm='HS256')
        self.token_backend.decode(no_exp_token)

        # Expired tokens should cause exception
        payload['exp'] = timezone.now() - timedelta(seconds=1)
        expired_token = jwt.encode(payload, self.secret, algorithm='HS256')
        with self.assertRaises(TokenBackendError):
            self.token_backend.decode(expired_token)

        # Token with invalid signature should cause exception
        payload['exp'] = timezone.now() + timedelta(days=1)
        token = jwt.encode(payload, self.secret, algorithm='HS256')
        payload['foo'] = 'baz'
        other_token = jwt.encode(payload, self.secret, algorithm='HS256')

        incorrect_payload = other_token.rsplit('.', 1)[0]
        correct_sig = token.rsplit('.', 1)[-1]
        invalid_token = incorrect_payload + '.' + correct_sig

        with self.assertRaises(TokenBackendError):
            self.token_backend.decode(invalid_token)

        # Otherwise, should return data payload for token
        self.assertEqual(self.token_backend.decode(other_token), payload)
