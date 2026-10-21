"""
app/domains/telemetry/router.py
Auditor endpoints: Restricted access to immutable security audit logs.
"""

from fastapi import APIRouter, Depends

from app.dependencies import RequireRoles, get_audit_logger
from app.domains.auth.models import TokenPayload, UserRole
from app.telemetry.models import AuditEvent, AuditEventType
from app.telemetry.protocols import AuditLoggerProtocol

router = APIRouter(prefix="/audit", tags=["Security Telemetry & Compliance"])

# Strict RBAC: Only Auditor and Admin can inspect audit logs
AllowAuditorOnly = RequireRoles([UserRole.AUDITOR, UserRole.ADMIN])


@router.get("/logs", response_model=list[AuditEvent])
def retrieve_audit_logs(
    limit: int = 50,
    event_type: AuditEventType | None = None,
    actor_id: str | None = None,
    caller: TokenPayload = Depends(AllowAuditorOnly),
    audit_logger: AuditLoggerProtocol = Depends(get_audit_logger),
):
    """
    Returns immutable chronological audit events. Restricted to AUDITOR and ADMIN roles.
    """
    return audit_logger.get_events(limit=limit, event_type=event_type, actor_id=actor_id)
