from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six import text_type
from jose import jwt
from mock import patch
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import datetime_to_epoch

from .utils import override_api_settings

User = get_user_model()


class TestToken(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

        self.token = Token()
        self.token.update_expiration(
            from_time=datetime(year=2000, month=1, day=1),
            lifetime=timedelta(seconds=0),
        )

    def test_init(self):
        # Should work with no arguments
        t = Token()
        self.assertTrue(len(t.payload) == 0)

        # No expiry tokens should cause exception
        payload = {'foo': 'bar'}
        no_exp_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(TokenError):
            Token(no_exp_token)

        # Expired tokens should cause exception
        payload['exp'] = datetime.utcnow() - timedelta(seconds=1)
        expired_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(TokenError):
            Token(expired_token)

        # Token with invalid signature should cause exception
        payload['exp'] = datetime.utcnow() + timedelta(days=1)
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        payload['foo'] = 'baz'
        other_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        incorrect_payload = other_token.rsplit('.', 1)[0]
        correct_sig = token.rsplit('.', 1)[-1]
        invalid_token = incorrect_payload + '.' + correct_sig

        with self.assertRaises(TokenError):
            Token(invalid_token)

        # Otherwise, should accept good token
        t = Token(other_token)
        self.assertEqual(t.token, other_token)
        self.assertEqual(t.payload, payload)

    def test_str(self):
        # Should encode the given token
        with override_api_settings(SECRET_KEY='not_secret'):
            encoded_token = str(self.token)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            encoded_token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs',
            ),
        )

    def test_repr(self):
        self.assertEqual(repr(self.token), repr(self.token.payload))

    def test_getitem(self):
        self.assertEqual(self.token['exp'], self.token.payload['exp'])

    def test_setitem(self):
        self.token['test'] = 1234
        self.assertEqual(self.token.payload['test'], 1234)

    def test_contains(self):
        self.assertIn('exp', self.token)

    def test_update_expiration(self):
        now = datetime.utcnow()
        token = Token()

        # By default, should add 'exp' claim to token using utcnow and the
        # TOKEN_LIFETIME setting
        with patch('rest_framework_simplejwt.tokens.datetime') as fake_datetime:
            fake_datetime.utcnow.return_value = now
            token.update_expiration()

        self.assertIn('exp', token)
        self.assertEqual(token['exp'], datetime_to_epoch(now + api_settings.TOKEN_LIFETIME))

        # Should allow overriding of beginning time, lifetime, and claim name
        token.update_expiration(claim='refresh_exp', from_time=now, lifetime=api_settings.TOKEN_REFRESH_LIFETIME)
        self.assertIn('refresh_exp', token)
        self.assertEqual(token['refresh_exp'], datetime_to_epoch(now + api_settings.TOKEN_REFRESH_LIFETIME))

    def test_check_expiration(self):
        token = Token()

        # Should raise an exception if no claim of given kind
        with self.assertRaises(TokenError):
            token.check_expiration()
        with self.assertRaises(TokenError):
            token.check_expiration('some_other_claim')

        now = datetime.utcnow()
        token.update_expiration(from_time=now, lifetime=timedelta(seconds=0))

        # By default, checks 'exp' claim against utcnow.  Should raise an
        # exception if claim has expired.
        utcfromtimestamp = datetime.utcfromtimestamp
        with patch('rest_framework_simplejwt.tokens.datetime') as fake_datetime:
            fake_datetime.utcfromtimestamp = utcfromtimestamp
            fake_datetime.utcnow.return_value = now + timedelta(seconds=10)

            with self.assertRaises(TokenError):
                token.check_expiration()

        # Otherwise, should raise no exception
        token.update_expiration(from_time=now, lifetime=timedelta(days=1))
        token.check_expiration()

        # Should allow specification of claim to be examined and timestamp to
        # compare against
        token.update_expiration('refresh_exp', from_time=now, lifetime=timedelta(days=1))
        token.check_expiration('refresh_exp')
        with self.assertRaises(TokenError):
            token.check_expiration('refresh_exp', current_time=now + timedelta(days=2))

    def test_for_user(self):
        # Should return an authorization token for the given user
        token = Token.for_user(self.user)

        user_id = getattr(self.user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = text_type(user_id)

        self.assertEqual(token[api_settings.USER_ID_CLAIM], user_id)

        self.assertIn('exp', token)
        self.assertTrue(isinstance(token['exp'], int))

        self.assertIn('refresh_exp', token)
        self.assertTrue(isinstance(token['refresh_exp'], int))

        # Test with non-int user id
        with override_api_settings(USER_ID_FIELD='username'):
            token = Token.for_user(self.user)

        self.assertEqual(token[api_settings.USER_ID_CLAIM], self.username)

    def test_encode(self):
        # Should return a JSON web token for the given payload
        payload = {'exp': datetime(year=2000, month=1, day=1)}

        with override_api_settings(SECRET_KEY='not_secret'):
            token = Token._encode(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs',
            ),
        )

    def test_decode(self):
        # No expiry causes no exception
        payload = {'foo': 'bar'}
        no_exp_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        Token._decode(no_exp_token)

        # Expired tokens should cause exception
        payload['exp'] = datetime.utcnow() - timedelta(seconds=1)
        expired_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        with self.assertRaises(TokenError):
            Token._decode(expired_token)

        # Token with invalid signature should cause exception
        payload['exp'] = datetime.utcnow() + timedelta(days=1)
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')
        payload['foo'] = 'baz'
        other_token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        incorrect_payload = other_token.rsplit('.', 1)[0]
        correct_sig = token.rsplit('.', 1)[-1]
        invalid_token = incorrect_payload + '.' + correct_sig

        with self.assertRaises(TokenError):
            Token._decode(invalid_token)

        # Otherwise, should return data payload for token
        self.assertEqual(Token._decode(other_token), payload)
