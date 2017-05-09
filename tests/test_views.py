from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from jose import jwt
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import datetime_to_epoch

from .utils import APIViewTestCase

User = get_user_model()


class TestTokenObtainView(APIViewTestCase):
    view_name = 'rest_framework_simplejwt:token_obtain'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={})
        self.assertEqual(res.status_code, 400)
        self.assertIn(User.USERNAME_FIELD, res.data)
        self.assertIn('password', res.data)

        res = self.view_post(data={User.USERNAME_FIELD: self.username})
        self.assertEqual(res.status_code, 400)
        self.assertIn('password', res.data)

        res = self.view_post(data={'password': self.password})
        self.assertEqual(res.status_code, 400)
        self.assertIn(User.USERNAME_FIELD, res.data)

    def test_credentials_wrong(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': 'test_user',
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)

    def test_success(self):
        res = self.view_post(data={
            User.USERNAME_FIELD: self.username,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.data)


class TestTokenRefreshView(APIViewTestCase):
    view_name = 'rest_framework_simplejwt:token_refresh'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_fields_missing(self):
        res = self.view_post(data={})
        self.assertEqual(res.status_code, 400)
        self.assertIn('token', res.data)

    def test_it_should_return_400_if_token_invalid(self):
        payload = {'foo': 'bar'}
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        res = self.view_post(data={'token': token})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn('has no expiration', res.data['non_field_errors'][0])

        payload['exp'] = datetime.utcnow() - timedelta(days=1)
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        res = self.view_post(data={'token': token})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn('invalid or expired', res.data['non_field_errors'][0])

    def test_it_should_return_400_if_token_has_no_refresh_exp_claim(self):
        payload = {
            'foo': 'bar',
            'exp': datetime.utcnow() + timedelta(days=1),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        res = self.view_post(data={'token': token})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn('no refresh expiration claim', res.data['non_field_errors'][0])

    def test_it_should_return_400_if_token_has_refresh_period_expired(self):
        payload = {
            'foo': 'bar',
            'exp': datetime.utcnow() + timedelta(days=1),
            'refresh_exp': datetime_to_epoch(datetime.utcnow() - timedelta(days=1)),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        res = self.view_post(data={'token': token})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn('refresh period has expired', res.data['non_field_errors'][0])

    def test_it_should_update_token_exp_claim_if_everything_ok(self):
        now = datetime.utcnow()

        exp = now + timedelta(seconds=10)
        refresh_exp = now + timedelta(days=1)

        payload = {
            'foo': 'bar',
            'exp': exp,
            'refresh_exp': datetime_to_epoch(refresh_exp),
        }
        token = jwt.encode(payload, api_settings.SECRET_KEY, algorithm='HS256')

        # View returns 200
        res = self.view_post(data={'token': token})
        self.assertEqual(res.status_code, 200)

        # Expiration claim has moved into future
        new_token = jwt.decode(res.data['token'], api_settings.SECRET_KEY, algorithms=['HS256'])
        new_exp = datetime.utcfromtimestamp(new_token['exp'])

        self.assertTrue(exp < new_exp)
