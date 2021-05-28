import fnmatch
import os
from pathlib import Path

from django.db import migrations, models

parent_dir = Path(__file__).resolve(strict=True).parent


class Migration(migrations.Migration):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependencies = [
            ('token_blacklist', '0010_fix_migrate_to_bigautofield')
        ]
        _m = sorted(fnmatch.filter(os.listdir(parent_dir), "000*.py"))
        if len(_m) == 9:
            self.dependencies.insert(0, ('token_blacklist', os.path.splitext(_m[8])[0]))

    operations = [
    ]
