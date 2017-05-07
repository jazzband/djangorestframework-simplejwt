from __future__ import unicode_literals

from django.contrib.auth import get_user_model

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
