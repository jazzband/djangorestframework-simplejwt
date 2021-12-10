from ninja_extra import api_controller, http_post
from ninja_extra.permissions import AllowAny
from ninja_schema import Schema

from ninja_jwt import schema


class TokenVerificationController:
    auto_import = False

    @http_post("/verify", response={200: Schema}, url_name="token_verify")
    def verify_token(self, token: schema.TokenVerifySerializer):
        return {}


class TokenBlackListController:
    auto_import = False

    @http_post("/blacklist", response={200: Schema}, url_name="token_blacklist")
    def blacklist_token(self, refresh: schema.TokenBlacklistSerializer):
        return {}


class TokenObtainPairController:
    auto_import = False

    @http_post(
        "/pair", response=schema.TokenObtainPairOutput, url_name="token_obtain_pair"
    )
    def obtain_token(self, user_token: schema.TokenObtainPairSerializer):
        return user_token.output_schema()

    @http_post(
        "/refresh", response=schema.TokenRefreshSerializer, url_name="token_refresh"
    )
    def refresh_token(self, refresh_token: schema.TokenRefreshSchema):
        refresh = schema.TokenRefreshSerializer(**refresh_token.dict())
        return refresh


class TokenObtainSlidingController(TokenObtainPairController):
    auto_import = False

    @http_post(
        "/sliding",
        response=schema.TokenObtainSlidingOutput,
        url_name="token_obtain_sliding",
    )
    def obtain_token(self, user_token: schema.TokenObtainSlidingSerializer):
        return user_token.output_schema()

    @http_post(
        "/sliding/refresh",
        response=schema.TokenRefreshSlidingSerializer,
        url_name="token_refresh_sliding",
    )
    def refresh_token(self, refresh_token: schema.TokenRefreshSlidingSchema):
        refresh = schema.TokenRefreshSlidingSerializer(**refresh_token.dict())
        return refresh


@api_controller("/token", permissions=[AllowAny], tags=["token"])
class NinjaJWTDefaultController(TokenVerificationController, TokenObtainPairController):
    """NinjaJWT Default controller for obtaining and refreshing tokens"""

    auto_import = False


@api_controller("/token", permissions=[AllowAny], tags=["token"])
class NinjaJWTSlidingController(
    TokenVerificationController, TokenObtainSlidingController
):
    """
    NinjaJWT Sliding controller for obtaining and refreshing tokens
    Add 'ninja_jwt.tokens.SlidingToken' in AUTH_TOKEN_CLASSES in Settings
    """

    auto_import = False
