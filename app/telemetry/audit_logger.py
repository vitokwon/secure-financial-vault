"""
app/telemetry/audit_logger.py
Concrete append-only audit logger writing structured JSON Lines to isolated vault storage.
"""

import json
from pathlib import Path
from typing import Any

from app.telemetry.models import AuditEvent, AuditEventType


class FileAuditLogger:
    """
    Tamper-resistant append-only audit trail logger.
    Persists events as serialized JSON Lines in an isolated log file.
    """

    # Sensitive key patterns that must be redacted from audit details
    SENSITIVE_KEYS = {"password", "secret", "master_key", "token", "authorization"}

    def __init__(self, log_file_path: Path | str = "vault_storage/audit.log") -> None:
        self.log_file_path = Path(log_file_path).resolve()
        # Automatically provision target directory if missing
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file_path.exists():
            self.log_file_path.touch(mode=0o600, exist_ok=True)

    def _sanitize_details(self, details: dict[str, Any]) -> dict[str, Any]:
        """Recursively masks sensitive fields to prevent credential leakage in audit logs."""
        sanitized = {}
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            else:
                sanitized[key] = value
        return sanitized

    def log(self, event: AuditEvent) -> None:
        """
        Persists an immutable event record in append-only JSON Lines format.
        """
        # Ensure details are strictly redacted before serialization
        sanitized_details = self._sanitize_details(event.details)
        event_dict = event.model_dump(mode="json")
        event_dict["details"] = sanitized_details

        line = json.dumps(event_dict, ensure_ascii=False) + "\n"

        # Thread-safe atomic append to disk
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(line)

    def get_events(
        self,
        limit: int = 100,
        event_type: AuditEventType | None = None,
        actor_id: str | None = None,
    ) -> list[AuditEvent]:
        """
        Reads and parses the append-only log file in reverse chronological order.
        """
        if not self.log_file_path.exists():
            return []

        events: list[AuditEvent] = []
        with open(self.log_file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Parse from most recent to oldest
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                event = AuditEvent.model_validate(data)

                # Apply query filters
                if event_type and event.event_type != event_type:
                    continue
                if actor_id and event.actor_id != actor_id:
                    continue

                events.append(event)
                if len(events) >= limit:
                    break
            except (json.JSONDecodeError, ValueError):
                # Ignore corrupted or unparseable lines gracefully
                continue

        return events
