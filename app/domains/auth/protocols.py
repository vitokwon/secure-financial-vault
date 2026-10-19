"""
app/domains/auth/protocols.py
Abstract interfaces for password hashing and JWT token operations.
"""

from typing import Protocol, runtime_checkable

from app.domains.auth.models import TokenPayload, UserRole


@runtime_checkable
class PasswordHasherProtocol(Protocol):
    """Contract for salted password hashing and timing-safe verification."""

    def hash_password(self, plain_password: str) -> str:
        """Hashes raw password with random salt using Bcrypt."""
        ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies plaintext against Bcrypt hash in constant time."""
        ...


@runtime_checkable
class TokenEngineProtocol(Protocol):
    """Contract for tamper-resistant JWT token generation and validation."""

    def issue_token(self, username: str, role: UserRole) -> str:
        """Issues an authenticated HS256 JWT access token."""
        ...

    def verify_token(self, token: str) -> TokenPayload:
        """Decodes and validates JWT token integrity and expiration."""
        ...
