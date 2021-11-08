from django.urls import path
from ninja_extra import NinjaExtraAPI, permissions, router

from ninja_jwt.controller import (
    NinjaJWTDefaultController,
    TokenBlackListController,
    TokenObtainSlidingController,
)

from .views import TestAPIController

sliding_router = router(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
    controller=TokenObtainSlidingController,
)

blacklist_router = router(
    "/token",
    permissions=[permissions.AllowAny],
    tags=["token"],
    controller=TokenBlackListController,
)

api = NinjaExtraAPI(urls_namespace="jwt")
api.add_controller_router(sliding_router, blacklist_router)
api.register_controllers(NinjaJWTDefaultController, TestAPIController)


urlpatterns = [
    path("api/", api.urls),
]
