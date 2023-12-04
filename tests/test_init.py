from importlib import reload
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from pkg_resources import DistributionNotFound


class TestInit(SimpleTestCase):
    def test_package_is_not_installed(self):
        with patch(
            "pkg_resources.get_distribution", Mock(side_effect=DistributionNotFound)
        ):
            # Import package mock package is not installed
            import rest_framework_simplejwt.__init__

            self.assertEqual(rest_framework_simplejwt.__init__.__version__, None)

        # Restore origin package without mock
        reload(rest_framework_simplejwt.__init__)
