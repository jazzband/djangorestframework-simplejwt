from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six import text_type
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

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

    def test_get_payload(self):
        # Should return a dict with the expected keys and values
        s = TokenObtainSerializer()
        payload = s.get_payload(self.user)

        self.assertEqual(
            payload[api_settings.PAYLOAD_ID_FIELD],
            text_type(getattr(self.user, api_settings.USER_ID_FIELD)),
        )
        self.assertIn('exp', payload)
        self.assertTrue(isinstance(payload['exp'], datetime))

    def test_get_token(self):
        # Should return a JSON web token for the given payload
        s = TokenObtainSerializer()
        payload = s.get_payload(self.user)
        del payload['exp']

        token = s.get_token(payload)

        self.assertEqual(token, 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3BrIjoiMSJ9.nGBUNP5o11vWigBoLqcYt_YlTpkF9blNPqceDIzXBkU')
