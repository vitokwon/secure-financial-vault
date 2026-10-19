"""
app/domains/auth/__init__.py
Public facade interface for the Authentication & RBAC domain.
"""

from .hasher import BcryptPasswordHasher
from .models import TokenPayload, TokenResponse, User, UserRole
from .protocols import PasswordHasherProtocol, TokenEngineProtocol
from .token_engine import JwtTokenEngine

__all__ = [
    "UserRole",
    "User",
    "TokenPayload",
    "TokenResponse",
    "PasswordHasherProtocol",
    "TokenEngineProtocol",
    "BcryptPasswordHasher",
    "JwtTokenEngine",
]