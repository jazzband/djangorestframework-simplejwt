from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from jose import jwt
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer, TokenRefreshSerializer
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import datetime_to_epoch

User = get_user_model()


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

    def test_it_should_produce_a_json_web_token_when_valid(self):
        s = TokenObtainSerializer(data={
            TokenObtainSerializer.username_field: self.username,
            'password': self.password,
        })

        self.assertTrue(s.is_valid())
        self.assertIn('token', s.validated_data)


class TestTokenRefreshSerializer(TestCase):
    def test_it_should_not_validate_if_token_invalid(self):
        payload = {'foo': 'bar'}
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        s = TokenRefreshSerializer(data={'token': token})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn('has no expiration', s.errors['non_field_errors'][0])

        payload['exp'] = datetime.utcnow() - timedelta(days=1)
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        s = TokenRefreshSerializer(data={'token': token})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn('invalid or expired', s.errors['non_field_errors'][0])

    def test_it_should_not_validate_if_token_has_no_refresh_exp_claim(self):
        payload = {
            'foo': 'bar',
            'exp': datetime.utcnow() + timedelta(days=1),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        s = TokenRefreshSerializer(data={'token': token})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn('no refresh expiration claim', s.errors['non_field_errors'][0])

    def test_it_should_not_validate_if_token_has_refresh_period_expired(self):
        payload = {
            'foo': 'bar',
            'exp': datetime.utcnow() + timedelta(days=1),
            'refresh_exp': datetime_to_epoch(datetime.utcnow() - timedelta(days=1)),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        s = TokenRefreshSerializer(data={'token': token})
        self.assertFalse(s.is_valid())
        self.assertIn('non_field_errors', s.errors)
        self.assertIn('refresh period has expired', s.errors['non_field_errors'][0])

    def test_it_should_update_tokens_exp_claim_if_everything_ok(self):
        now = datetime.utcnow()

        exp = now + timedelta(seconds=10)
        refresh_exp = now + timedelta(days=1)

        payload = {
            'foo': 'bar',
            'exp': exp,
            'refresh_exp': datetime_to_epoch(refresh_exp),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        # Serializer validates
        s = TokenRefreshSerializer(data={'token': token})
        self.assertTrue(s.is_valid())

        # Expiration claim has moved into future
        new_token = jwt.decode(s.validated_data['token'], api_settings.SECRET_KEY, algorithms=['HS256'])
        new_exp = datetime.utcfromtimestamp(new_token['exp'])

        self.assertTrue(exp < new_exp)
