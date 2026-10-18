import base64
import importlib
import sys

import pytest


VALID_AES_KEY = base64.urlsafe_b64encode(b"a" * 32).decode("ascii")
VALID_JWT_SECRET = "j" * 32
CONFIG_ENV_KEYS = [
    "FERNET_SECRET_KEY",
    "JWT_SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
]


def _import_config_with_env(monkeypatch: pytest.MonkeyPatch, overrides: dict | None = None):
    defaults = {
        "FERNET_SECRET_KEY": VALID_AES_KEY,
        "JWT_SECRET_KEY": VALID_JWT_SECRET,
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "15",
    }
    for key in CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    for key, value in {**defaults, **(overrides or {})}.items():
        monkeypatch.setenv(key, str(value))

    sys.modules.pop("app.config", None)
    return importlib.import_module("app.config")


def test_valid_aes_key_and_valid_jwt_secret_accepted(monkeypatch):
    config_module = _import_config_with_env(monkeypatch)

    assert config_module.settings.algorithm == "HS256"
    assert config_module.settings.access_token_expire_minutes == 15


def test_invalid_base64_aes_key_rejected(monkeypatch):
    with pytest.raises(ValueError, match="valid URL-safe Base64"):
        _import_config_with_env(monkeypatch, {"FERNET_SECRET_KEY": "not-valid-base64!!"})


def test_aes_key_wrong_decoded_length_rejected(monkeypatch):
    short_key = base64.urlsafe_b64encode(b"b" * 16).decode("ascii")

    with pytest.raises(ValueError, match="decode to exactly 32 bytes"):
        _import_config_with_env(monkeypatch, {"FERNET_SECRET_KEY": short_key})


def test_jwt_secret_shorter_than_32_bytes_rejected(monkeypatch):
    with pytest.raises(ValueError, match="at least 32 UTF-8 bytes"):
        _import_config_with_env(monkeypatch, {"JWT_SECRET_KEY": "too-short"})


def test_algorithm_other_than_hs256_rejected(monkeypatch):
    with pytest.raises(ValueError, match="ALGORITHM must be HS256"):
        _import_config_with_env(monkeypatch, {"ALGORITHM": "HS512"})


@pytest.mark.parametrize("invalid_minutes", [0, 16])
def test_access_token_lifetime_outside_range_rejected(monkeypatch, invalid_minutes):
    with pytest.raises(ValueError, match="between 1 and 15"):
        _import_config_with_env(monkeypatch, {"ACCESS_TOKEN_EXPIRE_MINUTES": invalid_minutes})
