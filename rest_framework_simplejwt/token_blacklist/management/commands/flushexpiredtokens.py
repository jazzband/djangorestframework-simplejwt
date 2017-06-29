from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import OutstandingToken


class Command(BaseCommand):
    help = 'Flushes any expired tokens in the outstanding token list'

    def handle(self, *args, **kwargs):
        OutstandingToken.objects.filter(expires_at__lte=timezone.now()).delete()
