from datetime import timedelta

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.compat import reverse
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from .utils import APIViewTestCase, override_api_settings

User = get_user_model()


class TestTestView(APIViewTestCase):
    view_name = "test_view"

    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_no_authorization(self):
        res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertIn("credentials were not provided", res.data["detail"])

    def test_wrong_auth_type(self):
        res = self.client.post(
            reverse("token_obtain_sliding"),
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
        )

        token = res.data["token"]
        self.authenticate_with_token("Wrong", token)

        res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertIn("credentials were not provided", res.data["detail"])

    def test_expired_token(self):
        old_lifetime = AccessToken.lifetime
        AccessToken.lifetime = timedelta(seconds=0)
        try:
            res = self.client.post(
                reverse("token_obtain_pair"),
                data={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
            )
        finally:
            AccessToken.lifetime = old_lifetime

        access = res.data["access"]
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(
            AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",)
        ):
            res = self.view_get()

        self.assertEqual(res.status_code, 401)
        self.assertEqual("token_not_valid", res.data["code"])

    def test_user_can_get_sliding_token_and_use_it(self):
        res = self.client.post(
            reverse("token_obtain_sliding"),
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
        )

        token = res.data["token"]
        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], token)

        with override_api_settings(
            AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.SlidingToken",)
        ):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["foo"], "bar")

    def test_user_can_get_access_and_refresh_tokens_and_use_them(self):
        res = self.client.post(
            reverse("token_obtain_pair"),
            data={
                User.USERNAME_FIELD: self.username,
                "password": self.password,
            },
        )

        access = res.data["access"]
        refresh = res.data["refresh"]

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(
            AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",)
        ):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["foo"], "bar")

        res = self.client.post(
            reverse("token_refresh"),
            data={"refresh": refresh},
        )

        access = res.data["access"]

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        with override_api_settings(
            AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",)
        ):
            res = self.view_get()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["foo"], "bar")
