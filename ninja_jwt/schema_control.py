from typing import TYPE_CHECKING, Type

from django.utils.module_loading import import_string

from ninja_jwt.schema import InputSchemaMixin, TokenInputSchemaMixin

if TYPE_CHECKING:  # pragma: no cover
    from ninja_jwt.settings import NinjaJWTSettings


class SchemaControl:
    """
    A Schema Helper Class that imports Schema from configurations
    """

    def __init__(self, api_settings: "NinjaJWTSettings") -> None:
        self._verify_schema = import_string(api_settings.TOKEN_VERIFY_INPUT_SCHEMA)
        self.validate_type(
            self._verify_schema, InputSchemaMixin, "TOKEN_VERIFY_INPUT_SCHEMA"
        )

        self._blacklist_schema = import_string(
            api_settings.TOKEN_BLACKLIST_INPUT_SCHEMA
        )
        self.validate_type(
            self._blacklist_schema, InputSchemaMixin, "TOKEN_BLACKLIST_INPUT_SCHEMA"
        )

        self._obtain_pair_schema = import_string(
            api_settings.TOKEN_OBTAIN_PAIR_INPUT_SCHEMA
        )
        self.validate_type(
            self._obtain_pair_schema,
            TokenInputSchemaMixin,
            "TOKEN_OBTAIN_PAIR_INPUT_SCHEMA",
        )

        self._obtain_pair_refresh_schema = import_string(
            api_settings.TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA
        )

        self.validate_type(
            self._obtain_pair_refresh_schema,
            InputSchemaMixin,
            "TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA",
        )

        self._obtain_sliding_schema = import_string(
            api_settings.TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA
        )
        self.validate_type(
            self._obtain_sliding_schema,
            TokenInputSchemaMixin,
            "TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA",
        )

        self._obtain_sliding_refresh_schema = import_string(
            api_settings.TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA
        )
        self.validate_type(
            self._obtain_sliding_refresh_schema,
            InputSchemaMixin,
            "TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA",
        )

    def validate_type(
        self, schema_type: Type, sub_class: Type, settings_key: str
    ) -> None:
        if not issubclass(schema_type, sub_class):
            raise Exception(f"{settings_key} type must inherit from `{sub_class}`")

    @property
    def verify_schema(self) -> "TokenInputSchemaMixin":
        return self._verify_schema

    @property
    def blacklist_schema(self) -> "TokenInputSchemaMixin":
        return self._blacklist_schema

    @property
    def obtain_pair_schema(self) -> "TokenInputSchemaMixin":
        return self._obtain_pair_schema

    @property
    def obtain_pair_refresh_schema(self) -> "TokenInputSchemaMixin":
        return self._obtain_pair_refresh_schema

    @property
    def obtain_sliding_schema(self) -> "TokenInputSchemaMixin":
        return self._obtain_sliding_schema

    @property
    def obtain_sliding_refresh_schema(self) -> "TokenInputSchemaMixin":
        return self._obtain_sliding_refresh_schema
