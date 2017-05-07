from django.contrib.auth import get_user_model
from rest_framework_simplejwt.compat import reverse
from rest_framework_simplejwt.settings import api_settings

from .utils import APIViewTestCase

User = get_user_model()


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
            reverse('rest_framework_simplejwt:token_obtain'),
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

    def test_user_can_get_token_and_use_it(self):
        res = self.client.post(
            reverse('rest_framework_simplejwt:token_obtain'),
            data={
                User.USERNAME_FIELD: self.username,
                'password': self.password,
            },
        )

        token = res.data['token']
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPE, token)

        res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['foo'], 'bar')
