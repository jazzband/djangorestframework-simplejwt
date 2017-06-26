from __future__ import unicode_literals

from django.contrib import admin

from .models import OutstandingToken, BlacklistedToken


class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'jti',
        'token',
        'created_at',
        'expires_at',
    )

    def get_queryset(self, *args, **kwargs):
        qs = super(BlacklistedTokenAdmin, self).get_queryset(*args, **kwargs)

        return qs.select_related('user')

admin.site.register(OutstandingToken, OutstandingTokenAdmin)


class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = (
        'token__user',
        'token__token',
        'token__created_at',
        'token__expires_at',
        'blacklisted_at',
    )

    def get_queryset(self, *args, **kwargs):
        qs = super(BlacklistedTokenAdmin, self).get_queryset(*args, **kwargs)

        return qs.select_related('token__user')

admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
