from datetime import timedelta

from django.conf import settings
from django.middleware.csrf import REASON_BAD_TOKEN

from rest_framework_simplejwt.compat import reverse
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.tokens import AccessToken
from .utils import APIViewTestCase, override_api_settings


class TestTestView(APIViewTestCase):
    view_name = 'test_view'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_no_authorization(self):
        res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertIn('credentials were not provided', res.data['detail'])

    def test_wrong_auth_type(self):
        res = self.client.post(
            reverse('token_obtain_sliding'),
            data={
                User.USERNAME_FIELD: self.username,
                'password': self.password,
            },
        )

        token = res.data['token']
        self.authenticate_with_token('Wrong', token)

        res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertIn('credentials were not provided', res.data['detail'])

    def test_expired_token(self):
        old_lifetime = AccessToken.lifetime
        AccessToken.lifetime = timedelta(seconds=0)
        try:
            res = self.client.post(
                reverse('token_obtain_pair'),
                data={
                    User.USERNAME_FIELD: self.username,
                    'password': self.password,
                },
            )
        finally:
            AccessToken.lifetime = old_lifetime

        access = res.data['access']
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertEqual('token_not_valid', res.data['code'])

    def test_user_can_get_sliding_token_and_use_it(self):
        res = self.client.post(
            reverse('token_obtain_sliding'),
            data={
                User.USERNAME_FIELD: self.username,
                'password': self.password,
            },
        )

        token = res.data['token']
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], token)

        with override_api_settings(AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

    def test_user_can_get_sliding_token_and_use_it_when_auth_cookie_enabled(self):
        # should also work with tokens in request.data when AUTH_COOKIE is enabled
        with override_api_settings(AUTH_COOKIE='authorization',
                                   AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            self.test_user_can_get_sliding_token_and_use_it()

    def test_user_can_get_access_refresh_and_delete_sliding_token_cookies_and_use_them(self):
        with override_api_settings(AUTH_COOKIE='authorization',
                                   AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            client = self.client_class(enforce_csrf_checks=True)
            res = client.post(
                reverse('token_obtain_sliding'),
                data={
                    User.USERNAME_FIELD: self.username,
                    'password': self.password,
                },
            )

            csrf_cookie = res.wsgi_request.environ['CSRF_COOKIE']
            client.cookies.load({settings.CSRF_COOKIE_NAME: csrf_cookie})

            res = client.get(reverse(self.view_name))

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(reverse(self.view_name))

            self.assertEqual(res.status_code, 403)
            self.assertTrue(REASON_BAD_TOKEN in res.data['detail'])

            res = client.post(reverse(self.view_name), **{settings.CSRF_HEADER_NAME: csrf_cookie})

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(
                reverse('token_refresh_sliding'),
            )

            res = client.get(reverse(self.view_name))

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(
                reverse('token_delete'),
            )

            res = client.get(reverse(self.view_name))
            self.assertEqual(res.status_code, 401)

            res = client.post(
                reverse('token_refresh_sliding'),
            )
            self.assertEqual(res.status_code, 401)

    def test_user_can_get_access_and_refresh_tokens_and_use_them(self):
        res = self.client.post(
            reverse('token_obtain_pair'),
            data={
                User.USERNAME_FIELD: self.username,
                'password': self.password,
            },
        )

        access = res.data['access']
        refresh = res.data['refresh']

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

        res = self.client.post(
            reverse('token_refresh'),
            data={'refresh': refresh},
        )

        access = res.data['access']

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

    def test_user_can_get_access_and_refresh_tokens_and_use_them_when_auth_cookie_enabled(self):
        # should also work with tokens in request.data when AUTH_COOKIE is enabled
        with override_api_settings(AUTH_COOKIE='authorization', ):
            self.test_user_can_get_access_and_refresh_tokens_and_use_them()

    def test_user_can_get_access_refresh_and_delete_token_cookies_and_use_them(self):
        with override_api_settings(AUTH_COOKIE='authorization', ):
            client = self.client_class(enforce_csrf_checks=True)
            res = client.post(
                reverse('token_obtain_pair'),
                data={
                    User.USERNAME_FIELD: self.username,
                    'password': self.password,
                },
            )

            csrf_cookie = res.wsgi_request.environ['CSRF_COOKIE']
            client.cookies.load({settings.CSRF_COOKIE_NAME: csrf_cookie})

            res = client.get(reverse(self.view_name))

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(reverse(self.view_name))

            self.assertEqual(res.status_code, 403)
            self.assertTrue(REASON_BAD_TOKEN in res.data['detail'])

            res = client.post(reverse(self.view_name), **{settings.CSRF_HEADER_NAME: csrf_cookie})

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(
                reverse('token_refresh'),
            )

            res = client.get(reverse(self.view_name))

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.data['foo'], 'bar')

            res = client.post(
                reverse('token_delete'),
            )

            res = client.get(reverse(self.view_name))
            self.assertEqual(res.status_code, 401)

            res = client.post(
                reverse('token_refresh'),
            )
            self.assertEqual(res.status_code, 401)
