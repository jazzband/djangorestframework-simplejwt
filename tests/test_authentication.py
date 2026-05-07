from datetime import timedelta
from importlib import reload

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, SlidingToken
from rest_framework_simplejwt.utils import get_md5_hash_password

from .utils import override_api_settings

User = get_user_model()
AuthToken = api_settings.AUTH_TOKEN_CLASSES[0]


class TestJWTAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.backend = authentication.JWTAuthentication()

        self.fake_token = b"TokenMcTokenface"
        self.fake_header = b"Bearer " + self.fake_token

    def test_get_header(self):
        # Should return None if no authorization header
        request = self.factory.get("/test-url/")
        self.assertIsNone(self.backend.get_header(request))

        # Should pull correct header off request
        request = self.factory.get("/test-url/", HTTP_AUTHORIZATION=self.fake_header)
        self.assertEqual(self.backend.get_header(request), self.fake_header)

        # Should work for unicode headers
        request = self.factory.get(
            "/test-url/", HTTP_AUTHORIZATION=self.fake_header.decode("utf-8")
        )
        self.assertEqual(self.backend.get_header(request), self.fake_header)

    @override_api_settings(AUTH_HEADER_NAME="HTTP_X_ACCESS_TOKEN")
    def test_get_header_x_access_token(self):
        # Should pull correct header off request when using X_ACCESS_TOKEN
        request = self.factory.get("/test-url/", HTTP_X_ACCESS_TOKEN=self.fake_header)
        self.assertEqual(self.backend.get_header(request), self.fake_header)

        # Should work for unicode headers when using
        request = self.factory.get(
            "/test-url/", HTTP_X_ACCESS_TOKEN=self.fake_header.decode("utf-8")
        )
        self.assertEqual(self.backend.get_header(request), self.fake_header)

    def test_get_raw_token(self):
        reload(authentication)

        # Should return None if an empty AUTHORIZATION header is sent
        self.assertIsNone(self.backend.get_raw_token(b""))

        # Should raise error if header is malformed
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_raw_token(b"Bearer one two")

        with self.assertRaises(AuthenticationFailed):
            self.backend.get_raw_token(b"Bearer")

        # Otherwise, should return unvalidated token in header
        self.assertEqual(self.backend.get_raw_token(self.fake_header), self.fake_token)

    @override_api_settings(AUTH_HEADER_TYPES="JWT")
    def test_get_raw_token_incorrect_header_keyword(self):
        # Should return None if header lacks correct type keyword
        # AUTH_HEADER_TYPES is "JWT", but header is "Bearer"
        reload(authentication)
        self.assertIsNone(self.backend.get_raw_token(self.fake_header))

    @override_api_settings(AUTH_HEADER_TYPES=("JWT", "Bearer"))
    def test_get_raw_token_multi_header_keyword(self):
        # Should return token if header has one of many valid token types
        reload(authentication)
        self.assertEqual(
            self.backend.get_raw_token(self.fake_header),
            self.fake_token,
        )

    def test_get_validated_token(self):
        # Should raise InvalidToken if token not valid
        token = AuthToken()
        token.set_exp(lifetime=-timedelta(days=1))
        with self.assertRaises(InvalidToken):
            self.backend.get_validated_token(str(token))

        # Otherwise, should return validated token
        token.set_exp()
        self.assertEqual(
            self.backend.get_validated_token(str(token)).payload, token.payload
        )

    @override_api_settings(
        AUTH_TOKEN_CLASSES=("rest_framework_simplejwt.tokens.AccessToken",),
    )
    def test_get_validated_token_reject_unknown_token(self):
        # Should not accept tokens not included in AUTH_TOKEN_CLASSES
        sliding_token = SlidingToken()
        with self.assertRaises(InvalidToken) as e:
            self.backend.get_validated_token(str(sliding_token))

        messages = e.exception.detail["messages"]
        self.assertEqual(1, len(messages))
        self.assertEqual(
            {
                "token_class": "AccessToken",
                "token_type": "access",
                "message": "Token has wrong type",
            },
            messages[0],
        )

    @override_api_settings(
        AUTH_TOKEN_CLASSES=(
            "rest_framework_simplejwt.tokens.AccessToken",
            "rest_framework_simplejwt.tokens.SlidingToken",
        ),
    )
    def test_get_validated_token_accept_known_token(self):
        # Should accept tokens included in AUTH_TOKEN_CLASSES
        access_token = AccessToken()
        sliding_token = SlidingToken()

        self.backend.get_validated_token(str(access_token))
        self.backend.get_validated_token(str(sliding_token))

    def test_get_user(self):
        payload = {"some_other_id": "foo"}

        # Should raise error if no recognizable user identification
        with self.assertRaises(InvalidToken):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Should raise exception if user not found
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u = User.objects.create_user(username="markhamill")
        u.is_active = False
        u.save()

        payload[api_settings.USER_ID_CLAIM] = getattr(u, api_settings.USER_ID_FIELD)

        # Should raise exception if user is inactive
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u.is_active = True
        u.save()

        # Otherwise, should return correct user
        self.assertEqual(self.backend.get_user(payload).id, u.id)

    @override_api_settings(
        CHECK_USER_IS_ACTIVE=False,
    )
    def test_get_inactive_user(self):
        payload = {"some_other_id": "foo"}

        # Should raise error if no recognizable user identification
        with self.assertRaises(InvalidToken):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Should raise exception if user not found
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u = User.objects.create_user(username="markhamill")
        u.is_active = False
        u.save()

        payload[api_settings.USER_ID_CLAIM] = getattr(u, api_settings.USER_ID_FIELD)

        # should return correct user
        self.assertEqual(self.backend.get_user(payload).id, u.id)

    @override_api_settings(
        CHECK_REVOKE_TOKEN=True, REVOKE_TOKEN_CLAIM="revoke_token_claim"
    )
    def test_get_user_with_check_revoke_token(self):
        payload = {"some_other_id": "foo"}

        # Should raise error if no recognizable user identification
        with self.assertRaises(InvalidToken):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Should raise exception if user not found
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u = User.objects.create_user(username="markhamill")
        u.is_active = False
        u.save()

        payload[api_settings.USER_ID_CLAIM] = getattr(u, api_settings.USER_ID_FIELD)

        # Should raise exception if user is inactive
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        u.is_active = True
        u.save()

        # Should raise exception if hash password is different
        with self.assertRaises(AuthenticationFailed):
            self.backend.get_user(payload)

        if api_settings.CHECK_REVOKE_TOKEN:
            payload[api_settings.REVOKE_TOKEN_CLAIM] = get_md5_hash_password(u.password)

        # Otherwise, should return correct user
        self.assertEqual(self.backend.get_user(payload).id, u.id)

    def test_get_user_with_str_user_id_claim(self):
        """
        Verify that even though the user id is an int, it can be verified
        and retrieved if the user id claim value is a string
        """

        user = User.objects.create_user(username="testuser")
        payload = {api_settings.USER_ID_CLAIM: str(user.id)}
        auth_user = self.backend.get_user(payload)
        self.assertEqual(auth_user.id, user.id)


class TestJWTStatelessUserAuthentication(TestCase):
    def setUp(self):
        self.backend = authentication.JWTStatelessUserAuthentication()

    def test_get_user(self):
        payload = {"some_other_id": "foo"}

        # Should raise error if no recognizable user identification
        with self.assertRaises(InvalidToken):
            self.backend.get_user(payload)

        payload[api_settings.USER_ID_CLAIM] = 42

        # Otherwise, should return a token user object
        user = self.backend.get_user(payload)

        self.assertIsInstance(user, TokenUser)
        self.assertEqual(user.id, 42)

    def test_custom_tokenuser(self):
        from django.utils.functional import cached_property

        class BobSaget(TokenUser):
            @cached_property
            def username(self):
                return "bsaget"

        temp = api_settings.TOKEN_USER_CLASS
        api_settings.TOKEN_USER_CLASS = BobSaget

        # Should return a token user object
        payload = {api_settings.USER_ID_CLAIM: 42}
        user = self.backend.get_user(payload)

        self.assertIsInstance(user, api_settings.TOKEN_USER_CLASS)
        self.assertEqual(user.id, 42)
        self.assertEqual(user.username, "bsaget")

        # Restore default TokenUser for future tests
        api_settings.TOKEN_USER_CLASS = temp


class TestCookieJWTAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.backend = authentication.CookieJWTAuthentication()

    @override_api_settings(COOKIE_NAME="access")
    def test_get_cookie_names_single_string(self):
        # When COOKIE_NAME is a string, get_cookie_names should return a list of length 1
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        self.assertEqual(backend.get_cookie_names(), ["access"])

    @override_api_settings(COOKIE_NAME=["access", "jwt"])
    def test_get_cookie_names_list(self):
        # When COOKIE_NAME is an iterable, get_cookie_names should return a list with same items
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        self.assertEqual(backend.get_cookie_names(), ["access", "jwt"])

    @override_api_settings(COOKIE_NAME="access")
    def test_get_raw_token_from_cookies_no_cookie(self):
        # Should return None if no configured cookie is present
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        request = self.factory.get("/test-url/")
        self.assertIsNone(backend.get_raw_token_from_cookies(request))

    @override_api_settings(COOKIE_NAME="access")
    def test_get_raw_token_from_cookies_single_cookie(self):
        # Should return the value of the configured cookie if present
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        token = "test-token"
        request = self.factory.get("/test-url/")
        request.COOKIES["access"] = token

        self.assertEqual(backend.get_raw_token_from_cookies(request), token)

    @override_api_settings(COOKIE_NAME=["access", "jwt"])
    def test_get_raw_token_from_cookies_multiple_cookies_first_non_empty(self):
        # Should return the first non-empty token based on COOKIE_NAME order
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        request = self.factory.get("/test-url/")
        # First cookie is empty, second has token
        request.COOKIES["access"] = ""
        request.COOKIES["jwt"] = "real-token"

        self.assertEqual(
            backend.get_raw_token_from_cookies(request),
            "real-token",
        )

    @override_api_settings(COOKIE_NAME=["access", "jwt"])
    def test_get_raw_token_from_cookies_ignores_unconfigured_cookies(self):
        # Should not read cookies that are not in COOKIE_NAME
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        request = self.factory.get("/test-url/")
        request.COOKIES["other"] = "other-token"

        self.assertIsNone(backend.get_raw_token_from_cookies(request))

    @override_api_settings(COOKIE_NAME="access")
    def test_authenticate_returns_none_when_no_cookie(self):
        # authenticate should return None when no configured cookie is present
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()
        request = self.factory.get("/test-url/")

        self.assertIsNone(backend.authenticate(request))

    @override_api_settings(COOKIE_NAME="access")
    def test_authenticate_with_valid_token_in_cookie(self):
        # Should authenticate and return (user, validated_token) when cookie contains a valid token
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()

        user = User.objects.create_user(username="cookieuser")
        access_token = AccessToken.for_user(user)

        request = self.factory.get("/test-url/")
        request.COOKIES["access"] = str(access_token)

        user_obj, validated_token = backend.authenticate(request)

        self.assertEqual(user_obj.id, user.id)
        self.assertEqual(validated_token.payload, access_token.payload)

    @override_api_settings(COOKIE_NAME="access")
    def test_authenticate_with_invalid_token_in_cookie(self):
        # Should raise InvalidToken if cookie contains an invalid token
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()

        request = self.factory.get("/test-url/")
        request.COOKIES["access"] = "not-a-real-token"

        with self.assertRaises(InvalidToken):
            backend.authenticate(request)

    @override_api_settings(COOKIE_NAME=["access", "jwt"])
    def test_authenticate_uses_first_non_empty_cookie(self):
        # When multiple cookie names are configured, authenticate should use
        # the first non-empty one and ignore the others
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()

        primary_user = User.objects.create_user(username="primary")
        secondary_user = User.objects.create_user(username="secondary")

        primary_token = AccessToken.for_user(primary_user)
        secondary_token = AccessToken.for_user(secondary_user)

        request = self.factory.get("/test-url/")
        # Order: ["access", "jwt"]
        request.COOKIES["access"] = str(primary_token)
        request.COOKIES["jwt"] = str(secondary_token)

        user_obj, validated_token = backend.authenticate(request)

        self.assertEqual(user_obj.id, primary_user.id)
        self.assertEqual(validated_token.payload, primary_token.payload)

    @override_api_settings(COOKIE_NAME=["access", "jwt"])
    def test_authenticate_skips_empty_first_cookie(self):
        # If the first cookie is empty, it should fall back to the next one
        reload(authentication)
        backend = authentication.CookieJWTAuthentication()

        user = User.objects.create_user(username="fallback")
        token = AccessToken.for_user(user)

        request = self.factory.get("/test-url/")
        request.COOKIES["access"] = ""
        request.COOKIES["jwt"] = str(token)

        user_obj, validated_token = backend.authenticate(request)

        self.assertEqual(user_obj.id, user.id)
        self.assertEqual(validated_token.payload, token.payload)
