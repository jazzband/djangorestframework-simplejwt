from django.core.cache import caches

from .settings import api_settings


class BlacklistCache:
    """
    Cache implementation for Simple JWT blacklist functionalities.
    Provides caching for both blacklisted refresh tokens and token families.
    """

    @property
    def cache(self):
        """Get the configured cache backend for Simple JWT."""
        return caches[api_settings.SJWT_CACHE_NAME]

    @property
    def is_refresh_tokens_cache_enabled(self):
        """Check if refresh token caching is enabled."""
        return api_settings.CACHE_BLACKLISTED_REFRESH_TOKENS

    @property
    def is_families_cache_enabled(self):
        """Check if token family caching is enabled."""
        return api_settings.CACHE_BLACKLISTED_FAMILIES

    def _get_refresh_token_key(self, jti: str) -> str:
        """Generate cache key for a refresh token JTI."""
        return f"{api_settings.CACHE_KEY_PREFIX_BLACKLISTED_REFRESH_TOKENS}:{jti}"

    def _get_family_key(self, family_id: str) -> str:
        """Generate cache key for a token family ID."""
        return f"{api_settings.CACHE_KEY_PREFIX_BLACKLISTED_FAMILIES}:{family_id}"

    def add_refresh_token(self, jti: str) -> None:
        """Stores refresh token JTI in the cache."""
        key = self._get_refresh_token_key(jti)
        self.cache.set(
            key, True, timeout=api_settings.CACHE_TTL_BLACKLISTED_REFRESH_TOKENS
        )

    def is_refresh_token_blacklisted(self, jti: str) -> bool:
        """Checks if a refresh token JTI is blacklisted in cache."""
        return self.cache.get(self._get_refresh_token_key(jti), False)

    def add_token_family(self, family_id: str) -> None:
        """Stores a token family ID in the cache."""
        key = self._get_family_key(family_id)
        self.cache.set(key, True, timeout=api_settings.CACHE_TTL_BLACKLISTED_FAMILIES)

    def is_token_family_blacklisted(self, family_id: str) -> bool:
        """Checks if a token family is blacklisted in cache."""
        return self.cache.get(self._get_family_key(family_id), False)

    def delete_refresh_token_from_cache(self, jti: str) -> bool:
        """Returns True if the token jti was successfully deleted, False otherwise."""
        return self.cache.delete(self._get_refresh_token_key(jti))

    def delete_family_from_cache(self, family_id: str) -> bool:
        """Returns True if the family ID was successfully deleted, False otherwise."""
        return self.cache.delete(self._get_family_key(family_id))


# Singleton instance for centralized cache management
blacklist_cache = BlacklistCache()
