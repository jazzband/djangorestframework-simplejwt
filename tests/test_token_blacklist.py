from importlib import reload
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import BigAutoField
from django.test import TestCase
from django.utils import timezone

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, SlidingToken
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch

from .utils import MigrationTestCase, override_api_settings


class TestTokenBlacklist(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
        )

    def test_token_blacklist_old_django(self):
        with patch("django.VERSION", (3, 1)):
            # Import package mock blacklist old django
            import rest_framework_simplejwt.token_blacklist.__init__ as blacklist

            self.assertEqual(
                blacklist.default_app_config,
                ("rest_framework_simplejwt.token_blacklist.apps.TokenBlacklistConfig"),
            )

        # Restore origin module without mock
        reload(blacklist)

    def test_sliding_tokens_are_added_to_outstanding_list(self):
        token = SlidingToken.for_user(self.user)

        qs = OutstandingToken.objects.all()
        outstanding_token = qs.first()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(outstanding_token.user, self.user)
        self.assertEqual(outstanding_token.jti, token["jti"])
        self.assertEqual(outstanding_token.token, str(token))
        self.assertEqual(outstanding_token.created_at, token.current_time)
        self.assertEqual(
            outstanding_token.expires_at, datetime_from_epoch(token["exp"])
        )

    def test_refresh_tokens_are_added_to_outstanding_list(self):
        token = RefreshToken.for_user(self.user)

        qs = OutstandingToken.objects.all()
        outstanding_token = qs.first()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(outstanding_token.user, self.user)
        self.assertEqual(outstanding_token.jti, token["jti"])
        self.assertEqual(outstanding_token.token, str(token))
        self.assertEqual(outstanding_token.created_at, token.current_time)
        self.assertEqual(
            outstanding_token.expires_at, datetime_from_epoch(token["exp"])
        )

    def test_access_tokens_are_not_added_to_outstanding_list(self):
        AccessToken.for_user(self.user)

        qs = OutstandingToken.objects.all()

        self.assertFalse(qs.exists())

    def test_token_will_not_validate_if_blacklisted(self):
        token = RefreshToken.for_user(self.user)
        outstanding_token = OutstandingToken.objects.first()

        # Should raise no exception
        RefreshToken(str(token))

        # Add token to blacklist
        BlacklistedToken.objects.create(token=outstanding_token)

        with self.assertRaises(TokenError) as e:
            # Should raise exception
            RefreshToken(str(token))
            self.assertIn("blacklisted", e.exception.args[0])

    def test_tokens_can_be_manually_blacklisted(self):
        token = RefreshToken.for_user(self.user)

        # Should raise no exception
        RefreshToken(str(token))

        self.assertEqual(OutstandingToken.objects.count(), 1)

        # Add token to blacklist
        blacklisted_token, created = token.blacklist()

        # Should not add token to outstanding list if already present
        self.assertEqual(OutstandingToken.objects.count(), 1)

        # Should return blacklist record and boolean to indicate creation
        self.assertEqual(blacklisted_token.token.jti, token["jti"])
        self.assertTrue(created)

        with self.assertRaises(TokenError) as e:
            # Should raise exception
            RefreshToken(str(token))
            self.assertIn("blacklisted", e.exception.args[0])

        # If blacklisted token already exists, indicate no creation through
        # boolean
        blacklisted_token, created = token.blacklist()
        self.assertEqual(blacklisted_token.token.jti, token["jti"])
        self.assertFalse(created)

        # Should add token to outstanding list if not already present
        new_token = RefreshToken()
        blacklisted_token, created = new_token.blacklist()
        self.assertEqual(blacklisted_token.token.jti, new_token["jti"])
        self.assertTrue(created)

        self.assertEqual(OutstandingToken.objects.count(), 2)

    def test_outstanding_token_and_blacklisted_token_expected_str(self):
        outstanding = OutstandingToken.objects.create(
            user=self.user,
            jti="abc",
            token="xyz",
            expires_at=timezone.now(),
        )
        blacklisted = BlacklistedToken.objects.create(token=outstanding)

        expected_outstanding_str = "Token for {} ({})".format(
            outstanding.user, outstanding.jti
        )
        expected_blacklisted_str = f"Blacklisted token for {blacklisted.token.user}"

        self.assertEqual(str(outstanding), expected_outstanding_str)
        self.assertEqual(str(blacklisted), expected_blacklisted_str)

    def test_outstanding_token_and_blacklisted_token_created_at(self):
        token = RefreshToken.for_user(self.user)

        token.blacklist()
        outstanding_token = OutstandingToken.objects.get(token=token)
        self.assertEqual(outstanding_token.created_at, token.current_time)

    def test_outstanding_token_and_blacklisted_token_user(self):
        token = RefreshToken.for_user(self.user)

        token.blacklist()
        outstanding_token = OutstandingToken.objects.get(token=token)
        self.assertEqual(outstanding_token.user, self.user)

    @override_api_settings(USER_ID_FIELD="email", USER_ID_CLAIM="email")
    def test_outstanding_token_and_blacklisted_token_created_at_with_modified_user_id_field(
        self,
    ):
        token = RefreshToken.for_user(self.user)

        token.blacklist()
        outstanding_token = OutstandingToken.objects.get(token=token)
        self.assertEqual(outstanding_token.created_at, token.current_time)

    @override_api_settings(USER_ID_FIELD="email", USER_ID_CLAIM="email")
    def test_outstanding_token_and_blacklisted_token_user_with_modifed_user_id_field(
        self,
    ):
        token = RefreshToken.for_user(self.user)

        token.blacklist()
        outstanding_token = OutstandingToken.objects.get(token=token)
        self.assertEqual(outstanding_token.user, self.user)

    @override_api_settings(USER_ID_FIELD="email", USER_ID_CLAIM="email")
    def test_outstanding_token_with_deleted_user_and_modifed_user_id_field(self):
        self.assertFalse(BlacklistedToken.objects.exists())
        token = RefreshToken.for_user(self.user)
        self.user.delete()
        token.blacklist()
        self.assertTrue(BlacklistedToken.objects.count(), 1)


class TestTokenBlacklistFlushExpiredTokens(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
        )

    def test_it_should_delete_any_expired_tokens(self):
        # Make some tokens that won't expire soon
        not_expired_1 = RefreshToken.for_user(self.user)
        not_expired_2 = RefreshToken.for_user(self.user)
        not_expired_3 = RefreshToken()

        # Blacklist fresh tokens
        not_expired_2.blacklist()
        not_expired_3.blacklist()

        # Make tokens with fake exp time that will expire soon
        fake_now = aware_utcnow() - api_settings.REFRESH_TOKEN_LIFETIME

        with patch("rest_framework_simplejwt.tokens.aware_utcnow") as fake_aware_utcnow:
            fake_aware_utcnow.return_value = fake_now
            expired_1 = RefreshToken.for_user(self.user)
            expired_2 = RefreshToken()

        # Blacklist expired tokens
        expired_1.blacklist()
        expired_2.blacklist()

        # Make another token that won't expire soon
        not_expired_4 = RefreshToken.for_user(self.user)

        # Should be certain number of outstanding tokens and blacklisted
        # tokens
        self.assertEqual(OutstandingToken.objects.count(), 6)
        self.assertEqual(BlacklistedToken.objects.count(), 4)

        call_command("flushexpiredtokens")

        # Expired outstanding *and* blacklisted tokens should be gone
        self.assertEqual(OutstandingToken.objects.count(), 4)
        self.assertEqual(BlacklistedToken.objects.count(), 2)

        self.assertEqual(
            [i.jti for i in OutstandingToken.objects.order_by("id")],
            [
                not_expired_1["jti"],
                not_expired_2["jti"],
                not_expired_3["jti"],
                not_expired_4["jti"],
            ],
        )
        self.assertEqual(
            [i.token.jti for i in BlacklistedToken.objects.order_by("id")],
            [not_expired_2["jti"], not_expired_3["jti"]],
        )

    def test_token_blacklist_will_not_be_removed_on_User_delete(self):
        token = RefreshToken.for_user(self.user)
        outstanding_token = OutstandingToken.objects.first()

        # Should raise no exception
        RefreshToken(str(token))

        # Add token to blacklist
        BlacklistedToken.objects.create(token=outstanding_token)

        with self.assertRaises(TokenError) as e:
            # Should raise exception
            RefreshToken(str(token))
            self.assertIn("blacklisted", e.exception.args[0])

        # Delete the User and try again
        self.user.delete()

        with self.assertRaises(TokenError) as e:
            # Should raise exception
            RefreshToken(str(token))
            self.assertIn("blacklisted", e.exception.args[0])


class TestPopulateJtiHexMigration(MigrationTestCase):
    migrate_from = ("token_blacklist", "0002_outstandingtoken_jti_hex")
    migrate_to = ("token_blacklist", "0003_auto_20171017_2007")

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
        )

        super().setUp()

    def setUpBeforeMigration(self, apps):
        # Ensure some tokens are present in the outstanding list
        RefreshToken.for_user(self.user)
        RefreshToken.for_user(self.user)

        OutstandingToken = apps.get_model("token_blacklist", "OutstandingToken")

        self.expected_hexes = [i.jti.hex for i in OutstandingToken.objects.all()]

    def test_jti_field_should_contain_uuid_hex_strings(self):
        OutstandingToken = self.apps.get_model("token_blacklist", "OutstandingToken")

        actual_hexes = [i.jti_hex for i in OutstandingToken.objects.all()]

        self.assertEqual(actual_hexes, self.expected_hexes)


class TokenVerifySerializerShouldHonourBlacklist(MigrationTestCase):
    migrate_from = ("token_blacklist", "0002_outstandingtoken_jti_hex")
    migrate_to = ("token_blacklist", "0003_auto_20171017_2007")

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
        )

        super().setUp()

    @override_api_settings(BLACKLIST_AFTER_ROTATION=True)
    def test_token_verify_serializer_should_honour_blacklist_if_rotation_enabled(
        self,
    ):
        refresh_token = RefreshToken.for_user(self.user)
        refresh_token.blacklist()

        serializer = TokenVerifySerializer(data={"token": str(refresh_token)})
        self.assertFalse(serializer.is_valid())

    @override_api_settings(BLACKLIST_AFTER_ROTATION=False)
    def test_token_verify_serializer_should_honour_blacklist_if_rotation_not_enabled(
        self,
    ):
        refresh_token = RefreshToken.for_user(self.user)
        refresh_token.blacklist()

        serializer = TokenVerifySerializer(data={"token": str(refresh_token)})
        self.assertFalse(serializer.is_valid())


class TestBigAutoFieldIDMigration(MigrationTestCase):
    migrate_from = ("token_blacklist", "0007_auto_20171017_2214")
    migrate_to = ("token_blacklist", "0008_migrate_to_bigautofield")

    def test_outstandingtoken_id_field_is_biagauto_field(self):
        OutstandingToken = self.apps.get_model("token_blacklist", "OutstandingToken")
        assert isinstance(OutstandingToken._meta.get_field("id"), BigAutoField)

    def test_blacklistedtoken_id_field_is_biagauto_field(self):
        BlacklistedToken = self.apps.get_model("token_blacklist", "BlacklistedToken")
        assert isinstance(BlacklistedToken._meta.get_field("id"), BigAutoField)
