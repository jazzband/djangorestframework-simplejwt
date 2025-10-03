# These tests verify the cache blacklisting functionalities.
#
# We primarily use Django's `LocMemCache` backend for these tests.
# This is because LocMemCache is an in-memory backend that is fast,
# requires no external services (like Redis or Memcached), and adheres
# strictly to the standard Django cache API.
#
# The cache integration logic managed via the BlacklistCache class *only* uses the standard
# methods provided by the Django cache API (like `set`, `get`, `delete`).
# It does NOT rely on any backend-specific features.
#
# BECAUSE the code only uses this standard API, testing thoroughly with
# a compliant backend like LocMemCache is considered sufficient. This ensures
# that the logic works correctly with *any other* compliant Django cache backend
# (such as RedisCache, MemcachedCache, etc.) that a user might configure in production,
# as they all implement the same standard API.

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import InvalidCacheBackendError, caches
from django.test import TestCase
from freezegun import freeze_time

from rest_framework_simplejwt.cache import BlacklistCache, blacklist_cache
from rest_framework_simplejwt.exceptions import RefreshTokenBlacklistedError, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.token_family.models import BlacklistedTokenFamily
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow
from tests.utils import override_api_settings


class TestBlacklistCache(TestCase):
    """
    Test the BlacklistCache class and its integration with token blacklisting.
    """

    def setUp(self):
        # Create a fresh cache instance for each test
        self.cache = BlacklistCache()
        # Clear the cache before each test
        self.cache.cache.clear()

    def test_cache_properties(self):
        """Test that the cache properties read from settings correctly"""
        with override_api_settings(
            CACHE_BLACKLISTED_REFRESH_TOKENS=True, CACHE_BLACKLISTED_FAMILIES=False
        ):
            self.assertTrue(self.cache.is_refresh_tokens_cache_enabled)
            self.assertFalse(self.cache.is_families_cache_enabled)

        with override_api_settings(
            CACHE_BLACKLISTED_REFRESH_TOKENS=False, CACHE_BLACKLISTED_FAMILIES=True
        ):
            self.assertFalse(self.cache.is_refresh_tokens_cache_enabled)
            self.assertTrue(self.cache.is_families_cache_enabled)

    @override_api_settings(
        CACHE_KEY_PREFIX_BLACKLISTED_REFRESH_TOKENS="test_rt",
        CACHE_KEY_PREFIX_BLACKLISTED_FAMILIES="test_fam",
    )
    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly"""
        refresh_key = self.cache._get_refresh_token_key("abc123")
        family_key = self.cache._get_family_key("fam456")

        self.assertEqual(refresh_key, "test_rt:abc123")
        self.assertEqual(family_key, "test_fam:fam456")

    def test_add_refresh_token(self):
        jti = "test-jti-123"

        # Add the token to the cache and verify it's there
        self.cache.add_refresh_token(jti)
        self.assertTrue(self.cache.is_refresh_token_blacklisted(jti))

    def test_add_token_family(self):
        family_id = "test-family-456"

        # Add the family to the cache and verify it's there
        self.cache.add_token_family(family_id)
        self.assertTrue(self.cache.is_token_family_blacklisted(family_id))

    def test_is_refresh_token_blacklisted(self):
        jti_blacklisted = "blacklisted-jti"
        jti_not_blacklisted = "clean-jti"

        self.cache.add_refresh_token(jti_blacklisted)

        self.assertTrue(self.cache.is_refresh_token_blacklisted(jti_blacklisted))
        self.assertFalse(self.cache.is_refresh_token_blacklisted(jti_not_blacklisted))

    def test_is_token_family_blacklisted(self):
        family_blacklisted = "blacklisted-family"
        family_not_blacklisted = "clean-family"

        self.cache.add_token_family(family_blacklisted)

        self.assertTrue(self.cache.is_token_family_blacklisted(family_blacklisted))
        self.assertFalse(self.cache.is_token_family_blacklisted(family_not_blacklisted))

    def test_delete_refresh_token_from_cache(self):
        jti = "delete-me-jti"
        self.cache.add_refresh_token(jti)

        # Verify it's in the cache before deletion
        self.assertTrue(self.cache.is_refresh_token_blacklisted(jti))

        # Delete and verify it's gone
        result = self.cache.delete_refresh_token_from_cache(jti)
        self.assertTrue(result)
        self.assertFalse(self.cache.is_refresh_token_blacklisted(jti))

        # Try deleting again - should return False
        result = self.cache.delete_refresh_token_from_cache(jti)
        self.assertFalse(result)

    def test_delete_family_from_cache(self):
        family_id = "delete-me-family"
        self.cache.add_token_family(family_id)

        # Verify it's in the cache before deletion
        self.assertTrue(self.cache.is_token_family_blacklisted(family_id))

        # Delete and verify it's gone
        result = self.cache.delete_family_from_cache(family_id)
        self.assertTrue(result)
        self.assertFalse(self.cache.is_token_family_blacklisted(family_id))

        # Try deleting again - should return False
        result = self.cache.delete_family_from_cache(family_id)
        self.assertFalse(result)

    @override_api_settings(
        CACHE_BLACKLISTED_REFRESH_TOKENS=True,
        CACHE_TTL_BLACKLISTED_REFRESH_TOKENS=30,  # Set to 30 seconds
    )
    def test_refresh_token_ttl(self):
        """Test that refresh tokens are gone after the configured TTL."""
        jti = "expiring-jti"

        with freeze_time(aware_utcnow() - timedelta(seconds=31)):
            self.cache.add_refresh_token(jti)
            self.assertTrue(self.cache.is_refresh_token_blacklisted(jti))

        # Should be gone now
        self.assertFalse(self.cache.is_refresh_token_blacklisted(jti))

    @override_api_settings(
        CACHE_BLACKLISTED_FAMILIES=True,
        CACHE_TTL_BLACKLISTED_FAMILIES=30,  # Set to 30 seconds
    )
    def test_token_family_ttl(self):
        """Test that token families are gone after the configured TTL."""
        family_id = "expiring-family"

        with freeze_time(aware_utcnow() - timedelta(seconds=31)):
            self.cache.add_token_family(family_id)
            self.assertTrue(self.cache.is_token_family_blacklisted(family_id))

        # Should be gone now
        self.assertFalse(self.cache.is_token_family_blacklisted(family_id))


class TestBlacklistMixinCacheIntegration(TestCase):
    """
    Test the integration of BlacklistCache with the BlacklistMixin.
    """

    def setUp(self):
        # Clear the cache before each test
        blacklist_cache.cache.clear()

    @override_api_settings(CACHE_BLACKLISTED_REFRESH_TOKENS=True)
    def test_refresh_token_blacklist_method_with_cache_enabled(self):
        """Test that blacklisted tokens are added to cache when enabled"""
        # Create a token and blacklist it
        token = RefreshToken()
        jti = token.payload[api_settings.JTI_CLAIM]

        token.blacklist()

        # Check that it was added to the cache
        self.assertTrue(blacklist_cache.is_refresh_token_blacklisted(jti))

        # check that is was added to the DB
        try:
            BlacklistedToken.objects.get(token__jti=jti)
        except BlacklistedToken.DoesNotExist:
            self.fail(f"Expected BlacklistedToken object with jti='{jti}'")

    @override_api_settings(CACHE_BLACKLISTED_REFRESH_TOKENS=True)
    def test_refresh_token_check_blacklist_method_with_cache_enabled(self):
        """Test that check_blacklist checks the cache when enabled"""
        # Create a token
        token = RefreshToken()
        jti = token.payload[api_settings.JTI_CLAIM]

        # Add it to the cache directly (not the database)
        blacklist_cache.add_refresh_token(jti)

        # Verify that check_blacklist finds it in the cache
        with self.assertRaises(RefreshTokenBlacklistedError):
            token.check_blacklist()

        # call blacklist method to add the token to the DB blacklist
        token.blacklist()
        blacklist_cache.cache.clear()

        self.assertFalse(blacklist_cache.is_refresh_token_blacklisted(jti))

        # here we verify that the DB is check if the token is not in the cache
        with self.assertRaises(RefreshTokenBlacklistedError):
            token.check_blacklist()

    @override_api_settings(CACHE_BLACKLISTED_REFRESH_TOKENS=False)
    def test_refresh_token_blacklist_method_with_cache_disabled(self):
        # Create a token and blacklist it
        token = RefreshToken()
        jti = token.payload[api_settings.JTI_CLAIM]

        token.blacklist()

        # Check that is not present in the cache
        self.assertFalse(blacklist_cache.is_refresh_token_blacklisted(jti))

        # check that is was added to the DB
        try:
            BlacklistedToken.objects.get(token__jti=jti)
        except BlacklistedToken.DoesNotExist:
            self.fail(f"Expected BlacklistedToken object with jti='{jti}'")

    @override_api_settings(CACHE_BLACKLISTED_REFRESH_TOKENS=False)
    def test_refresh_token_check_blacklist_method_with_cache_disabled(self):
        """Test that check_blacklist checks the cache when enabled"""
        # Create a token
        token = RefreshToken()
        jti = token.payload[api_settings.JTI_CLAIM]

        # Add it to the cache directly (not the database)
        blacklist_cache.add_refresh_token(jti)

        # it should pass and not raise and error since the token
        # is only in the cache and not the DB
        token.check_blacklist()

        # clean cache to remove the previous token
        blacklist_cache.cache.clear()

        # call blacklist method to add the token to the DB blacklist
        token.blacklist()

        self.assertFalse(blacklist_cache.is_refresh_token_blacklisted(jti))

        with self.assertRaises(RefreshTokenBlacklistedError):
            token.check_blacklist()


class TestFamilyMixinCacheIntegration(TestCase):
    """
    Test the integration of BlacklistCache with the FamilyMixin.
    """

    def setUp(self):
        self.user = User.objects.create(username="test_user", password="test_password")
        # Clear the cache before each test
        blacklist_cache.cache.clear()

    @override_api_settings(CACHE_BLACKLISTED_FAMILIES=True, TOKEN_FAMILY_ENABLED=True)
    def test_token_family_blacklist_method_with_cache_enabled(self):
        # Create a token and blacklist its family
        token = RefreshToken.for_user(self.user)
        family_id = token.payload.get(api_settings.TOKEN_FAMILY_CLAIM)

        # Ensure there is a family_id
        self.assertIsNotNone(family_id)

        token.blacklist_family()

        # Check that it was added to the cache
        self.assertTrue(blacklist_cache.is_token_family_blacklisted(family_id))

        # check that is was added to the DB
        try:
            BlacklistedTokenFamily.objects.get(family__family_id=family_id)
        except BlacklistedTokenFamily.DoesNotExist:
            self.fail(
                f"Expected BlacklistedTokenFamily object with family_id='{family_id}'"
            )

    @override_api_settings(CACHE_BLACKLISTED_FAMILIES=True, TOKEN_FAMILY_ENABLED=True)
    def test_token_family_check_blacklist_method_with_cache_enabled(self):
        # Create a token
        token = RefreshToken.for_user(self.user)
        family_id = token.payload.get(api_settings.TOKEN_FAMILY_CLAIM)

        # Ensure there is a family_id
        self.assertIsNotNone(family_id)

        # Add it to the cache directly (not the database)
        blacklist_cache.add_token_family(family_id)

        with self.assertRaises(TokenError):
            RefreshToken.check_family_blacklist(token)

        # call blacklist method to add the token to the DB blacklist
        token.blacklist_family()
        blacklist_cache.cache.clear()

        self.assertFalse(blacklist_cache.is_token_family_blacklisted(family_id))

        # here we verify that the DB is check if the token is not in the cache
        with self.assertRaises(TokenError):
            token.check_family_blacklist(token)

    @override_api_settings(CACHE_BLACKLISTED_FAMILIES=False, TOKEN_FAMILY_ENABLED=True)
    def test_token_family_blacklist_method_with_cache_disabled(self):
        # Create a token and blacklist its family
        token = RefreshToken.for_user(self.user)
        family_id = token.payload.get(api_settings.TOKEN_FAMILY_CLAIM)

        # Ensure there is a family_id
        self.assertIsNotNone(family_id)

        token.blacklist_family()

        # Check that token is not present in the cache
        self.assertFalse(blacklist_cache.is_token_family_blacklisted(family_id))

        # check that is was added to the DB
        try:
            BlacklistedTokenFamily.objects.get(family__family_id=family_id)
        except BlacklistedTokenFamily.DoesNotExist:
            self.fail(
                f"Expected BlacklistedTokenFamily object with family_id='{family_id}'"
            )

    @override_api_settings(CACHE_BLACKLISTED_FAMILIES=False, TOKEN_FAMILY_ENABLED=True)
    def test_token_family_check_blacklist_method_with_cache_disabled(self):
        # Create a token
        token = RefreshToken.for_user(self.user)
        family_id = token.payload.get(api_settings.TOKEN_FAMILY_CLAIM)

        # Ensure there is a family_id
        self.assertIsNotNone(family_id)

        # Add it to the cache directly (not the database)
        blacklist_cache.add_token_family(family_id)

        # it should pass and not raise any errors
        RefreshToken.check_family_blacklist(token)

        # clean cache to remove the previous family
        blacklist_cache.cache.clear()

        # call blacklist method to add the token to the DB blacklist
        token.blacklist_family()

        self.assertFalse(blacklist_cache.is_token_family_blacklisted(family_id))

        with self.assertRaises(TokenError):
            token.check_family_blacklist(token)


class TestCacheBackend(TestCase):
    """
    Test the cache backend configuration.
    """

    def test_cache_backend_configuration(self):
        """Test that the correct cache backend is used"""
        with override_api_settings(SJWT_CACHE_NAME="default"):
            self.assertEqual(blacklist_cache.cache, caches["default"])

        # If you have a different cache configured, you can test it
        # Note: This requires the cache to be configured in settings
        with override_api_settings(SJWT_CACHE_NAME="alternate"):
            self.assertEqual(blacklist_cache.cache, caches["alternate"])

    @override_api_settings(SJWT_CACHE_NAME="nonexistent_cache")
    def test_invalid_cache_backend(self):
        """Test that trying to use a non-existent cache backend raises an appropriate error."""
        cache = BlacklistCache()
        with self.assertRaises(InvalidCacheBackendError):
            # This should raise an exception when trying to access the cache property
            _ = cache.cache
