from importlib import reload
from importlib.metadata import PackageNotFoundError
from unittest.mock import Mock, patch

from django.test import SimpleTestCase


class TestInit(SimpleTestCase):
    def test_package_is_not_installed(self):
        with patch(
            "importlib.metadata.version", Mock(side_effect=PackageNotFoundError)
        ):
            import rest_framework_simplejwt.__init__

            self.assertEqual(rest_framework_simplejwt.__init__.__version__, None)

        # Restore origin package without mock
        reload(rest_framework_simplejwt.__init__)
