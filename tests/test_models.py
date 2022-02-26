from django.test import TestCase

from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings

AuthToken = api_settings.AUTH_TOKEN_CLASSES[0]


class TestTokenUser(TestCase):
    def setUp(self):
        self.token = AuthToken()
        self.token[api_settings.USER_ID_CLAIM] = 42
        self.token["username"] = "deep-thought"
        self.token["some_other_stuff"] = "arstarst"

        self.user = TokenUser(self.token)

    def test_username(self):
        self.assertEqual(self.user.username, "deep-thought")

    def test_is_active(self):
        self.assertTrue(self.user.is_active)

    def test_str(self):
        self.assertEqual(str(self.user), "TokenUser 42")

    def test_id(self):
        self.assertEqual(self.user.id, 42)

    def test_pk(self):
        self.assertEqual(self.user.pk, 42)

    def test_is_staff(self):
        payload = {api_settings.USER_ID_CLAIM: 42}
        user = TokenUser(payload)

        self.assertFalse(user.is_staff)

        payload["is_staff"] = True
        user = TokenUser(payload)

        self.assertTrue(user.is_staff)

    def test_is_superuser(self):
        payload = {api_settings.USER_ID_CLAIM: 42}
        user = TokenUser(payload)

        self.assertFalse(user.is_superuser)

        payload["is_superuser"] = True
        user = TokenUser(payload)

        self.assertTrue(user.is_superuser)

    def test_eq(self):
        user1 = TokenUser({api_settings.USER_ID_CLAIM: 1})
        user2 = TokenUser({api_settings.USER_ID_CLAIM: 2})
        user3 = TokenUser({api_settings.USER_ID_CLAIM: 1})

        self.assertNotEqual(user1, user2)
        self.assertEqual(user1, user3)

    def test_hash(self):
        self.assertEqual(hash(self.user), hash(self.user.id))

    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.user.save()

        with self.assertRaises(NotImplementedError):
            self.user.delete()

        with self.assertRaises(NotImplementedError):
            self.user.set_password("arst")

        with self.assertRaises(NotImplementedError):
            self.user.check_password("arst")

    def test_groups(self):
        self.assertFalse(self.user.groups.exists())

    def test_user_permissions(self):
        self.assertFalse(self.user.user_permissions.exists())

    def test_get_group_permissions(self):
        self.assertEqual(len(self.user.get_group_permissions()), 0)

    def test_get_all_permissions(self):
        self.assertEqual(len(self.user.get_all_permissions()), 0)

    def test_has_perm(self):
        self.assertFalse(self.user.has_perm("test_perm"))

    def test_has_perms(self):
        self.assertFalse(self.user.has_perms(["test_perm"]))

    def test_has_module_perms(self):
        self.assertFalse(self.user.has_module_perms("test_module"))

    def test_is_anonymous(self):
        self.assertFalse(self.user.is_anonymous)

    def test_is_authenticated(self):
        self.assertTrue(self.user.is_authenticated)

    def test_get_username(self):
        self.assertEqual(self.user.get_username(), "deep-thought")
