import importlib

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate, deactivate
from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt import state
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from tests.utils import override_api_settings

User = get_user_model()


class LocalizationTestCase(APITestCase):
    """Test built-in SimpleJWT token views with localization support."""

    def setUp(self):
        """Create a test user for authentication and ensure language is deactivated after each test."""
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.addCleanup(deactivate)

    def get_tokens(self):
        """
        Helper function to generate access and refresh tokens.

        Returns:
            str: Access token.
            str: Refresh token.
        """
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token), str(refresh)

    def get_expired_token(self):
        """
        Helper function to generate an expired access token.

        Returns:
            str: Expired access token.
        """
        refresh = RefreshToken.for_user(self.user)
        refresh["exp"] = timezone.now() - timezone.timedelta(days=1)
        return str(refresh.access_token)

    def get_user_not_found_token(self):
        """
        Helper function to generate an access token for a non-existent user.

        Returns:
            str: Access token with a non-existent user ID.
        """
        refresh = RefreshToken.for_user(self.user)
        refresh[api_settings.USER_ID_CLAIM] = 1111121122
        return str(refresh.access_token)

    def get_invalid_token_type_token(self):
        """
        Helper function to generate an access token with an invalid token type.

        Returns:
            str: Access token with invalid token type.
        """
        refresh = RefreshToken.for_user(self.user)
        payload = refresh.payload
        payload["token_type"] = "invalid_token_type"
        return str(refresh.get_token_backend().encode(payload=payload))

    def get_token_without_user_identification(self):
        """
        Helper function to generate an access token without user identification.

        Returns:
            str: Access token without recognizable user identification.
        """
        refresh = RefreshToken.for_user(self.user)
        del refresh[api_settings.USER_ID_CLAIM]
        return str(refresh.access_token)

    def assert_localized_response(self, url, method, expected, token=None, data=None):
        """
        Helper to check both English and Persian responses for a given endpoint.
        Args:
            url (str): The endpoint URL.
            method (str): HTTP method ('get' or 'post').
            expected (dict): Mapping of language code to dict with 'status' and 'detail'.
            token (str, optional): Bearer token for Authorization header.
            data (dict, optional): Data for POST requests.
        """
        for lang, expected_detail in expected.items():
            with self.subTest(lang=lang):
                headers = {"HTTP_ACCEPT_LANGUAGE": lang}
                if token:
                    headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
                client_method = getattr(self.client, method)
                response = client_method(url, data, **headers) if data else client_method(url, **headers)
                self.assertEqual(response.status_code, expected_detail["status"])
                self.assertEqual(str(response.data["detail"]), expected_detail["detail"])

    def test_token_no_user_identification(self):
        token_without_user = self.get_token_without_user_identification()
        url = reverse("test_view")
        self.assert_localized_response(
            url, "get",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED,
                       "detail": "Token contained no recognizable user identification"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED,
                       "detail": "توکن شامل هیچ شناسه قابل تشخیصی از کاربر نیست"},
            },
            token=token_without_user
        )

    def test_inactive_user_localization(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        token, _ = self.get_tokens()
        url = reverse("test_view")
        self.assert_localized_response(
            url, "get",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "User is inactive"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "کاربر غیرفعال است"},
            },
            token=token
        )

    @override_api_settings(CHECK_REVOKE_TOKEN=True)
    def test_password_change_revoke_token(self):
        token, _ = self.get_tokens()
        self.user.set_password("newpassword")
        self.user.save(update_fields=["password"])
        url = reverse("test_view")
        self.assert_localized_response(
            url, "get",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "The user's password has been changed."},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "رمز عبور کاربر تغییر کرده است"},
            },
            token=token
        )

    def test_invalid_token_type_localization(self):
        invalid_token = self.get_invalid_token_type_token()
        url = reverse("test_view")
        self.assert_localized_response(
            url, "get",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Given token not valid for any token type"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED,
                       "detail": "توکن داده شده برای هیچ نوع توکنی معتبر نمی‌باشد"},
            },
            token=invalid_token
        )

    def test_malformed_authorization_header_localization(self):
        url = reverse("test_view")
        for lang, expected_detail in {
            "en": {"status": status.HTTP_401_UNAUTHORIZED,
                   "detail": "Authorization header must contain two space-delimited values"},
            "fa": {"status": status.HTTP_401_UNAUTHORIZED,
                   "detail": "هدر اعتبارسنجی باید شامل دو مقدار جدا شده با فاصله باشد"},
        }.items():
            with self.subTest(lang=lang):
                headers = {"HTTP_ACCEPT_LANGUAGE": lang, "HTTP_AUTHORIZATION": "Bearer"}
                response = self.client.get(url, **headers)
                self.assertEqual(response.status_code, expected_detail["status"])
                self.assertEqual(str(response.data["detail"]), expected_detail["detail"])

    def test_obtain_token_localization(self):
        data = {"username": "testuser", "password": "testpassword"}
        url = reverse("token_obtain_pair")
        for lang in ["en", "fa"]:
            with self.subTest(lang=lang):
                headers = {"HTTP_ACCEPT_LANGUAGE": lang}
                response = self.client.post(url, data, **headers)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn("access", response.data)

    def test_invalid_credentials_localization(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        url = reverse("token_obtain_pair")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED,
                       "detail": "No active account found with the given credentials"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED,
                       "detail": "هیچ اکانت فعالی برای اطلاعات داده شده یافت نشد"},
            },
            data=data
        )

    def test_verify_token_localization(self):
        invalid_token = "invalid.token.here"
        url = reverse("token_verify")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token is invalid"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن نامعتبر است"},
            },
            data={"token": invalid_token}
        )

    def test_user_not_found_token_localization(self):
        not_found_token = self.get_user_not_found_token()
        url = reverse("test_view")
        self.assert_localized_response(
            url, "get",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "User not found"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "کاربر یافت نشد"},
            },
            token=not_found_token
        )

    def test_refresh_token_localization(self):
        _, refresh_token = self.get_tokens()
        url = reverse("token_refresh")
        for lang in ["en", "fa"]:
            with self.subTest(lang=lang):
                headers = {"HTTP_ACCEPT_LANGUAGE": lang}
                response = self.client.post(url, {"refresh": refresh_token}, **headers)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn("access", response.data)

    def test_expired_refresh_token_localization(self):
        expired_refresh_token = "expired.refresh.token"
        url = reverse("token_refresh")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token is invalid"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن نامعتبر است"},
            },
            data={"refresh": expired_refresh_token}
        )

    def test_algorithm_related_messages_localization(self):
        """
        Ensures setting an invalid algorithm raises a localized TokenBackendError.

        This test is complex because the error is raised when the `state`
        module is first imported. To test this, we must:
        1. Save the original, valid token backend instance.
        2. Use `override_api_settings` to set an invalid algorithm.
        3. Force a reload of the `state` module to trigger the exception.
        4. Assert the exception has the correct localized message.
        5. Restore the original token backend to ensure test isolation.
        """
        original_backend = state.token_backend
        try:
            for lang, expected_detail in {
                "en": "Unrecognized algorithm type 'invalid_algorithm'",
                "fa": "نوع الگوریتم ناشناخته 'invalid_algorithm'",
            }.items():
                with self.subTest(lang=lang):
                    # Activate language middleware to ensure translation is loaded
                    self.client.get(
                        reverse("token_obtain_pair"), HTTP_ACCEPT_LANGUAGE=lang
                    )

                    with override_api_settings(ALGORITHM="invalid_algorithm"):
                        with self.assertRaises(TokenBackendError) as context:
                            importlib.reload(state)
                        self.assertEqual(str(context.exception), expected_detail)
        finally:
            # Restore the original backend to prevent side effects in other tests
            state.token_backend = original_backend

    def test_token_claim_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        del access_token["exp"]
        token = str(access_token)
        url = reverse("token_verify")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token has no 'exp' claim"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن دارای 'exp' claim نمی‌باشد"},
            },
            data={"token": token}
        )

    def test_token_type_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        refresh["token_type"] = "invalid_type"
        token = str(refresh)
        url = reverse("token_refresh")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token has wrong type"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن دارای نوع نادرستی است"},
            },
            data={"refresh": token}
        )

    def test_token_lifetime_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        del access_token["exp"]
        token = str(access_token)
        url = reverse("token_verify")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token has no 'exp' claim"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن دارای 'exp' claim نمی‌باشد"},
            },
            data={"token": token}
        )

    def test_token_claim_expiration_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        refresh["exp"] = timezone.now() - timezone.timedelta(days=1)
        token = str(refresh)
        url = reverse("token_refresh")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token is expired"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن منقضی شده است"},
            },
            data={"refresh": token}
        )

    def test_token_id_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        del refresh["jti"]
        token = str(refresh)
        url = reverse("token_verify")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token has no id"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن id ندارد"},
            },
            data={"token": token}
        )

    def test_token_creation_messages_localization(self):
        refresh = RefreshToken.for_user(self.user)
        del refresh["token_type"]
        del refresh["exp"]
        token = str(refresh)
        url = reverse("token_refresh")
        self.assert_localized_response(
            url, "post",
            {
                "en": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token has no 'exp' claim"},
                "fa": {"status": status.HTTP_401_UNAUTHORIZED, "detail": "توکن دارای 'exp' claim نمی‌باشد"},
            },
            data={"refresh": token}
        )

    def test_leeway_messages_localization(self):
        # Test for English language
        activate("en")
        with self.assertRaises(TokenBackendError) as e:
            backend = TokenBackend("HS256", "secret", leeway="invalid")
            backend.get_leeway()
        self.assertEqual(str(e.exception),
                         "Unrecognized type '<class 'str'>', 'leeway' must be of type int, float or timedelta.")
        deactivate()

        # Test for Persian language
        activate("fa")
        with self.assertRaises(TokenBackendError) as e:
            backend = TokenBackend("HS256", "secret", leeway="invalid")
            backend.get_leeway()
        self.assertEqual(str(e.exception),
                         "نوع ناشناخته '<class 'str'>'، 'leeway' باید از نوع int، float یا timedelta باشد.")
        deactivate()
