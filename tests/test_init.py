from django.test import SimpleTestCase

import rest_framework_simplejwt


class TestInit(SimpleTestCase):
    def test_package_version_is_available(self):
        """Test that the package version is available."""
        self.assertIsNotNone(rest_framework_simplejwt.__version__)
        self.assertIsInstance(rest_framework_simplejwt.__version__, str)
