"""
app/telemetry/models.py
Structured event schemas and data models for security telemetry and audit trails.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditEventType(StrEnum):
    """Enumeration of critical security audit event types."""

    # Authentication events
    AUTH_LOGIN_SUCCESS = "AUTH_LOGIN_SUCCESS"
    AUTH_LOGIN_FAILURE = "AUTH_LOGIN_FAILURE"

    # Vault cryptographic storage events
    VAULT_UPLOAD = "VAULT_UPLOAD"
    VAULT_DOWNLOAD = "VAULT_DOWNLOAD"

    # Access control & Security exceptions
    ACCESS_DENIED = "ACCESS_DENIED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"


class AuditEvent(BaseModel):
    """
    Immutable structured security event model.
    Encapsulates all relevant metadata required for STRIDE Non-Repudiation (R).
    """

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique cryptographically secure identifier for the event.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="ISO 8601 UTC timestamp of event generation.",
    )
    event_type: AuditEventType = Field(..., description="Categorized security event type.")
    actor_id: str = Field(..., description="Subject identity (User ID or system entity).")
    actor_role: str | None = Field(
        default=None,
        description="RBAC role assigned to the actor at execution time.",
    )
    target_resource_id: str | None = Field(
        default=None,
        description="Target document ID, file identifier, or affected resource.",
    )
    status: str = Field(
        default="SUCCESS",
        description="Execution outcome: SUCCESS, FAILURE, or BLOCKED.",
    )
    client_ip: str | None = Field(
        default="127.0.0.1",
        description="Client IP address initiating the transaction.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Sanitized non-sensitive metadata. Passwords/keys must never be passed.",
    )
