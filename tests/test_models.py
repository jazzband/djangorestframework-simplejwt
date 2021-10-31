import pytest
from django.test import TestCase

from ninja_jwt.models import TokenUser
from ninja_jwt.settings import api_settings

AuthToken = api_settings.AUTH_TOKEN_CLASSES[0]


class TestTokenUser:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.token = AuthToken()
        self.token[api_settings.USER_ID_CLAIM] = 42
        self.token["username"] = "deep-thought"
        self.token["some_other_stuff"] = "arstarst"

        self.user = TokenUser(self.token)

    def test_username(self):
        assert self.user.username == "deep-thought"

    def test_is_active(self):
        assert self.user.is_active

    def test_str(self):
        assert str(self.user) == "TokenUser 42"

    def test_id(self):
        assert self.user.id == 42

    def test_pk(self):
        assert self.user.pk == 42

    def test_is_staff(self):
        payload = {api_settings.USER_ID_CLAIM: 42}
        user = TokenUser(payload)

        assert not user.is_staff

        payload["is_staff"] = True
        user = TokenUser(payload)

        assert user.is_staff

    def test_is_superuser(self):
        payload = {api_settings.USER_ID_CLAIM: 42}
        user = TokenUser(payload)

        assert not user.is_superuser

        payload["is_superuser"] = True
        user = TokenUser(payload)

        assert user.is_superuser

    def test_eq(self):
        user1 = TokenUser({api_settings.USER_ID_CLAIM: 1})
        user2 = TokenUser({api_settings.USER_ID_CLAIM: 2})
        user3 = TokenUser({api_settings.USER_ID_CLAIM: 1})

        assert user1 != user2
        assert user1 == user3

    def test_hash(self):
        assert hash(self.user) == hash(self.user.id)

    def test_not_implemented(self):
        with pytest.raises(NotImplementedError):
            self.user.save()

        with pytest.raises(NotImplementedError):
            self.user.delete()

        with pytest.raises(NotImplementedError):
            self.user.set_password("arst")

        with pytest.raises(NotImplementedError):
            self.user.check_password("arst")

    def test_groups(self):
        assert not self.user.groups.exists()

    def test_user_permissions(self):
        assert not self.user.user_permissions.exists()

    def test_get_group_permissions(self):
        assert len(self.user.get_group_permissions()) == 0

    def test_get_all_permissions(self):
        assert len(self.user.get_all_permissions()) == 0

    def test_has_perm(self):
        assert not self.user.has_perm("test_perm")

    def test_has_perms(self):
        assert not self.user.has_perms(["test_perm"])

    def test_has_module_perms(self):
        assert not self.user.has_module_perms("test_module")

    def test_is_anonymous(self):
        assert not self.user.is_anonymous

    def test_is_authenticated(self):
        assert self.user.is_authenticated

    def test_get_username(self):
        assert self.user.get_username() == "deep-thought"
