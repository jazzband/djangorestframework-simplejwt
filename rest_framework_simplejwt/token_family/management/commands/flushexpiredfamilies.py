from django.core.management.base import BaseCommand

from rest_framework_simplejwt.utils import aware_utcnow

from ...models import TokenFamily


class Command(BaseCommand):
    help = "Flushes expired token families that have a defined expiration date. Families without an expiration date are not affected."

    def handle(self, *args, **kwargs) -> None:
        TokenFamily.objects.filter(expires_at__lte=aware_utcnow()).delete()
