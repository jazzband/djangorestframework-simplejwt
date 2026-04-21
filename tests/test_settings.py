import pytest

from rest_framework_simplejwt.settings import DEFAULTS, IMPORT_STRINGS, APISettings


def test_validation_mode_must_be_supported():
    with pytest.raises(RuntimeError, match="AUDIENCE_VALIDATION"):
        APISettings(
            {"AUDIENCE_VALIDATION": "invalid"},
            DEFAULTS,
            IMPORT_STRINGS,
        )

@pytest.mark.parametrize(
    "value",
    ["", " ", 1, [], ["issuer", ""], ["issuer", 1]],
)
def test_issuer_must_be_non_empty_string_or_string_sequence(value):
    with pytest.raises(RuntimeError, match="ISSUER"):
        APISettings(
            {
                "ISSUER": value,
            },
            DEFAULTS,
            IMPORT_STRINGS,
        )


def test_issuer_sequence_is_valid():
    settings = APISettings(
        {
            "ISSUER": ["https://issuer.example"],
        },
        DEFAULTS,
        IMPORT_STRINGS,
    )

    assert settings.ISSUER == ["https://issuer.example"]
