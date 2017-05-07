from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.six import text_type
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

from .utils import override_api_settings

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
        payload = {'exp': datetime(year=2000, month=1, day=1)}

        with override_api_settings(SECRET_KEY='not_secret'):
            token = s.get_token(payload)

        # Token could be one of two depending on header dict ordering
        self.assertIn(
            token,
            (
                'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk0NjY4NDgwMH0.NHpdD2X8ub4SE_MZLBedWa57FCpntGaN_r6f8kNKdUs',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk0NjY4NDgwMH0.jvxQgXCSDToR8uKoRJcMT-LmMJJn2-NM76nfSR2FOgs',
            ),
        )
