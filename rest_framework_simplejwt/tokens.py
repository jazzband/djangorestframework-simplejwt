from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .cache import blacklist_cache
from .exceptions import (
    ExpiredTokenError,
    RefreshTokenBlacklistedError,
    TokenBackendError,
    TokenBackendExpiredToken,
    TokenError,
)
from .models import TokenUser
from .settings import api_settings
from .token_blacklist.models import BlacklistedToken, OutstandingToken
from .token_family.models import BlacklistedTokenFamily, TokenFamily
from .utils import (
    aware_utcnow,
    datetime_from_epoch,
    datetime_to_epoch,
    format_lazy,
    get_md5_hash_password,
    logger,
)

if TYPE_CHECKING:
    from .backends import TokenBackend

T = TypeVar("T", bound="Token")

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """

    token_type: Optional[str] = None
    lifetime: Optional[timedelta] = None

    def __init__(self, token: Optional["Token"] = None, verify: bool = True) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError(_("Cannot create token with no type or lifetime"))

        self.token = token
        self.current_time = aware_utcnow()

        # Set up token
        if token is not None:
            # An encoded token was provided
            token_backend = self.get_token_backend()

            # Decode token
            try:
                self.payload = token_backend.decode(token, verify=verify)
            except TokenBackendExpiredToken as e:
                raise ExpiredTokenError(_("Token is expired")) from e
            except TokenBackendError as e:
                raise TokenError(_("Token is invalid")) from e

            if verify:
                self.verify()
        else:
            # New token.  Skip all the verification steps.
            self.payload = {api_settings.TOKEN_TYPE_CLAIM: self.token_type}

            # Set "exp" and "iat" claims with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
            self.set_iat(at_time=self.current_time)

            # Set "jti" claim
            self.set_jti()

    def __repr__(self) -> str:
        return repr(self.payload)

    def __getitem__(self, key: str):
        return self.payload[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.payload[key] = value

    def __delitem__(self, key: str) -> None:
        del self.payload[key]

    def __contains__(self, key: str) -> Any:
        return key in self.payload

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.payload.get(key, default)

    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        return self.get_token_backend().encode(self.payload)

    def verify(self) -> None:
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # If the defaults are not None then we should enforce the
        # requirement of these settings.As above, the spec labels
        # these as optional.
        if (
            api_settings.JTI_CLAIM is not None
            and api_settings.JTI_CLAIM not in self.payload
        ):
            raise TokenError(_("Token has no id"))

        if api_settings.TOKEN_TYPE_CLAIM is not None:
            self.verify_token_type()

    def verify_token_type(self) -> None:
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[api_settings.TOKEN_TYPE_CLAIM]
        except KeyError as e:
            raise TokenError(_("Token has no type")) from e

        if self.token_type != token_type:
            raise TokenError(_("Token has wrong type"))

    def set_jti(self) -> None:
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self.payload[api_settings.JTI_CLAIM] = uuid4().hex

    def set_exp(
        self,
        claim: str = "exp",
        from_time: Optional[datetime] = None,
        lifetime: Optional[timedelta] = None,
    ) -> None:
        """
        Updates the expiration time of a token.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.4
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    def set_iat(self, claim: str = "iat", at_time: Optional[datetime] = None) -> None:
        """
        Updates the time at which the token was issued.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.6
        """
        if at_time is None:
            at_time = self.current_time

        self.payload[claim] = datetime_to_epoch(at_time)

    def check_exp(
        self, claim: str = "exp", current_time: Optional[datetime] = None
    ) -> None:
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError as e:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim)) from e

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.get_token_backend().get_leeway()
        if claim_time <= current_time - leeway:
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    def outstand(self) -> Optional[OutstandingToken]:
        """
        Ensures this token is included in the outstanding token list and
        adds it to the outstanding token list if not.
        """
        return None

    @classmethod
    def for_user(cls: type[T], user: AuthUser) -> T:
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """

        if hasattr(user, "is_active") and not user.is_active:
            logger.warning(
                f"Creating token for inactive user: {user.id}. If this is not intentional, consider checking the user's status before calling the `for_user` method."
            )

        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id

        if api_settings.CHECK_REVOKE_TOKEN:
            token[api_settings.REVOKE_TOKEN_CLAIM] = get_md5_hash_password(
                user.password
            )

        return token

    _token_backend: Optional["TokenBackend"] = None

    @property
    def token_backend(self) -> "TokenBackend":
        if self._token_backend is None:
            self._token_backend = import_string(
                "rest_framework_simplejwt.state.token_backend"
            )
        return self._token_backend

    def get_token_backend(self) -> "TokenBackend":
        # Backward compatibility.
        return self.token_backend


class BlacklistMixin(Generic[T]):
    """
    If the `rest_framework_simplejwt.token_blacklist` app was configured to be
    used, tokens created from `BlacklistMixin` subclasses will insert
    themselves into an outstanding token list and also check for their
    membership in a token blacklist.
    """

    payload: dict[str, Any]

    if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:

        def verify(self, *args, **kwargs) -> None:
            self.check_blacklist()

            super().verify(*args, **kwargs)  # type: ignore

        def check_blacklist(self) -> None:
            """
            Checks if this token is present in the token blacklist.  Raises
            `TokenError` if so.
            """
            jti = self.payload[api_settings.JTI_CLAIM]

            if (
                blacklist_cache.is_refresh_tokens_cache_enabled
                and blacklist_cache.is_refresh_token_blacklisted(jti)
            ):
                raise RefreshTokenBlacklistedError(_("Token is blacklisted"))

            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise RefreshTokenBlacklistedError(_("Token is blacklisted"))

        def blacklist(self) -> tuple[BlacklistedToken, bool]:
            """
            Ensures this token is included in the outstanding token list and
            adds it to the blacklist.
            """
            jti = self.payload[api_settings.JTI_CLAIM]
            exp = self.payload["exp"]
            user_id = self.payload.get(api_settings.USER_ID_CLAIM)
            User = get_user_model()
            try:
                user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except User.DoesNotExist:
                user = None

            # Ensure outstanding token exists with given jti
            token, _ = OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "user": user,
                    "created_at": self.current_time,
                    "token": str(self),
                    "expires_at": datetime_from_epoch(exp),
                },
            )

            blacklisted_token, created = BlacklistedToken.objects.get_or_create(
                token=token
            )

            if blacklist_cache.is_refresh_tokens_cache_enabled:
                blacklist_cache.add_refresh_token(jti)

            return blacklisted_token, created

        def outstand(self) -> Optional[OutstandingToken]:
            """
            Ensures this token is included in the outstanding token list and
            adds it to the outstanding token list if not.
            """
            jti = self.payload[api_settings.JTI_CLAIM]
            exp = self.payload["exp"]
            user_id = self.payload.get(api_settings.USER_ID_CLAIM)
            User = get_user_model()
            try:
                user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except User.DoesNotExist:
                user = None

            # Ensure outstanding token exists with given jti
            return OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "user": user,
                    "created_at": self.current_time,
                    "token": str(self),
                    "expires_at": datetime_from_epoch(exp),
                },
            )

        @classmethod
        def for_user(cls: type[T], user: AuthUser) -> T:
            """
            Adds this token to the outstanding token list.
            """
            token = super().for_user(user)  # type: ignore

            jti = token[api_settings.JTI_CLAIM]
            exp = token["exp"]

            OutstandingToken.objects.create(
                user=user,
                jti=jti,
                token=str(token),
                created_at=token.current_time,
                expires_at=datetime_from_epoch(exp),
            )

            return token


class FamilyMixin(Generic[T]):
    """
    Tokens created from FamilyMixin subclasses will track token families,
    enhancing the ability to detect and manage unwanted refresh token reuse.

    This is useful for implementing security measures such as blacklisting
    entire token families upon detected misuse.
    """

    payload: dict[str, Any]

    if (
        api_settings.TOKEN_FAMILY_ENABLED
        and "rest_framework_simplejwt.token_family" in settings.INSTALLED_APPS
    ):

        def verify(self, *args, **kwargs) -> None:
            """
            Runs verification checks for token family expiration and blacklist status
            before calling the superclass verification.
            """
            self.__class__.check_family_expiration(token=self)
            self.__class__.check_family_blacklist(token=self)

            super().verify(*args, **kwargs)  # type: ignore

        def blacklist_family(self) -> tuple[BlacklistedTokenFamily, bool]:
            """
            Blacklists the token family.
            """
            family_id = self.get_family_id()
            if not family_id:
                raise TokenError(_("Token has no family ID"))

            # Ensure Family exist with the given family_id
            family, created = TokenFamily.objects.get_or_create(
                family_id=family_id,
                defaults={
                    "user": self._get_user(),
                    "created_at": self.current_time,
                    "expires_at": self.get_family_expiration_date(),
                },
            )

            # Blacklist the entire family
            blacklisted_fam, created = BlacklistedTokenFamily.objects.get_or_create(
                family=family
            )

            if blacklist_cache.is_families_cache_enabled:
                blacklist_cache.add_token_family(family_id)

            return blacklisted_fam, created

        def get_family_id(self) -> Optional[str]:
            return self.payload.get(api_settings.TOKEN_FAMILY_CLAIM, None)

        def get_family_expiration_date(self) -> Optional[datetime]:
            expires_at = self.payload.get(
                api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM, None
            )

            if expires_at is None:
                return None

            return datetime_from_epoch(expires_at)

        def _get_user(self) -> Optional[AuthUser]:
            """
            Retrieves the user associated with this token.
            Returns None if the user does not exist.
            """
            user_id = self.payload.get(api_settings.USER_ID_CLAIM)
            if not user_id:
                return None

            User = get_user_model()
            try:
                return User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except User.DoesNotExist:
                return None

        @staticmethod
        def check_family_blacklist(token: T) -> None:
            """
            Checks if this token's family is blacklisted.
            Raises `TokenError` if so.

            If the token does not have a `family_id`, it is either an old
            token (before this feature was added/enabled) or it could be a
            manually issued JWT without family tracking. In such cases, we
            skip the blacklist check.
            """
            family_id = token.get(api_settings.TOKEN_FAMILY_CLAIM)

            if not family_id:
                user_id = token.get(api_settings.USER_ID_CLAIM)
                logger.warning(
                    f"Token of user:{user_id} does not have a family_id. Skipping family blacklist check."
                )
                return

            if (
                blacklist_cache.is_families_cache_enabled
                and blacklist_cache.is_token_family_blacklisted(family_id)
            ):
                raise TokenError(_("Token family is blacklisted"))

            if BlacklistedTokenFamily.objects.filter(
                family__family_id=family_id
            ).exists():
                raise TokenError(_("Token family is blacklisted"))

        @staticmethod
        def check_family_expiration(
            token: T, current_time: Optional[datetime] = None
        ) -> None:
            """
            Checks whether the token family's expiration timestamp has passed
            (relative to the given `current_time`).

            Raises a `TokenError` with a user-facing error message if the family has expired.
            If no expiration claim is set, the check is skipped.
            """
            expires_at = token.get(api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM, None)

            if expires_at is None:
                return  # No expiration set, so we skip this check.

            expiration_date = datetime_from_epoch(expires_at)

            if current_time is None:
                current_time = aware_utcnow()

            if expiration_date <= current_time:
                raise TokenError(_("Token family has expired"))

        @classmethod
        def for_user(cls: type[T], user: AuthUser) -> T:
            """
            Generates a new token instance with a unique family ID and optional family expiration.

            This method:
            - Creates a unique `family_id`.
            - Assigns a family expiration timestamp if `TOKEN_FAMILY_LIFETIME` is set.
            - Saves the token family information in the database.
            """
            token = super().for_user(user)  # type: ignore

            # Generate a new family ID
            family_id = uuid4().hex
            token[api_settings.TOKEN_FAMILY_CLAIM] = family_id

            family_lifetime = api_settings.TOKEN_FAMILY_LIFETIME
            expires_at: Optional[datetime]

            # Since the token_family settings values are checked at startup,
            # we don't have to worry about checking the value type again.
            if family_lifetime is None:
                expires_at = None
            else:
                expires_at = token.current_time + family_lifetime
                token[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM] = datetime_to_epoch(
                    expires_at
                )

            # Create the token family
            TokenFamily.objects.create(
                user=user,
                family_id=family_id,
                created_at=token.current_time,
                expires_at=expires_at,
            )

            return token


class SlidingToken(BlacklistMixin["SlidingToken"], Token):
    token_type = "sliding"
    lifetime = api_settings.SLIDING_TOKEN_LIFETIME

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.token is None:
            # Set sliding refresh expiration claim if new token
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )


class AccessToken(Token):
    token_type = "access"
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME

    def verify(self):
        """Runs standard verification and optionally checks token family status."""
        super().verify()

        if (
            api_settings.TOKEN_FAMILY_ENABLED
            and api_settings.TOKEN_FAMILY_CHECK_ON_ACCESS
            and "rest_framework_simplejwt.token_family" in settings.INSTALLED_APPS
        ):
            FamilyMixin.check_family_expiration(token=self)
            FamilyMixin.check_family_blacklist(token=self)


class RefreshToken(BlacklistMixin["RefreshToken"], FamilyMixin["RefreshToken"], Token):
    token_type = "refresh"
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        "exp",
        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        "jti",
        "iat",
    )
    access_token_class = AccessToken

    @property
    def access_token(self) -> AccessToken:
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        access = self.access_token_class()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        # Convert tuple to set for efficient updates.
        # This allows us to dynamically add or remove claims without creating a new tuple
        no_copy = set(self.no_copy_claims)

        # If TOKEN_FAMILY_CHECK_ON_ACCESS is False, the family claims are not needed in the access token.
        # We exclude them from being copied to reduce unnecessary token size.
        if (
            api_settings.TOKEN_FAMILY_ENABLED
            and not api_settings.TOKEN_FAMILY_CHECK_ON_ACCESS
        ):
            no_copy.update(
                {
                    api_settings.TOKEN_FAMILY_CLAIM,
                    api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM,
                }
            )

        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access


class UntypedToken(Token):
    token_type = "untyped"
    lifetime = timedelta(seconds=0)

    def verify_token_type(self) -> None:
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        pass
