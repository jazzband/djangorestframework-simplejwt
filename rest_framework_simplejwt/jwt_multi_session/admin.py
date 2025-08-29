from django.contrib import admin

from .models import JWTSession


@admin.register(JWTSession)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at", "expired_at"]
    list_display_links = ["id", "user"]
    search_fields = ["id"]
    list_filter = ["created_at", "expired_at"]

    def has_add_permission(self, request):
        """Check if the user has permission to add the model."""
        return False

    def has_change_permission(self, request, *args):
        """Check if the user has permission to change the model."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Check if the user has permission to change the model."""
        return True
