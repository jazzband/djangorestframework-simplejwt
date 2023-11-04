from typing import Any, Dict, Generic, Type, TypeVar, cast

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError

from .settings import api_settings
from .tokens import RefreshToken, SlidingToken, Token, UntypedToken

if api_settings.BLACKLIST_AFTER_ROTATION:
    from .token_blacklist.models import BlacklistedToken

T = TypeVar("T", bound=Token)


class PasswordField(serializers.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("style", {})

        kwargs["style"]["input_type"] = "password"
        kwargs["write_only"] = True

        super().__init__(*args, **kwargs)


class TokenObtainSerializer(serializers.Serializer, Generic[T]):
    username_field = get_user_model().USERNAME_FIELD
    token_class: Type[T]  # Subclasses should set this attribute
    user: AbstractBaseUser

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(write_only=True)
        self.fields["password"] = PasswordField()

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)  # type: ignore # Will be validated to not be None in the next line

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        return {}

    @classmethod
    def get_token(cls, user: AbstractBaseUser) -> T:
        return cast(T, cls.token_class.for_user(user))


class TokenObtainPairSerializer(TokenObtainSerializer[RefreshToken]):
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)  # type: ignore # Manual call can pass None

        return data


class TokenObtainSlidingSerializer(TokenObtainSerializer[SlidingToken]):
    token_class = SlidingToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        token = self.get_token(self.user)

        data["token"] = str(token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)  # type: ignore # Manual call can pass None

        return data


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data


class TokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()
    token_class = SlidingToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        token = self.token_class(attrs["token"])

        # Check that the timestamp in the "refresh_exp" claim has not
        # passed
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)

        # Update the "exp" and "iat" claims
        token.set_exp()
        token.set_iat()

        return {"token": str(token)}


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, None]) -> Dict[Any, Any]:
        token = UntypedToken(attrs["token"])

        if (
            api_settings.BLACKLIST_AFTER_ROTATION
            and "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti: str = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise ValidationError("Token is blacklisted")

        return {}


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return {}
