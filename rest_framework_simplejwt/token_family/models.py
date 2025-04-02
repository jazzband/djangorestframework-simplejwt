from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TokenFamily(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='token_families'
    )

    family_id = models.CharField(unique=True, null=False, max_length=255)  # Unique token family identifier
    
    created_at = models.DateTimeField(null=False, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Token Family")
        verbose_name_plural = _("Token Families")
  
    def __str__(self) -> str:
        return _("Token Family for %(user)s (%(family_id)s)") % {
            "user": self.user,
            "family_id": self.family_id,
        }


class TokenFamilyBlacklist(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    family = models.OneToOneField(TokenFamily, on_delete=models.CASCADE, related_name="blacklisted")

    blacklisted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Token Family Blacklist")
        verbose_name_plural = _("Blacklisted Token Families")

    def __str__(self) -> str:
        return _("Blacklisted Token Family (%(family_id)s) for %(user)s") % {
            "family_id": self.family.family_id,
            "user": self.family.user,
        }
  