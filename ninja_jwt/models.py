from typing import Any

from django.contrib.auth import models as auth_models
from django.db.models.manager import EmptyManager
from django.utils.functional import cached_property

from .compat import CallableFalse, CallableTrue
from .settings import api_settings


class TokenUser:
    """
    A dummy user class modeled after django.contrib.auth.models.AnonymousUser.
    Used in conjunction with the `JWTStatelessUserAuthentication` backend to
    implement single sign-on functionality across services which share the same
    secret key.  `JWTStatelessUserAuthentication` will return an instance of this
    class instead of a `User` model instance.  Instances of this class act as
    stateless user objects which are backed by validated tokens.
    """

    # User is always active since Simple JWT will never issue a token for an
    # inactive user
    is_active = True

    _groups = EmptyManager(auth_models.Group)
    _user_permissions = EmptyManager(auth_models.Permission)

    def __init__(self, token: Any) -> None:
        self.token = token

    def __str__(self) -> str:
        return "TokenUser {}".format(self.id)

    @cached_property
    def id(self) -> Any:
        return self.token[api_settings.USER_ID_CLAIM]

    @cached_property
    def pk(self) -> Any:
        return self.id

    @cached_property
    def username(self) -> str:
        return self.token.get("username", "")

    @cached_property
    def is_staff(self) -> bool:
        return self.token.get("is_staff", False)

    @cached_property
    def is_superuser(self) -> bool:
        return self.token.get("is_superuser", False)

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def save(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def delete(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def set_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def check_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    @property
    def groups(self) -> EmptyManager:
        return self._groups

    @property
    def user_permissions(self) -> EmptyManager:
        return self._user_permissions

    def get_group_permissions(self, obj=None) -> set:
        return set()

    def get_all_permissions(self, obj=None) -> set:
        return set()

    def has_perm(self, perm, obj=None) -> bool:
        return False

    def has_perms(self, perm_list, obj=None) -> bool:
        return False

    def has_module_perms(self, module) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return CallableFalse

    @property
    def is_authenticated(self) -> bool:
        return CallableTrue

    def get_username(self) -> str:
        return self.username

    def __getattr__(self, attr):
        """This acts as a backup attribute getter for custom claims defined in Token serializers."""
        return self.token.get(attr, None)
