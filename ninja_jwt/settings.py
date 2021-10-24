from datetime import timedelta
from typing import Optional, Type, Union, TYPE_CHECKING, List, Tuple
from ninja_schema import Schema
from pydantic import Field, AnyUrl, root_validator
from .lazy import LazyStrImport, LazyObject

from django.conf import settings
if TYPE_CHECKING:
    from .tokens import Token

class SimpleJWTUserDefinedSettings:
    def __init__(self, data:dict) -> None:
        self.__dict__ = data

SimpleJWT_SETTINGS_DEFAULTS = dict(
    USER_AUTHENTICATION_RULE='ninja_jwt.authentication.default_user_authentication_rule',
    AUTH_TOKEN_CLASSES=['ninja_jwt.tokens.AccessToken'],
    TOKEN_USER_CLASS='ninja_jwt.models.TokenUser'
)

USER_SETTINGS = SimpleJWTUserDefinedSettings(getattr(settings, 'SIMPLE_JWT', SimpleJWT_SETTINGS_DEFAULTS))


class SimpleJWTSettings(Schema):
    class Config:
        orm_mode = True

    ACCESS_TOKEN_LIFETIME: timedelta = Field(timedelta(minutes=5))
    REFRESH_TOKEN_LIFETIME: timedelta = Field(timedelta(minutes=5))
    ROTATE_REFRESH_TOKENS: bool = Field(False)
    BLACKLIST_AFTER_ROTATION: bool = Field(False)
    UPDATE_LAST_LOGIN: bool = Field(False)
    ALGORITHM: str = Field('HS256')
    SIGNING_KEY: str = Field(settings.SECRET_KEY)
    VERIFYING_KEY: Optional[str] = Field(None)
    AUDIENCE: Optional[str] = Field(None)
    ISSUER: Optional[str] = Field(None)
    JWK_URL: Optional[AnyUrl] = Field(None)
    LEEWAY: Union[int, timedelta] = Field(0)

    AUTH_HEADER_TYPES: Tuple[str] = Field(('Bearer',))
    AUTH_HEADER_NAME: str = Field('HTTP_AUTHORIZATION')

    USER_ID_FIELD: str = Field('id')
    USER_ID_CLAIM: str = Field('user_id')

    USER_AUTHENTICATION_RULE: Union[str, Type[LazyObject]] = Field('ninja_jwt.authentication.default_user_authentication_rule')
    TOKEN_USER_CLASS: Union[str, Type[LazyObject]] = Field('ninja_jwt.models.TokenUser')
    AUTH_TOKEN_CLASSES: Union[List[str], List[Type[LazyObject]]] = Field(['ninja_jwt.tokens.AccessToken'])

    TOKEN_TYPE_CLAIM: str = Field('token_type')
    JTI_CLAIM: str = Field('jti')
    SLIDING_TOKEN_REFRESH_EXP_CLAIM: str = Field('refresh_exp')
    SLIDING_TOKEN_LIFETIME: timedelta = Field(timedelta(minutes=5))
    SLIDING_TOKEN_REFRESH_LIFETIME: timedelta = Field(timedelta(minutes=5))

    @root_validator()
    def validate_settings(cls, values):
        values['USER_AUTHENTICATION_RULE'] = LazyStrImport(values['USER_AUTHENTICATION_RULE'])
        values['TOKEN_USER_CLASS'] = LazyStrImport(values['TOKEN_USER_CLASS'])

        auth_token_classes = values["AUTH_TOKEN_CLASSES"]
        _values = [auth_token_classes] if not isinstance(auth_token_classes, (list, tuple)) else auth_token_classes

        values["AUTH_TOKEN_CLASSES"] = [LazyStrImport(klass) for klass in _values]
        return values


api_settings = SimpleJWTSettings.from_orm(USER_SETTINGS)