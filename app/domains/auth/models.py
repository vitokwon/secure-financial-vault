"""
app/domains/auth/models.py
Domain models and schemas for Authentication and Role-Based Access Control (RBAC).
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    """
    3-Tier RBAC Roles for the Secure Financial Document Vault.
    """

    ADMIN = "admin"  # Master configuration and system administration
    AUDITOR = "auditor"  # Compliance inspection and read-only audit log review
    STAFF = "staff"  # Operational document storage and retrieval


class User(BaseModel):
    """
    Internal user entity holding credentials and authorization metadata.
    """

    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str = Field(..., description="Bcrypt salted password hash")
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)


class TokenPayload(BaseModel):
    """
    Decoded JWT token claims verified against tampering.
    """

    sub: str = Field(..., description="Username subject")
    role: UserRole = Field(..., description="Assigned authorization role")
    exp: datetime = Field(..., description="Token expiration timestamp")


class TokenResponse(BaseModel):
    """
    Bearer token output schema returned upon successful login.
    """

    access_token: str
    token_type: str = "bearer"
