from asgiref.sync import sync_to_async
from ninja_extra import ControllerBase, api_controller, http_post
from ninja_extra.permissions import AllowAny

from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings

__all__ = [
    "TokenVerificationController",
    "TokenBlackListController",
    "TokenObtainPairController",
    "TokenObtainSlidingController",
    "TokenObtainSlidingController",
    "NinjaJWTDefaultController",
    "NinjaJWTSlidingController",
    "AsyncTokenVerificationController",
    "AsyncTokenBlackListController",
    "AsyncTokenObtainPairController",
    "AsyncTokenObtainSlidingController",
    "AsyncTokenObtainSlidingController",
    "AsyncNinjaJWTDefaultController",
    "AsyncNinjaJWTSlidingController",
]

schema = SchemaControl(api_settings)


class TokenVerificationController:
    auto_import = False

    @http_post(
        "/verify",
        response={200: schema.verify_schema.get_response_schema()},
        url_name="token_verify",
        operation_id="token_verify",
    )
    def verify_token(self, token: schema.verify_schema):
        return token.to_response_schema()


class TokenBlackListController:
    auto_import = False

    @http_post(
        "/blacklist",
        response={200: schema.blacklist_schema.get_response_schema()},
        url_name="token_blacklist",
        operation_id="token_blacklist",
    )
    def blacklist_token(self, refresh: schema.blacklist_schema):
        return refresh.to_response_schema()


class TokenObtainPairController:
    auto_import = False

    @http_post(
        "/pair",
        response=schema.obtain_pair_schema.get_response_schema(),
        url_name="token_obtain_pair",
        operation_id="token_obtain_pair",
    )
    def obtain_token(self, user_token: schema.obtain_pair_schema):
        user_token.check_user_authentication_rule()
        return user_token.to_response_schema()

    @http_post(
        "/refresh",
        response=schema.obtain_pair_refresh_schema.get_response_schema(),
        url_name="token_refresh",
        operation_id="token_refresh",
    )
    def refresh_token(self, refresh_token: schema.obtain_pair_refresh_schema):
        return refresh_token.to_response_schema()


class TokenObtainSlidingController(TokenObtainPairController):
    auto_import = False

    @http_post(
        "/sliding",
        response=schema.obtain_sliding_schema.get_response_schema(),
        url_name="token_obtain_sliding",
        operation_id="token_obtain_sliding",
    )
    def obtain_token(self, user_token: schema.obtain_sliding_schema):
        user_token.check_user_authentication_rule()
        return user_token.to_response_schema()

    @http_post(
        "/sliding/refresh",
        response=schema.obtain_sliding_refresh_schema.get_response_schema(),
        url_name="token_refresh_sliding",
        operation_id="token_refresh_sliding",
    )
    def refresh_token(self, refresh_token: schema.obtain_sliding_refresh_schema):
        return refresh_token.to_response_schema()


@api_controller("/token", permissions=[AllowAny], tags=["token"], auth=None)
class NinjaJWTDefaultController(
    ControllerBase, TokenVerificationController, TokenObtainPairController
):
    """NinjaJWT Default controller for obtaining and refreshing tokens"""

    auto_import = False


@api_controller("/token", permissions=[AllowAny], tags=["token"], auth=None)
class NinjaJWTSlidingController(
    ControllerBase, TokenVerificationController, TokenObtainSlidingController
):
    """
    NinjaJWT Sliding controller for obtaining and refreshing tokens
    Add 'ninja_jwt.tokens.SlidingToken' in AUTH_TOKEN_CLASSES in Settings
    """

    auto_import = False


class AsyncTokenVerificationController(TokenVerificationController):
    @http_post(
        "/verify",
        response={200: schema.verify_schema.get_response_schema()},
        url_name="token_verify",
        operation_id="token_verify_async",
    )
    async def verify_token(self, token: schema.verify_schema):
        return token.to_response_schema()


class AsyncTokenBlackListController(TokenBlackListController):
    auto_import = False

    @http_post(
        "/blacklist",
        response={200: schema.blacklist_schema.get_response_schema()},
        url_name="token_blacklist",
        operation_id="token_blacklist_async",
    )
    async def blacklist_token(self, refresh: schema.blacklist_schema):
        return refresh.to_response_schema()


class AsyncTokenObtainPairController(TokenObtainPairController):
    @http_post(
        "/pair",
        response=schema.obtain_pair_schema.get_response_schema(),
        url_name="token_obtain_pair",
        operation_id="token_obtain_pair_async",
    )
    async def obtain_token(self, user_token: schema.obtain_pair_schema):
        await sync_to_async(user_token.check_user_authentication_rule)()
        return user_token.to_response_schema()

    @http_post(
        "/refresh",
        response=schema.obtain_pair_refresh_schema.get_response_schema(),
        url_name="token_refresh",
        operation_id="token_refresh_async",
    )
    async def refresh_token(self, refresh_token: schema.obtain_pair_refresh_schema):
        refresh = await sync_to_async(refresh_token.to_response_schema)()
        return refresh


class AsyncTokenObtainSlidingController(TokenObtainSlidingController):
    @http_post(
        "/sliding",
        response=schema.obtain_sliding_schema.get_response_schema(),
        url_name="token_obtain_sliding",
        operation_id="token_obtain_sliding_async",
    )
    async def obtain_token(self, user_token: schema.obtain_sliding_schema):
        await sync_to_async(user_token.check_user_authentication_rule)()
        return user_token.to_response_schema()

    @http_post(
        "/sliding/refresh",
        response=schema.obtain_sliding_refresh_schema.get_response_schema(),
        url_name="token_refresh_sliding",
        operation_id="token_refresh_sliding_async",
    )
    async def refresh_token(self, refresh_token: schema.obtain_sliding_refresh_schema):
        refresh = await sync_to_async(refresh_token.to_response_schema)()
        return refresh


@api_controller("/token", permissions=[AllowAny], tags=["token"], auth=None)
class AsyncNinjaJWTDefaultController(
    ControllerBase, AsyncTokenVerificationController, AsyncTokenObtainPairController
):
    """NinjaJWT Async Default controller for obtaining and refreshing tokens"""

    auto_import = False


@api_controller("/token", permissions=[AllowAny], tags=["token"], auth=None)
class AsyncNinjaJWTSlidingController(
    ControllerBase, AsyncTokenVerificationController, AsyncTokenObtainSlidingController
):
    """
    NinjaJWT Async Sliding controller for obtaining and refreshing tokens
    Add 'ninja_jwt.tokens.SlidingToken' in AUTH_TOKEN_CLASSES in Settings
    """

    auto_import = False
