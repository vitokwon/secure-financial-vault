"""
tests/unit/test_telemetry.py
Automated security test suite verifying append-only audit logging and non-repudiation.
"""

from pathlib import Path

from app.telemetry.audit_logger import FileAuditLogger
from app.telemetry.models import AuditEvent, AuditEventType
from app.telemetry.protocols import AuditLoggerProtocol


def test_audit_logger_protocol_conformance(tmp_path: Path):
    """Verifies that FileAuditLogger satisfies the AuditLoggerProtocol structural typing."""
    log_file = tmp_path / "test_audit.log"
    logger = FileAuditLogger(log_file_path=log_file)
    assert isinstance(logger, AuditLoggerProtocol)


def test_audit_log_append_and_retrieval(tmp_path: Path):
    """Verifies append-only storage and deserialization of multiple security audit events."""
    log_file = tmp_path / "audit.log"
    logger = FileAuditLogger(log_file_path=log_file)

    event1 = AuditEvent(
        event_type=AuditEventType.AUTH_LOGIN_SUCCESS,
        actor_id="user_staff_01",
        actor_role="STAFF",
        status="SUCCESS",
        details={"ip": "192.168.1.10"},
    )
    event2 = AuditEvent(
        event_type=AuditEventType.VAULT_UPLOAD,
        actor_id="user_staff_01",
        actor_role="STAFF",
        target_resource_id="doc-uuid-12345",
        status="SUCCESS",
        details={"filename": "quarterly_balance.pdf"},
    )

    logger.log(event1)
    logger.log(event2)

    # Validate file content has 2 lines (Append-only JSON Lines)
    with open(log_file, encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2

    # Query events back
    events = logger.get_events(limit=10)
    assert len(events) == 2
    # Verify reverse chronological ordering (event2 first)
    assert events[0].event_type == AuditEventType.VAULT_UPLOAD
    assert events[0].target_resource_id == "doc-uuid-12345"
    assert events[1].event_type == AuditEventType.AUTH_LOGIN_SUCCESS
    assert events[1].actor_id == "user_staff_01"


def test_sensitive_credential_redaction(tmp_path: Path):
    """Verifies that passwords or tokens passed in event details are strictly redacted."""
    log_file = tmp_path / "audit.log"
    logger = FileAuditLogger(log_file_path=log_file)

    leak_attempt_event = AuditEvent(
        event_type=AuditEventType.AUTH_LOGIN_FAILURE,
        actor_id="attacker_user",
        actor_role="UNKNOWN",
        status="FAILURE",
        details={
            "attempted_password": "PlaintextPassword123!",
            "token": "secret_jwt_string",
            "nested": {"authorization": "Bearer secret_value", "safe_info": "ok"},
        },
    )

    logger.log(leak_attempt_event)

    # Check raw disk log content
    raw_content = log_file.read_text(encoding="utf-8")
    assert "PlaintextPassword123!" not in raw_content
    assert "secret_jwt_string" not in raw_content
    assert "secret_value" not in raw_content
    assert "[REDACTED]" in raw_content

    # Deserialized check
    fetched = logger.get_events(limit=1)[0]
    assert fetched.details["attempted_password"] == "[REDACTED]"
    assert fetched.details["token"] == "[REDACTED]"
    assert fetched.details["nested"]["authorization"] == "[REDACTED]"
    assert fetched.details["nested"]["safe_info"] == "ok"


def test_audit_event_filtering(tmp_path: Path):
    """Verifies event querying with event_type and actor_id filtering."""
    log_file = tmp_path / "audit.log"
    logger = FileAuditLogger(log_file_path=log_file)

    logger.log(
        AuditEvent(
            event_type=AuditEventType.ACCESS_DENIED,
            actor_id="user_attacker",
            status="BLOCKED",
        )
    )
    logger.log(
        AuditEvent(
            event_type=AuditEventType.VAULT_DOWNLOAD,
            actor_id="user_auditor",
            status="SUCCESS",
        )
    )

    denied_events = logger.get_events(event_type=AuditEventType.ACCESS_DENIED)
    assert len(denied_events) == 1
    assert denied_events[0].actor_id == "user_attacker"

    auditor_events = logger.get_events(actor_id="user_auditor")
    assert len(auditor_events) == 1
    assert auditor_events[0].event_type == AuditEventType.VAULT_DOWNLOAD
