from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.compat import reverse
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from .utils import APIViewTestCase, override_api_settings


class TestTestView(APIViewTestCase):
    view_name = 'test_view'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
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
                self.user_model.USERNAME_FIELD: self.username,
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
                    self.user_model.USERNAME_FIELD: self.username,
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
                self.user_model.USERNAME_FIELD: self.username,
                'password': self.password,
            },
        )

        token = res.data['token']
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], token)

        with override_api_settings(AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

    def test_user_can_get_access_and_refresh_tokens_and_use_them(self):
        res = self.client.post(
            reverse('token_obtain_pair'),
            data={
                self.user_model.USERNAME_FIELD: self.username,
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


class TestTestViewWithCookie(APIViewTestCase):

    view_name = 'test_view'

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.client = self.client_class(enforce_csrf_checks=True)

    def test_no_authorization_with_auth_cookie(self):
        auth_cookie_name = 'authorization'
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertIn('credentials were not provided', res.data['detail'])

    def test_user_can_get_access_refresh_and_delete_sliding_token_and_use_them_with_auth_cookie(self):
        auth_cookie_name = 'authorization'
        auth_refresh_cookie_name = '%s_refresh' % auth_cookie_name
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.client.post(
                reverse('token_obtain_sliding'),
                data={
                    self.user_model.USERNAME_FIELD: self.username,
                    'password': self.password,
                },
            )
        self.assertNotIn('access', res.data)
        self.assertGreater(len(res.cookies.get(auth_cookie_name).value), 0)
        # Sliding tokens don't have a refresh token, it's a splippery slope if you ask me
        self.assertIsNone(res.cookies.get(auth_refresh_cookie_name))
        self.assertEqual(res.status_code, 200)
        csrf_token = res.data['csrf_token']

        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            # Get on test view, this should work
            res = self.view_get()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

        # Refresh the token
        with override_api_settings(AUTH_COOKIE=auth_cookie_name):
            res = self.client.post(reverse('token_refresh_sliding'))
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.cookies.get(auth_cookie_name).value), 0)
        self.assertIsNone(res.cookies.get(auth_refresh_cookie_name))

        # Get again
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.view_get()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

        # Try a post without CSRF
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.view_post(data={})
        self.assertEqual(res.status_code, 403)

        # Add CSRF
        self.client.credentials(HTTP_X_CSRFTOKEN=csrf_token)
        self.client.cookies[settings.CSRF_COOKIE_NAME] = csrf_token
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.view_post(data={})

        self.assertEqual(res.status_code, 200)

        # Delete cookies
        with override_api_settings(AUTH_COOKIE=auth_cookie_name):
            res = self.client.post(reverse('token_delete'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.cookies.get(auth_cookie_name).value, '')
        self.assertEqual(res.cookies.get(auth_refresh_cookie_name).value, '')
        self.assertEqual(res.cookies.get(settings.CSRF_COOKIE_NAME).value, '')

    def test_user_can_get_access_refresh_and_delete_tokens_and_use_them_with_auth_cookie(self):
        auth_cookie_name = 'authorization'
        auth_refresh_cookie_name = '%s_refresh' % auth_cookie_name
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.SlidingToken',)):
            res = self.client.post(
                reverse('token_obtain_pair'),
                data={
                    self.user_model.USERNAME_FIELD: self.username,
                    'password': self.password,
                },
            )

        # There is no reason to have the tokens in the response body we set them in the cookie
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertIsNotNone(res.data['csrf_token'])
        # Make sure set cookie is called
        self.assertGreater(len(res.cookies.get(auth_cookie_name).value), 0)
        self.assertGreater(len(res.cookies.get(auth_refresh_cookie_name).value), 0)
        # Get the csrf token
        csrf_token = res.data['csrf_token']

        # Get on test view
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

        # Refresh the token
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, ROTATE_REFRESH_TOKENS=False):
            res = self.client.post(reverse('token_refresh'))
        self.assertEqual(res.status_code, 200)
        # Make sure we only update the access token
        self.assertGreater(len(res.cookies.get(auth_cookie_name).value), 0)
        self.assertIsNone(res.cookies.get(auth_refresh_cookie_name))
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertIn('csrf_token', res.data)

        # Now refresh token with rotation enabled
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, ROTATE_REFRESH_TOKENS=True):
            res = self.client.post(reverse('token_refresh'))

        self.assertEqual(res.status_code, 200)
        # Make sure both tokens are updated
        self.assertGreater(len(res.cookies.get(auth_cookie_name).value), 0)
        self.assertGreater(len(res.cookies.get(auth_refresh_cookie_name).value), 0)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)
        self.assertIn('csrf_token', res.data)

        # Get on test view again and test that it stills work after a refresh
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')

        # Try to post, it should fail because CSRF token is not in the header
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_post(data={})
        self.assertEqual(res.status_code, 403)

        # Add CSRF
        self.client.credentials(HTTP_X_CSRFTOKEN=csrf_token)
        self.client.cookies[settings.CSRF_COOKIE_NAME] = csrf_token
        with override_api_settings(AUTH_COOKIE=auth_cookie_name, AUTH_TOKEN_CLASSES=('rest_framework_simplejwt.tokens.AccessToken',)):
            res = self.view_post(data={})

        self.assertEqual(res.status_code, 200)

        # Delete cookies
        with override_api_settings(AUTH_COOKIE=auth_cookie_name):
            res = self.client.post(reverse('token_delete'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.cookies.get(auth_cookie_name).value, '')
        self.assertEqual(res.cookies.get(auth_refresh_cookie_name).value, '')
        self.assertEqual(res.cookies.get(settings.CSRF_COOKIE_NAME).value, '')
