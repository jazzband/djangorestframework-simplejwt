from datetime import timedelta
from importlib import reload
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow

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

        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
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

        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
        self.assertIn("credentials were not provided", res.data["detail"])

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
    )
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

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual("token_not_valid", res.data["code"])

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.SlidingToken",),
    )
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

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
    )
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

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

        res = self.client.post(
            reverse("token_refresh"),
            data={"refresh": refresh},
        )

        access = res.data["access"]

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
        TOKEN_FAMILY_CHECK_ON_ACCESS=True,
    )
    def test_access_token_performs_family_blacklist_check_when_enabled(self):
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

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

        RefreshToken(str(refresh)).blacklist_family()

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual("token_not_valid", res.data["code"])

        error_msg = res.data.get("messages")[0].get("message")
        self.assertIn("family", error_msg)
        self.assertIn("blacklisted", error_msg)

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
        TOKEN_FAMILY_CHECK_ON_ACCESS=True,
        # We use a smaller family lifetime than the default access token lifetime
        # so we dont have to reload the tokens and serializers modules
        TOKEN_FAMILY_LIFETIME=timedelta(minutes=2),
    )
    def test_access_token_performs_family_expiration_check_when_enabled(self):

        with freeze_time(aware_utcnow() - timedelta(minutes=2)):
            res = self.client.post(
                reverse("token_obtain_pair"),
                data={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
            )

        access = res.data["access"]

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)

        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual("token_not_valid", res.data["code"])

        error_msg = res.data.get("messages")[0].get("message")
        self.assertIn("family", error_msg)
        self.assertIn("expired", error_msg)

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
        TOKEN_FAMILY_CHECK_ON_ACCESS=False, 
        # We use a smaller family lifetime than the default access token lifetime
        # so we dont have to reload the tokens and serializers modules
        TOKEN_FAMILY_LIFETIME=timedelta(minutes=2),
    )
    def test_access_token_does_not_performs_family_checks_when_disabled(self):
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
        res = self.view_get()

        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

        # blacklisting the token family
        RefreshToken(str(refresh)).blacklist_family()

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)
        res = self.view_get()

        # response must be 200_OK  since the family check for the access token is disabled
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")

        # testing for family expiration now
        with freeze_time(aware_utcnow() - timedelta(minutes=2)):
            res = self.client.post(
                reverse("token_obtain_pair"),
                data={
                    User.USERNAME_FIELD: self.username,
                    "password": self.password,
                },
            )

        access = res.data["access"]

        self.authenticate_with_token(api_settings.AUTH_HEADER_TYPES[0], access)
        res = self.view_get()
    
        # response must be 200_OK  since the family check for the access token is disabled
        self.assertEqual(res.status_code, HTTP_200_OK)
        self.assertEqual(res.data["foo"], "bar")     
