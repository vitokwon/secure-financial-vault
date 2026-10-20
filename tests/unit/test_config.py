import base64
import importlib

import pytest


def _encoded_key(raw: bytes = b"a" * 32) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _load_config_module(monkeypatch, **env_overrides):
    defaults = {
        "ENCRYPTION_KEY": _encoded_key(),
        "JWT_SECRET_KEY": "j" * 32,
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "15",
    }
    defaults.update(env_overrides)

    for key, value in defaults.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    import app.config as config_module

    return importlib.reload(config_module)


@pytest.mark.parametrize("jwt_secret", ["", "too-short-secret"])
def test_missing_or_short_jwt_secret_rejected(monkeypatch, jwt_secret):
    config_module = _load_config_module(monkeypatch)
    settings = config_module.AppSettings(
        encryption_key=_encoded_key(),
        jwt_secret_key=jwt_secret,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    with pytest.raises(ValueError, match="JWT_SECRET_KEY must be at least 32 bytes"):
        settings.validate_keys()


def test_non_hs256_algorithm_rejected(monkeypatch):
    config_module = _load_config_module(monkeypatch)
    settings = config_module.AppSettings(
        encryption_key=_encoded_key(),
        jwt_secret_key="j" * 32,
        # Intentional insecure value for a negative validation test.
        algorithm="none",  # nosemgrep: sfv.jwt.insecure-none-algorithm
        access_token_expire_minutes=15,
    )
    with pytest.raises(ValueError, match="ALGORITHM must be HS256"):
        settings.validate_keys()


@pytest.mark.parametrize("minutes", [0, 16])
def test_token_lifetime_out_of_range_rejected(monkeypatch, minutes):
    config_module = _load_config_module(monkeypatch)
    settings = config_module.AppSettings(
        encryption_key=_encoded_key(),
        jwt_secret_key="j" * 32,
        algorithm="HS256",
        access_token_expire_minutes=minutes,
    )
    with pytest.raises(ValueError, match="ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 15"):
        settings.validate_keys()


@pytest.mark.parametrize(
    "encryption_key",
    [
        "not-a-valid-base64-key",
        _encoded_key(b"a" * 31),
    ],
)
def test_invalid_encryption_key_format_or_length_rejected(monkeypatch, encryption_key):
    config_module = _load_config_module(monkeypatch)
    settings = config_module.AppSettings(
        encryption_key=encryption_key,
        jwt_secret_key="j" * 32,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    with pytest.raises(ValueError, match="ENCRYPTION_KEY"):
        settings.validate_keys()


def test_valid_local_configuration_passes_validation(monkeypatch):
    config_module = _load_config_module(monkeypatch)
    settings = config_module.AppSettings(
        encryption_key=_encoded_key(),
        jwt_secret_key="j" * 32,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    settings.validate_keys()


def test_legacy_fernet_secret_key_fallback_supported(monkeypatch):
    config_module = _load_config_module(
        monkeypatch,
        ENCRYPTION_KEY=None,
        FERNET_SECRET_KEY=_encoded_key(),
    )
    settings = config_module.AppSettings()
    settings.validate_keys()
