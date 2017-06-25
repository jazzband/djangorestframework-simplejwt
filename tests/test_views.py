from __future__ import unicode_literals

from datetime import datetime, timedelta

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.tokens import SlidingToken

from .utils import APIViewTestCase


class TestTokenObtainSlidingView(APIViewTestCase):
    view_name = 'token_obtain_sliding'

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


class TestTokenRefreshSlidingView(APIViewTestCase):
    view_name = 'token_refresh_sliding'

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
        token = SlidingToken()
        del token['exp']

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn("has no 'exp' claim", res.data['non_field_errors'][0])

        token.set_exp(lifetime=-timedelta(seconds=1))

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn('invalid or expired', res.data['non_field_errors'][0])

    def test_it_should_return_400_if_token_has_no_refresh_exp_claim(self):
        token = SlidingToken()
        del token[api_settings.SLIDING_REFRESH_EXP_CLAIM]

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn("has no '{}' claim".format(api_settings.SLIDING_REFRESH_EXP_CLAIM), res.data['non_field_errors'][0])

    def test_it_should_return_400_if_token_has_refresh_period_expired(self):
        token = SlidingToken()
        token.set_exp(api_settings.SLIDING_REFRESH_EXP_CLAIM, lifetime=-timedelta(seconds=1))

        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 400)
        self.assertIn('non_field_errors', res.data)
        self.assertIn("'{}' claim has expired".format(api_settings.SLIDING_REFRESH_EXP_CLAIM), res.data['non_field_errors'][0])

    def test_it_should_update_token_exp_claim_if_everything_ok(self):
        now = datetime.utcnow()

        token = SlidingToken()
        exp = now + api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1)
        token.set_exp(from_time=now, lifetime=api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1))

        # View returns 200
        res = self.view_post(data={'token': str(token)})
        self.assertEqual(res.status_code, 200)

        # Expiration claim has moved into future
        new_token = SlidingToken(res.data['token'])
        new_exp = datetime.utcfromtimestamp(new_token['exp'])

        self.assertTrue(exp < new_exp)
