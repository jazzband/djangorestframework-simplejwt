from datetime import timedelta
from importlib import reload
from unittest.mock import MagicMock, patch
from freezegun import freeze_time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import exceptions as drf_exceptions
from rest_framework.serializers import ValidationError

from rest_framework_simplejwt.exceptions import (
    TokenError,
    TokenFamilyNotConfigured,
    RefreshTokenBlacklistedError
    )
from rest_framework_simplejwt.serializers import (
    TokenBlacklistSerializer,
    TokenObtainPairSerializer,
    TokenObtainSerializer,
    TokenObtainSlidingSerializer,
    TokenRefreshSerializer,
    TokenRefreshSlidingSerializer,
    TokenVerifySerializer,
    TokenFamilyBlacklistSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.token_family.models import (
    TokenFamily,
    BlacklistedTokenFamily,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, SlidingToken
from rest_framework_simplejwt.utils import (
    aware_utcnow,
    datetime_from_epoch,
    datetime_to_epoch,
)

from .utils import override_api_settings

User = get_user_model()


class TestTokenObtainSerializer(TestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_not_validate_if_any_fields_missing(self):
        s = TokenObtainSerializer(data={})
        self.assertFalse(s.is_valid())
        self.assertIn(s.username_field, s.errors)
        self.assertIn("password", s.errors)

        s = TokenObtainSerializer(
            data={
                TokenObtainSerializer.username_field: "oieanrst",
            }
        )
        self.assertFalse(s.is_valid())
        self.assertIn("password", s.errors)

        s = TokenObtainSerializer(
            data={
                "password": "oieanrst",
            }
        )
        self.assertFalse(s.is_valid())
        self.assertIn(s.username_field, s.errors)

    def test_it_should_not_validate_if_user_not_found(self):
        s = TokenObtainSerializer(
            context=MagicMock(),
            data={
                TokenObtainSerializer.username_field: "missing",
                "password": "pass",
            },
        )

        with self.assertRaises(drf_exceptions.AuthenticationFailed):
            s.is_valid()

    def test_it_should_pass_validate_if_request_not_in_context(self):
        s = TokenObtainSerializer(
            context={},
            data={
                "username": self.username,
                "password": self.password,
            },
        )

        s.is_valid()

    def test_it_should_raise_if_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        s = TokenObtainSerializer(
            context=MagicMock(),
            data={
                TokenObtainSerializer.username_field: self.username,
                "password": self.password,
            },
        )

        with self.assertRaises(drf_exceptions.AuthenticationFailed):
            s.is_valid()

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "django.contrib.auth.backends.AllowAllUsersModelBackend",
            "django.contrib.auth.backends.ModelBackend",
        ]
    )
    @override_api_settings(
        CHECK_USER_IS_ACTIVE=False,
    )
    def test_it_should_validate_if_user_inactive_but_rule_allows(self):
        self.user.is_active = False
        self.user.save()

        s = TokenObtainSerializer(
            context=MagicMock(),
            data={
                TokenObtainSerializer.username_field: self.username,
                "password": self.password,
            },
        )

        self.assertTrue(s.is_valid())


class TestTokenObtainSlidingSerializer(TestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_produce_a_json_web_token_when_valid(self):
        s = TokenObtainSlidingSerializer(
            context=MagicMock(),
            data={
                TokenObtainSlidingSerializer.username_field: self.username,
                "password": self.password,
            },
        )

        self.assertTrue(s.is_valid())
        self.assertIn("token", s.validated_data)

        # Expecting token type claim to be correct for sliding token.  If this
        # is the case, instantiating a `SlidingToken` instance with encoded
        # token should not raise an exception.
        SlidingToken(s.validated_data["token"])


class TestTokenObtainPairSerializer(TestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_produce_a_json_web_token_when_valid(self):
        s = TokenObtainPairSerializer(
            context=MagicMock(),
            data={
                TokenObtainPairSerializer.username_field: self.username,
                "password": self.password,
            },
        )

        self.assertTrue(s.is_valid())
        self.assertIn("access", s.validated_data)
        self.assertIn("refresh", s.validated_data)

        # Expecting token type claim to be correct for both tokens.  If this is
        # the case, instantiating appropriate token subclass instances with
        # encoded tokens should not raise an exception.
        AccessToken(s.validated_data["access"])
        RefreshToken(s.validated_data["refresh"])


class TestTokenRefreshSlidingSerializer(TestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_not_validate_if_token_invalid(self):
        token = SlidingToken()
        del token["exp"]

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("has no 'exp' claim", e.exception.args[0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("expired", e.exception.args[0])

    def test_it_should_raise_token_error_if_token_has_no_refresh_exp_claim(self):
        token = SlidingToken()
        del token[api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM]

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn(
            f"has no '{api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM}' claim",
            e.exception.args[0],
        )

    def test_it_should_raise_token_error_if_token_has_refresh_period_expired(self):
        token = SlidingToken()
        token.set_exp(
            api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM, lifetime=-timedelta(days=1)
        )

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn(
            "'{}' claim has expired".format(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM
            ),
            e.exception.args[0],
        )

    def test_it_should_raise_token_error_if_token_has_wrong_type(self):
        token = SlidingToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("wrong type", e.exception.args[0])

    def test_it_should_update_token_exp_claim_if_everything_ok(self):
        old_token = SlidingToken()

        lifetime = api_settings.SLIDING_TOKEN_LIFETIME - timedelta(seconds=1)
        old_exp = old_token.current_time + lifetime

        old_token.set_exp(lifetime=lifetime)

        # Serializer validates
        s = TokenRefreshSlidingSerializer(data={"token": str(old_token)})
        self.assertTrue(s.is_valid())

        # Expiration claim has moved into future
        new_token = SlidingToken(s.validated_data["token"])
        new_exp = datetime_from_epoch(new_token["exp"])

        self.assertTrue(old_exp < new_exp)

    def test_it_should_raise_error_for_deleted_users(self):
        token = SlidingToken.for_user(self.user)
        self.user.delete()

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        # It should raise AuthenticationFailed instead of ObjectDoesNotExist
        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid()

        self.assertEqual(e.exception.get_codes(), "no_active_account")

    def test_it_should_raise_error_for_inactive_users(self):
        token = SlidingToken.for_user(self.user)
        self.user.is_active = False
        self.user.save()

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid()

        self.assertEqual(e.exception.get_codes(), "no_active_account")

    @override_api_settings(
        CHECK_REVOKE_TOKEN=True,
        REVOKE_TOKEN_CLAIM="hash_password",
        BLACKLIST_AFTER_ROTATION=False,
    )
    def test_sliding_token_should_fail_after_password_change(self):
        """
        Tests that sliding token refresh fails if CHECK_REVOKE_TOKEN is True and the
        user's password has changed.
        """
        token = SlidingToken.for_user(self.user)
        self.user.set_password("new_password")
        self.user.save()

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})

        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid(raise_exception=True)

        self.assertEqual(e.exception.get_codes(), "password_changed")

    @override_api_settings(
        CHECK_REVOKE_TOKEN=True,
        REVOKE_TOKEN_CLAIM="hash_password",
        BLACKLIST_AFTER_ROTATION=True,
    )
    def test_sliding_token_should_blacklist_after_password_change(self):
        """
        Tests that if sliding token refresh fails due to a password change, the
        offending token is blacklisted.
        """
        token = SlidingToken.for_user(self.user)
        self.user.set_password("new_password")
        self.user.save()

        s = TokenRefreshSlidingSerializer(data={"token": str(token)})
        with self.assertRaises(drf_exceptions.AuthenticationFailed):
            s.is_valid(raise_exception=True)

        # Check that the token is now in the blacklist
        jti = token[api_settings.JTI_CLAIM]
        self.assertTrue(OutstandingToken.objects.filter(jti=jti).exists())
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=jti).exists())


class TestTokenRefreshSerializer(TestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_password"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_it_should_raise_error_for_deleted_users(self):
        refresh = RefreshToken.for_user(self.user)
        self.user.delete()

        s = TokenRefreshSerializer(data={"refresh": str(refresh)})

        # It should raise AuthenticationFailed instead of ObjectDoesNotExist
        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid()

        self.assertEqual(e.exception.get_codes(), "no_active_account")

    def test_it_should_raise_error_for_inactive_users(self):
        refresh = RefreshToken.for_user(self.user)
        self.user.is_active = False
        self.user.save()

        s = TokenRefreshSerializer(data={"refresh": str(refresh)})

        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid()

        self.assertIn("No active account", e.exception.args[0])

    def test_it_should_return_access_token_for_active_users(self):
        refresh = RefreshToken.for_user(self.user)

        s = TokenRefreshSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2
        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            s.is_valid()

        access = AccessToken(s.validated_data["access"])

        self.assertEqual(
            access["exp"], datetime_to_epoch(now + api_settings.ACCESS_TOKEN_LIFETIME)
        )

    def test_it_should_raise_token_error_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        s = TokenRefreshSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("has no 'exp' claim", e.exception.args[0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenRefreshSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("expired", e.exception.args[0])

    def test_it_should_raise_token_error_if_token_has_wrong_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"

        s = TokenRefreshSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("wrong type", e.exception.args[0])

    def test_it_should_return_access_token_if_everything_ok(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # Serializer validates
        s = TokenRefreshSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(s.is_valid())

        access = AccessToken(s.validated_data["access"])

        self.assertEqual(refresh["test_claim"], access["test_claim"])
        self.assertEqual(
            access["exp"], datetime_to_epoch(now + api_settings.ACCESS_TOKEN_LIFETIME)
        )

    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=False,
    )
    def test_it_should_return_refresh_token_if_tokens_should_be_rotated(self):
        refresh = RefreshToken()

        refresh["test_claim"] = "arst"

        old_jti = refresh["jti"]
        old_exp = refresh["exp"]

        # Serializer validates
        ser = TokenRefreshSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(ser.is_valid())

        access = AccessToken(ser.validated_data["access"])
        new_refresh = RefreshToken(ser.validated_data["refresh"])

        self.assertEqual(refresh["test_claim"], access["test_claim"])
        self.assertEqual(refresh["test_claim"], new_refresh["test_claim"])

        self.assertNotEqual(old_jti, new_refresh["jti"])
        self.assertNotEqual(old_exp, new_refresh["exp"])

        self.assertEqual(
            access["exp"], datetime_to_epoch(now + api_settings.ACCESS_TOKEN_LIFETIME)
        )
        self.assertEqual(
            new_refresh["exp"],
            datetime_to_epoch(now + api_settings.REFRESH_TOKEN_LIFETIME),
        )

    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=True,
    )
    def test_it_should_blacklist_refresh_token_if_tokens_should_be_rotated_and_blacklisted(
        self,
    ):
        self.assertEqual(OutstandingToken.objects.count(), 0)
        self.assertEqual(BlacklistedToken.objects.count(), 0)

        refresh = RefreshToken()

        refresh["test_claim"] = "arst"

        old_jti = refresh["jti"]
        old_exp = refresh["exp"]

        # Serializer validates
        ser = TokenRefreshSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(ser.is_valid())

        access = AccessToken(ser.validated_data["access"])
        new_refresh = RefreshToken(ser.validated_data["refresh"])

        self.assertEqual(refresh["test_claim"], access["test_claim"])
        self.assertEqual(refresh["test_claim"], new_refresh["test_claim"])

        self.assertNotEqual(old_jti, new_refresh["jti"])
        self.assertNotEqual(old_exp, new_refresh["exp"])

        self.assertEqual(
            access["exp"], datetime_to_epoch(now + api_settings.ACCESS_TOKEN_LIFETIME)
        )
        self.assertEqual(
            new_refresh["exp"],
            datetime_to_epoch(now + api_settings.REFRESH_TOKEN_LIFETIME),
        )

        self.assertEqual(OutstandingToken.objects.count(), 2)
        self.assertEqual(BlacklistedToken.objects.count(), 1)

        # Assert old refresh token is blacklisted
        self.assertEqual(BlacklistedToken.objects.first().token.jti, old_jti)

    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=True,
    )
    def test_blacklist_app_not_installed_should_pass(self):
        from rest_framework_simplejwt import serializers, tokens

        # Remove blacklist app
        new_apps = list(settings.INSTALLED_APPS)
        new_apps.remove("rest_framework_simplejwt.token_blacklist")

        with self.settings(INSTALLED_APPS=tuple(new_apps)):
            # Reload module that blacklist app not installed
            reload(tokens)
            reload(serializers)

            refresh = tokens.RefreshToken()

            # Serializer validates
            ser = serializers.TokenRefreshSerializer(data={"refresh": str(refresh)})
            ser.validate({"refresh": str(refresh)})

        # Restore origin module without mock
        reload(tokens)
        reload(serializers)

    @override_api_settings(
        CHECK_REVOKE_TOKEN=True,
        REVOKE_TOKEN_CLAIM="hash_password",
        BLACKLIST_AFTER_ROTATION=False,
    )
    def test_refresh_token_should_fail_after_password_change(self):
        """
        Tests that token refresh fails if CHECK_REVOKE_TOKEN is True and the
        user's password has changed.
        """
        refresh = RefreshToken.for_user(self.user)
        self.user.set_password("new_password")
        self.user.save()

        s = TokenRefreshSerializer(data={"refresh": str(refresh)})

        with self.assertRaises(drf_exceptions.AuthenticationFailed) as e:
            s.is_valid(raise_exception=True)

        self.assertEqual(e.exception.get_codes(), "password_changed")

    @override_api_settings(
        CHECK_REVOKE_TOKEN=True,
        REVOKE_TOKEN_CLAIM="hash_password",
        BLACKLIST_AFTER_ROTATION=True,
    )
    def test_refresh_token_should_blacklist_after_password_change(self):
        """
        Tests that if token refresh fails due to a password change, the
        offending refresh token is blacklisted.
        """
        refresh = RefreshToken.for_user(self.user)
        self.user.set_password("new_password")
        self.user.save()

        s = TokenRefreshSerializer(data={"refresh": str(refresh)})
        with self.assertRaises(drf_exceptions.AuthenticationFailed):
            s.is_valid(raise_exception=True)

        # Check that the token is now in the blacklist
        jti = refresh[api_settings.JTI_CLAIM]
        self.assertTrue(OutstandingToken.objects.filter(jti=jti).exists())
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=jti).exists())

    
    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=True,
        TOKEN_FAMILY_BLACKLIST_ON_REUSE=True,
        )
    def test_family_blacklisting_on_refresh_token_reuse_is_enabled(self):
        """ 
        Tests that the token family is blacklisted upon refresh token reuse.

        If a refresh token has been rotated and subsequently added to the
        blacklist, attempting to use that same original token again should
        be detected as reuse. This reuse detection should then cause its
        associated token family to be added to the BlacklistedTokenFamily model.
        """
        refresh = RefreshToken()
        refresh.payload[api_settings.TOKEN_FAMILY_CLAIM] = "random string"

        ser = TokenRefreshSerializer(data={"refresh": str(refresh)})
        ser.validate({"refresh": str(refresh)})

        with self.assertRaises(RefreshTokenBlacklistedError) as e:
            ser.validate({"refresh": str(refresh)})

        self.assertIn("blacklisted", e.exception.args[0])

        qs = BlacklistedTokenFamily.objects.filter(family__family_id = "random string")

        self.assertEqual(qs.count(), 1)

    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=True,
        TOKEN_FAMILY_BLACKLIST_ON_REUSE=False,
        )
    def test_family_blacklisting_on_refresh_token_reuse_is_disabled(self):
        """
        Tests that refresh token reuse is detected, but the token family
        is not added to the blacklist because the option for that is disabled.

        When a refresh token is reused and the TOKEN_FAMILY_BLACKLIST_ON_REUSE
        setting is False, the reuse should be detected (raising the standard
        blacklisted token error), but the token's associated family should NOT
        be added to the BlacklistedTokenFamily model.
        """
        refresh = RefreshToken()
        refresh.payload[api_settings.TOKEN_FAMILY_CLAIM] = "random string"

        ser = TokenRefreshSerializer(data={"refresh": str(refresh)})
        ser.validate({"refresh": str(refresh)})

        with self.assertRaises(RefreshTokenBlacklistedError) as e:
            ser.validate({"refresh": str(refresh)})

        self.assertIn("blacklisted", e.exception.args[0])

        qs = BlacklistedTokenFamily.objects.all()

        self.assertEqual(qs.count(), 0)

    @override_api_settings(
        ROTATE_REFRESH_TOKENS=True,
        BLACKLIST_AFTER_ROTATION=True,
        TOKEN_FAMILY_BLACKLIST_ON_REUSE=False,
        )
    def test_family_blacklisting_on_token_reuse_is_enabled_but_token_has_no_family_id(self):
        """
        Ensures that no error is raised and no family is blacklisted when a reused token lacks a family ID.

        This simulates the case where a token was issued before the token family feature was enabled.
        Such tokens are still considered valid and should not trigger family-level blacklisting.
        """
        # token has no family id
        refresh = RefreshToken()

        ser = TokenRefreshSerializer(data={"refresh": str(refresh)})
        ser.validate({"refresh": str(refresh)})

        self.assertEqual(BlacklistedToken.objects.all().count(), 1)
        self.assertEqual(BlacklistedTokenFamily.objects.all().count(), 0)

    @override_api_settings(
        TOKEN_FAMILY_LIFETIME= timedelta(minutes=30)
        )
    def test_raises_token_error_if_token_family_is_expired(self):

        with freeze_time(aware_utcnow() - timedelta(minutes= 30)):
            token = RefreshToken()
            fam_exp = datetime_to_epoch(aware_utcnow())
            token.payload[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM] = fam_exp

        ser = TokenRefreshSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0]) 
        self.assertIn("expired", e.exception.args[0])

    def test_raises_token_error_if_token_family_is_blacklisted(self):
        token = RefreshToken()
        token.payload[api_settings.TOKEN_FAMILY_CLAIM] =  "random string"
        token.blacklist_family()

        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            1
        )

        ser = TokenRefreshSerializer(data={"refresh": str(token)})
        
        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0])
        self.assertIn("blacklisted", e.exception.args[0])


class TestTokenVerifySerializer(TestCase):
    def test_it_should_raise_token_error_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        s = TokenVerifySerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("has no 'exp' claim", e.exception.args[0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenVerifySerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("expired", e.exception.args[0])

    def test_it_should_not_raise_token_error_if_token_has_wrong_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"
                
        s = TokenVerifySerializer(data={"token": str(token)})

        self.assertTrue(s.is_valid())

    def test_it_should_return_given_token_if_everything_ok(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # Serializer validates
        s = TokenVerifySerializer(data={"token": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(s.is_valid())

        self.assertEqual(len(s.validated_data), 0)

    @override_api_settings(
        TOKEN_FAMILY_LIFETIME= timedelta(minutes=30)
        )
    def test_raises_token_error_if_token_family_is_expired(self):

        with freeze_time(aware_utcnow() - timedelta(minutes= 30)):
            token = RefreshToken()
            fam_exp = datetime_to_epoch(aware_utcnow())
            token.payload[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM] = fam_exp

        ser = TokenVerifySerializer(data={"token": str(token)})

        with self.assertRaises(TokenError) as e:
            ser.validate({"token": str(token)})
        
        self.assertIn("family", e.exception.args[0]) 
        self.assertIn("expired", e.exception.args[0])
        
    def test_raises_token_error_if_token_family_is_blacklisted(self):
        token = RefreshToken()
        token.payload[api_settings.TOKEN_FAMILY_CLAIM] =  "random string"
        token.blacklist_family()

        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            1
        )

        ser = TokenVerifySerializer(data={"token": str(token)})
        
        with self.assertRaises(TokenError) as e:
            ser.validate({"token": str(token)})
        
        self.assertIn("family", e.exception.args[0])
        self.assertIn("blacklisted", e.exception.args[0])


class TestTokenBlacklistSerializer(TestCase):
    def test_it_should_raise_token_error_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        s = TokenBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("has no 'exp' claim", e.exception.args[0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("expired", e.exception.args[0])

    def test_it_should_raise_token_error_if_token_has_wrong_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"

        s = TokenBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("wrong type", e.exception.args[0])

    def test_it_should_return_nothing_if_everything_ok(self):
        refresh = RefreshToken()
        refresh["test_claim"] = "arst"

        # Serializer validates
        s = TokenBlacklistSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(s.is_valid())

        self.assertDictEqual(s.validated_data, {})

    def test_it_should_blacklist_refresh_token_if_everything_ok(self):
        self.assertEqual(OutstandingToken.objects.count(), 0)
        self.assertEqual(BlacklistedToken.objects.count(), 0)

        refresh = RefreshToken()

        refresh["test_claim"] = "arst"

        old_jti = refresh["jti"]

        # Serializer validates
        ser = TokenBlacklistSerializer(data={"refresh": str(refresh)})

        now = aware_utcnow() - api_settings.ACCESS_TOKEN_LIFETIME / 2

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = now
            self.assertTrue(ser.is_valid())

        self.assertEqual(OutstandingToken.objects.count(), 1)
        self.assertEqual(BlacklistedToken.objects.count(), 1)

        # Assert old refresh token is blacklisted
        self.assertEqual(BlacklistedToken.objects.first().token.jti, old_jti)

    def test_blacklist_app_not_installed_should_pass(self):
        from rest_framework_simplejwt import serializers, tokens

        # Remove blacklist app
        new_apps = list(settings.INSTALLED_APPS)
        new_apps.remove("rest_framework_simplejwt.token_blacklist")

        with self.settings(INSTALLED_APPS=tuple(new_apps)):
            # Reload module that blacklist app not installed
            reload(tokens)
            reload(serializers)

            refresh = tokens.RefreshToken()

            # Serializer validates
            ser = serializers.TokenBlacklistSerializer(data={"refresh": str(refresh)})
            ser.validate({"refresh": str(refresh)})

        # Restore origin module without mock
        reload(tokens)
        reload(serializers)

    @override_api_settings(
        TOKEN_FAMILY_LIFETIME= timedelta(minutes=30)
        )
    def test_raises_token_error_if_token_family_is_expired(self):

        with freeze_time(aware_utcnow() - timedelta(minutes= 30)):
            token = RefreshToken()
            fam_exp = datetime_to_epoch(aware_utcnow())
            token.payload[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM] = fam_exp

        ser = TokenBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0]) 
        self.assertIn("expired", e.exception.args[0])

    def test_raises_token_error_if_token_family_is_blacklisted(self):
        token = RefreshToken()
        token.payload[api_settings.TOKEN_FAMILY_CLAIM] =  "random string"
        token.blacklist_family()

        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            1
        )

        ser = TokenBlacklistSerializer(data={"refresh": str(token)})
        
        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0])
        self.assertIn("blacklisted", e.exception.args[0])


class TestTokenFamilyBlacklistSerializer(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_it_should_raise_token_error_if_token_invalid(self):
        token = RefreshToken()
        del token["exp"]

        s = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("has no 'exp' claim", e.exception.args[0])

        token.set_exp(lifetime=-timedelta(days=1))

        s = TokenBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("expired", e.exception.args[0])

    def test_it_should_raise_token_error_if_token_has_wrong_type(self):
        token = RefreshToken()
        token[api_settings.TOKEN_TYPE_CLAIM] = "wrong_type"

        s = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            s.is_valid()

        self.assertIn("wrong type", e.exception.args[0])

    @override_api_settings(TOKEN_FAMILY_ENABLED= True)
    def test_it_should_raise_token_family_not_confgured_if_family_app_is_not_installed(self):
        from rest_framework_simplejwt import serializers, tokens

        # Remove family app
        new_apps = list(settings.INSTALLED_APPS)
        new_apps.remove("rest_framework_simplejwt.token_family")

        with self.settings(INSTALLED_APPS=tuple(new_apps)):
            # Reload module that blacklist app not installed
            reload(tokens)
            reload(serializers)

            token = tokens.RefreshToken()
            token[api_settings.TOKEN_FAMILY_CLAIM] = "random string"

            # Serializer validates
            ser = serializers.TokenFamilyBlacklistSerializer(data={"refresh": str(token)})

            with self.assertRaises(TokenFamilyNotConfigured) as e:
                ser.validate({"refresh": str(token)})

        # Restore origin module without mock
        reload(tokens)
        reload(serializers)        

    def test_it_should_raise_token_family_not_confgured_if_family_setting_is_disable(self):
        """ the default value of the setting TOKEN_FAMILY_ENABLED is False """
        from rest_framework_simplejwt import tokens, serializers

        with override_api_settings(TOKEN_FAMILY_ENABLED=False):
            reload(tokens)
            reload(serializers)

            token = tokens.RefreshToken()
            token[api_settings.TOKEN_FAMILY_CLAIM] = "random string"

            # Serializer validates
            ser = serializers.TokenFamilyBlacklistSerializer(data={"refresh": str(token)})

            with self.assertRaises(TokenFamilyNotConfigured) as e:
                ser.validate({"refresh": str(token)})

        # restore origin modules 
        with override_api_settings(TOKEN_FAMILY_ENABLED=True):
            reload(tokens)
            reload(serializers)

    def test_raises_validation_error_if_token_has_no_family_id_in_payload(self):
        refresh = RefreshToken.for_user(self.user)
        del refresh.payload[api_settings.TOKEN_FAMILY_CLAIM]

        ser = TokenFamilyBlacklistSerializer(data={"refresh": str(refresh)})
        
        with self.assertRaises(ValidationError) as e:
            ser.validate({"refresh": str(refresh)})
    
    @override_api_settings(
        TOKEN_FAMILY_LIFETIME= timedelta(minutes=30)
        )
    def test_raises_token_error_if_family_is_expired(self):

        with freeze_time(aware_utcnow() - timedelta(minutes= 30)):
            token = RefreshToken.for_user(self.user)

        ser = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})

        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0])
        self.assertIn("expired", e.exception.args[0])

    def test_it_should_blacklist_family_if_everything_is_ok(self):
        token = RefreshToken.for_user(self.user)
        ser = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})
        ser.is_valid()

        qs = BlacklistedTokenFamily.objects.filter(family__family_id= token.get_family_id())

        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), 1)

    def test_raises_token_error_if_family_is_blacklisted(self):
        token = RefreshToken.for_user(self.user)
        token.blacklist_family()

        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            1
        )

        ser = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})
        
        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("family", e.exception.args[0])
        self.assertIn("blacklisted", e.exception.args[0])

    def test_raises_token_error_if_token_is_blacklisted(self):
        token = RefreshToken.for_user(self.user)
        token.blacklist()

        self.assertEqual(
            BlacklistedToken.objects.all().count(),
            1
        )

        ser = TokenFamilyBlacklistSerializer(data={"refresh": str(token)})
        
        with self.assertRaises(TokenError) as e:
            ser.validate({"refresh": str(token)})
        
        self.assertIn("blacklisted", e.exception.args[0])
        