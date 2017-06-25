from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.test import TestCase
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer, TokenObtainSlidingSerializer,
    TokenRefreshSlidingSerializer
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.tokens import SlidingToken


class TestTokenObtainSerializer(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_not_validate_if_any_fields_missing(self):
        s = TokenObtainSerializer(data={})
        self.assertFalse(s.is_valid())
        self.assertIn(s.username_field, s.errors)
        self.assertIn('password', s.errors)

        s = TokenObtainSerializer(data={
            TokenObtainSerializer.username_field: 'oieanrst',
        })
        self.assertFalse(s.is_valid())
        self.assertIn('password', s.errors)

        s = TokenObtainSerializer(data={
            'password': 'oieanrst',
        })
        self.assertFalse(s.is_valid())
        self.assertIn(s.username_field, s.errors)

    def test_it_should_not_validate_if_user_not_found(self):
        s = TokenObtainSerializer(data={
            TokenObtainSerializer.username_field: 'missing',
            'password': 'pass',
        })

        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)

    def test_it_should_not_validate_if_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        s = TokenObtainSerializer(data={
            TokenObtainSerializer.username_field: self.username,
            'password': self.password,
        })

        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)


class TestTokenObtainSlidingSerializer(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_produce_a_json_web_token_when_valid(self):
        s = TokenObtainSlidingSerializer(data={
            TokenObtainSlidingSerializer.username_field: self.username,
            'password': self.password,
        })

        self.assertTrue(s.is_valid())
        self.assertIn('token', s.validated_data)

        # Expecting token type claim to be correct for sliding token.  If this
        # is the case, instantiating a `SlidingToken` instance with encoded
        # token should not raise an exception.
        SlidingToken(s.validated_data['token'])


class TestTokenRefreshSlidingSerializer(TestCase):
    def test_it_should_not_validate_if_token_invalid(self):
        token = SlidingToken()
        del token['exp']

        s = TokenRefreshSlidingSerializer(data={'token': str(token)})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn("has no 'exp' claim", s.errors['non_field_errors'][0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenRefreshSlidingSerializer(data={'token': str(token)})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn('invalid or expired', s.errors['non_field_errors'][0])

    def test_it_should_not_validate_if_token_has_no_refresh_exp_claim(self):
        token = SlidingToken()
        del token[api_settings.SLIDING_REFRESH_EXP_CLAIM]

        s = TokenRefreshSlidingSerializer(data={'token': str(token)})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn("has no '{}' claim".format(api_settings.SLIDING_REFRESH_EXP_CLAIM), s.errors['non_field_errors'][0])

    def test_it_should_not_validate_if_token_has_refresh_period_expired(self):
        token = SlidingToken()
        token.set_exp(api_settings.SLIDING_REFRESH_EXP_CLAIM, lifetime=-timedelta(days=1))

        s = TokenRefreshSlidingSerializer(data={'token': str(token)})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn("'{}' claim has expired".format(api_settings.SLIDING_REFRESH_EXP_CLAIM), s.errors['non_field_errors'][0])

    def test_it_should_not_validate_if_token_has_wrong_type(self):
        token = SlidingToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = 'wrong_type'
        token.set_exp(api_settings.SLIDING_REFRESH_EXP_CLAIM, lifetime=-timedelta(days=1))

        s = TokenRefreshSlidingSerializer(data={'token': str(token)})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn("wrong type", s.errors['non_field_errors'][0])

    def test_it_should_update_token_exp_claim_if_everything_ok(self):
        old_token = SlidingToken()

        lifetime = api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1)
        old_exp = old_token.current_time + lifetime

        old_token.set_exp(lifetime=lifetime)

        # Serializer validates
        s = TokenRefreshSlidingSerializer(data={'token': str(old_token)})
        self.assertTrue(s.is_valid())

        # Expiration claim has moved into future
        new_token = SlidingToken(s.validated_data['token'])
        new_exp = datetime.utcfromtimestamp(new_token['exp'])

        self.assertTrue(old_exp < new_exp)
