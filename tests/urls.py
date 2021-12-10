from django.urls import path
from ninja_extra import NinjaExtraAPI, api_controller, permissions

from ninja_jwt.controller import (
    NinjaJWTDefaultController,
    TokenBlackListController,
    TokenObtainSlidingController,
)

from .views import TestAPIController

TokenObtainSlidingController = api_controller(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
)(TokenObtainSlidingController)

TokenBlackListController = api_controller(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
)(TokenBlackListController)

api = NinjaExtraAPI(urls_namespace="jwt")
api.register_controllers(
    NinjaJWTDefaultController,
    TestAPIController,
    TokenObtainSlidingController,
    TokenBlackListController,
)


urlpatterns = [
    path("api/", api.urls),
]
