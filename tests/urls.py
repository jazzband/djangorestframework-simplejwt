import django
from django.urls import path
from ninja_extra import NinjaExtraAPI, api_controller, permissions

from ninja_jwt import controller

from . import views

TokenObtainSlidingController = api_controller(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
)(controller.TokenObtainSlidingController)

TokenBlackListController = api_controller(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
)(controller.TokenBlackListController)

api = NinjaExtraAPI(urls_namespace="jwt")
api.register_controllers(
    controller.NinjaJWTDefaultController,
    views.TestAPIController,
    TokenObtainSlidingController,
    TokenBlackListController,
)


urlpatterns = [
    path("api/", api.urls),
]

if not django.VERSION < (3, 1):
    AsyncTokenObtainSlidingController = api_controller(
        "/token-async",
        permissions=[permissions.AllowAny],
        tags=["token-async"],
    )(controller.AsyncTokenObtainSlidingController)

    AsyncTokenBlackListController = api_controller(
        "/token-async",
        permissions=[permissions.AllowAny],
        tags=["token-async"],
    )(controller.AsyncTokenBlackListController)

    async_api = NinjaExtraAPI(urls_namespace="jwt-async")
    async_api.register_controllers(
        controller.AsyncNinjaJWTDefaultController,
        views.TestAPIAsyncController,
        AsyncTokenObtainSlidingController,
        AsyncTokenBlackListController,
    )

    urlpatterns += [
        path("api/async/", async_api.urls),
    ]
