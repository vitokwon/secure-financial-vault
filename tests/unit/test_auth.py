"""
tests/unit/test_auth.py
Unit tests verifying Bcrypt password hashing and JWT RBAC token lifecycle.
"""

import base64
import json
from datetime import UTC, datetime

import pytest

from app.domains.auth.hasher import BcryptPasswordHasher
from app.domains.auth.models import UserRole
from app.domains.auth.protocols import PasswordHasherProtocol, TokenEngineProtocol
from app.domains.auth.token_engine import JwtTokenEngine

TEST_SECRET = "supersecretjwtkeyforvaulttestingsuite2026"


@pytest.fixture
def password_hasher():
    return BcryptPasswordHasher()


@pytest.fixture
def token_engine():
    return JwtTokenEngine(secret_key=TEST_SECRET, algorithm="HS256", expire_minutes=15)


def test_auth_protocols_conformance(password_hasher, token_engine):
    """Verify runtime conformance against Protocol contracts."""
    assert isinstance(password_hasher, PasswordHasherProtocol)
    assert isinstance(token_engine, TokenEngineProtocol)


def test_password_hashing_and_verification(password_hasher):
    """Verify Bcrypt salt generation and password match."""
    password = "CorrectFinancialVaultPassword#2026"
    hashed = password_hasher.hash_password(password)

    # Assert hash is salted Bcrypt format ($2b$)
    assert hashed != password
    assert hashed.startswith("$2b$")

    # Assert correct verification
    assert password_hasher.verify_password(password, hashed) is True
    # Assert wrong password rejection
    assert password_hasher.verify_password("WrongPassword123", hashed) is False


def test_empty_password_rejected(password_hasher):
    """Verify that empty passwords cannot be hashed."""
    with pytest.raises(ValueError, match="Password cannot be empty"):
        password_hasher.hash_password("")


def test_token_issue_and_verification_cycle(token_engine):
    """Verify issuing and decoding a signed JWT token."""
    username = "auditor_david"
    role = UserRole.AUDITOR

    token = token_engine.issue_token(username=username, role=role)
    assert isinstance(token, str)

    payload = token_engine.verify_token(token)
    assert payload.sub == username
    assert payload.role == UserRole.AUDITOR
    assert payload.exp > datetime.now(UTC)


def test_tampered_token_rejected(token_engine):
    """Verify that modified token payload triggers signature failure."""
    token = token_engine.issue_token(username="staff_user", role=UserRole.STAFF)

    # Tamper with the token string signature
    tampered_token = token[:-4] + "abcd"

    with pytest.raises(ValueError, match="Invalid, tampered, or expired token"):
        token_engine.verify_token(tampered_token)


def test_expired_token_rejected():
    """Verify that expired tokens are immediately rejected."""
    expired_engine = JwtTokenEngine(
        secret_key=TEST_SECRET,
        algorithm="HS256",
        expire_minutes=-1,  # Already expired
    )
    token = expired_engine.issue_token(username="staff_user", role=UserRole.STAFF)

    with pytest.raises(ValueError, match="Invalid, tampered, or expired token"):
        expired_engine.verify_token(token)


def test_insecure_algorithm_token_rejected(token_engine):
    """
    STRIDE S2 Defense: Reject tokens crafted with alg=none.
    Manually constructs an unverified alg=none JWT string to simulate attack payload.
    """
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = (
        base64.urlsafe_b64encode(json.dumps({"sub": "attacker", "role": "admin"}).encode())
        .decode()
        .rstrip("=")
    )
    forged_none_token = f"{header}.{payload}."

    with pytest.raises(ValueError, match="Invalid, tampered, or expired token"):
        token_engine.verify_token(forged_none_token)
