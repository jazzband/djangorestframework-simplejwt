from datetime import datetime
from typing import Any, Optional, TypeVar

from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from ..models import TokenUser
from .models import BlacklistedTokenFamily, TokenFamily

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class TokenFamilyAdmin(admin.ModelAdmin):
    list_display = (
        "family_id",
        "user",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "user__id",
        "family_id",
    )
    ordering = ("user",)

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        qs = super().get_queryset(*args, **kwargs)

        return qs.select_related("user")

    # Read-only behavior defined below
    actions = None

    def get_readonly_fields(self, *args, **kwargs) -> list[Any]:
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(
        self, request: Request, obj: Optional[object] = None
    ) -> bool:
        return request.method in ["GET", "HEAD"] and super().has_change_permission(
            request, obj
        )


admin.site.register(TokenFamily, TokenFamilyAdmin)


class BlacklistedTokenFamilyAdmin(admin.ModelAdmin):
    list_display = (
        "family_id",
        "family_user",
        "family_created_at",
        "family_expires_at",
        "blacklisted_at",
    )
    search_fields = (
        "family__user__id",
        "family__family_id",
    )
    ordering = ("family__user",)

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        qs = super().get_queryset(*args, **kwargs)

        return qs.select_related("family__user")

    def family_id(self, obj: BlacklistedTokenFamily) -> str:
        return obj.family.family_id

    family_id.short_description = _("family id")  # type: ignore
    family_id.admin_order_field = "family__family_id"  # type: ignore

    def family_user(self, obj: BlacklistedTokenFamily) -> AuthUser:
        return obj.family.user

    family_user.short_description = _("user")  # type: ignore
    family_user.admin_order_field = "family__user"  # type: ignore

    def family_created_at(self, obj: BlacklistedTokenFamily) -> datetime:
        return obj.family.created_at

    family_created_at.short_description = _("created at")  # type: ignore
    family_created_at.admin_order_field = "family__created_at"  # type: ignore

    def family_expires_at(self, obj: BlacklistedTokenFamily) -> datetime:
        return obj.family.expires_at

    family_expires_at.short_description = _("expires at")  # type: ignore
    family_expires_at.admin_order_field = "family__expires_at"  # type: ignore


admin.site.register(BlacklistedTokenFamily, BlacklistedTokenFamilyAdmin)
