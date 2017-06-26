from datetime import datetime

from django.core.management.base import BaseCommand

from ...models import OutstandingToken


class Command(BaseCommand):
    help = 'Flushes any expired tokens in the outstanding token list'

    def handle(self, *args, **kwargs):
        OutstandingToken.objects.filter(expires_at__lte=datetime.utcnow()).delete()
