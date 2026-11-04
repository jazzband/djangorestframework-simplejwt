from datetime import timedelta

from django.core.signals import setting_changed
from django.test import SimpleTestCase, override_settings

import rest_framework_simplejwt.settings as jwt_settings


class SettingChangedTests(SimpleTestCase):
    def test_uses_django_core_signal(self):
        self.assertIs(jwt_settings.setting_changed, setting_changed)

    def test_module_does_not_import_django_test(self):
        source = open(jwt_settings.__file__, encoding="utf-8").read()
        self.assertNotIn("django.test", source)

    def test_override_settings_reloads_access_token_lifetime(self):
        lifetime = timedelta(minutes=42)
        with override_settings(SIMPLE_JWT={"ACCESS_TOKEN_LIFETIME": lifetime}):
            self.assertEqual(jwt_settings.api_settings.ACCESS_TOKEN_LIFETIME, lifetime)

        self.assertEqual(
            jwt_settings.api_settings.ACCESS_TOKEN_LIFETIME,
            timedelta(minutes=5),
        )
