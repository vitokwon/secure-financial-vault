"""
app/telemetry/protocols.py
Defines abstract contracts for security telemetry logging and audit trail inspection.
"""

from typing import Protocol, runtime_checkable

from app.telemetry.models import AuditEvent, AuditEventType


@runtime_checkable
class AuditLoggerProtocol(Protocol):
    """
    Contract defining append-only audit event logging and secure retrieval.
    """

    def log(self, event: AuditEvent) -> None:
        """
        Appends an immutable audit event record to the persistence layer.

        :param event: Validated AuditEvent instance.
        """
        ...

    def get_events(
        self,
        limit: int = 100,
        event_type: AuditEventType | None = None,
        actor_id: str | None = None,
    ) -> list[AuditEvent]:
        """
        Queries and retrieves audit event records for inspection by authorized auditors.

        :param limit: Maximum number of recent events to return.
        :param event_type: Optional filter by specific event category.
        :param actor_id: Optional filter by initiating user identity.
        :return: List of deserialized AuditEvent models.
        """
        ...
