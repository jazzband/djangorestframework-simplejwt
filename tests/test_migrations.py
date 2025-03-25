from io import StringIO
from typing import Optional

import pytest
from django.core.management import call_command
from django.test import TestCase


class MigrationTestCase(TestCase):
    def test_no_missing_migrations(self):
        """
        Ensures all model changes are reflected in migrations.
        If this test fails, there are model changes that require a new migration.

        Behavior:
        - Passes silently if no migrations are required
        - Fails with a detailed message if migrations are need
        """

        output = StringIO()

        # Initialize exception variable to track migration check result
        exec: Optional[SystemExit] = None

        try:
            # Check for pending migrations without actually creating them
            call_command(
                "makemigrations", "--check", "--dry-run", stdout=output, stderr=output
            )
        except SystemExit as e:
            # Capture the SystemExit if migrations are needed (the command will had ended with exit code 1)
            exec = e

        # If an exception was raised, verify it indicates no migration changes are required
        if exec is not None:
            self.assertEqual(
                exec.code,
                0,  # 0 means no migrations needed
                f"Model changes detected that require migrations!\n"
                f"Please run `python manage.py makemigrations` to create the necessary migrations.\n\n"
                f"Detected Changes:\n{output.getvalue()}",
            )
