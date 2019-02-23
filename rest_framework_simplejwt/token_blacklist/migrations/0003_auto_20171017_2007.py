from uuid import UUID

from django.db import migrations


def populate_jti_hex(apps, schema_editor):
    OutstandingToken = apps.get_model('token_blacklist', 'OutstandingToken')

    for token in OutstandingToken.objects.all():
        token.jti_hex = token.jti.hex
        token.save()


def reverse_populate_jti_hex(apps, schema_editor):  # pragma: no cover
    OutstandingToken = apps.get_model('token_blacklist', 'OutstandingToken')

    for token in OutstandingToken.objects.all():
        token.jti = UUID(hex=token.jti_hex)
        token.save()


class Migration(migrations.Migration):

    dependencies = [
        ('token_blacklist', '0002_outstandingtoken_jti_hex'),
    ]

    operations = [
        migrations.RunPython(populate_jti_hex, reverse_populate_jti_hex),
    ]
