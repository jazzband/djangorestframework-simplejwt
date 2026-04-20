import pytest

from rest_framework_simplejwt.settings import APISettings, DEFAULTS, IMPORT_STRINGS


def test_validation_mode_must_be_supported():
    with pytest.raises(RuntimeError, match="AUDIENCE_VALIDATION"):
        APISettings(
            {"AUDIENCE_VALIDATION": "invalid"},
            DEFAULTS,
            IMPORT_STRINGS,
        )

    with pytest.raises(RuntimeError, match="ISSUER_VALIDATION"):
        APISettings(
            {"ISSUER_VALIDATION": "invalid"},
            DEFAULTS,
            IMPORT_STRINGS,
        )


@pytest.mark.parametrize("value", ["issuer", ["issuer", ""], ["issuer", 1]])
def test_allowed_issuers_must_contain_non_empty_strings(value):
    with pytest.raises(RuntimeError, match="ALLOWED_ISSUERS"):
        APISettings(
            {
                "ISSUER_VALIDATION": "dynamic",
                "ALLOWED_ISSUERS": value,
            },
            DEFAULTS,
            IMPORT_STRINGS,
        )


def test_allowed_issuers_requires_dynamic_issuer_validation():
    with pytest.raises(RuntimeError, match="ISSUER_VALIDATION"):
        APISettings(
            {
                "ISSUER_VALIDATION": "static",
                "ALLOWED_ISSUERS": ["https://issuer.example"],
            },
            DEFAULTS,
            IMPORT_STRINGS,
        )


def test_dynamic_issuer_validation_rejects_static_issuer_and_allowed_issuers():
    with pytest.raises(RuntimeError, match="ISSUER'.*ALLOWED_ISSUERS"):
        APISettings(
            {
                "ISSUER_VALIDATION": "dynamic",
                "ISSUER": "https://issuer.example",
                "ALLOWED_ISSUERS": ["https://issuer.example"],
            },
            DEFAULTS,
            IMPORT_STRINGS,
        )


def test_allowed_issuers_with_dynamic_validation_is_valid():
    settings = APISettings(
        {
            "ISSUER_VALIDATION": "dynamic",
            "ALLOWED_ISSUERS": ["https://issuer.example"],
        },
        DEFAULTS,
        IMPORT_STRINGS,
    )

    assert settings.ALLOWED_ISSUERS == ["https://issuer.example"]
