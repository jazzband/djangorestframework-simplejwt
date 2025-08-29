from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import aware_utcnow

User = get_user_model()


class JWTSession(models.Model):
    id = models.UUIDField(
        _("id"), editable=False, unique=True, primary_key=True, default=uuid4
    )
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    device_agent = models.CharField(
        _("User agent"),
        max_length=250,
    )
    device_ip = models.CharField(
        _("Ip Address"),
        max_length=16,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(_("Session expire date"))

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.id)

    @property
    def is_expired(self) -> bool:
        current_time = aware_utcnow()
        return current_time > self.expired_at

    def validate(self) -> bool:
        """
        Validates the given device agent, and IP address, session limit
        """
        return self.is_expired

    def update(self):
        current_time = aware_utcnow()
        self.expired_at = current_time + timedelta(
            seconds=api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
        )
        self.save(update_fields=["expired_at"])

    def save(self, *args, **kwargs):
        current_time = aware_utcnow()

        if not self.expired_at:
            self.expired_at = current_time + timedelta(
                seconds=api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
            )
        super().save(*args, **kwargs)
