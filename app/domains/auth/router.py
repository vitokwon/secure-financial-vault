"""
app/domains/auth/router.py
Controller handling user authentication, credential validation, and JWT token issuance.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_password_hasher, get_token_engine
from app.domains.auth.hasher import BcryptPasswordHasher
from app.domains.auth.models import UserRole
from app.domains.auth.token_engine import JwtTokenEngine
from app.telemetry.models import AuditEvent, AuditEventType
from app.telemetry.protocols import AuditLoggerProtocol

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

# In-memory Seed Database for Demonstration & Testing
_hasher = BcryptPasswordHasher()
SEED_USERS = {
    "admin_user": {
        "password_hash": _hasher.hash_password("AdminPass123!"),
        "role": UserRole.ADMIN,
    },
    "auditor_user": {
        "password_hash": _hasher.hash_password("AdminPass123!"),
        "role": UserRole.AUDITOR,
    },
    "staff_user": {
        "password_hash": _hasher.hash_password("AdminPass123!"),
        "role": UserRole.STAFF,
    },
}


class LoginRequest(BaseModel):
    username: str = Field(..., description="Registered user account ID")
    password: str = Field(..., min_length=8, description="Account password")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: str
    username: str


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    hasher: BcryptPasswordHasher = Depends(get_password_hasher),
    token_engine: JwtTokenEngine = Depends(get_token_engine),
    audit_logger: AuditLoggerProtocol = Depends(get_audit_logger),
):
    user_record = SEED_USERS.get(req.username)
    if not user_record or not hasher.verify_password(req.password, user_record["password_hash"]):
        audit_logger.log(
            AuditEvent(
                event_type=AuditEventType.AUTH_LOGIN_FAILURE,
                actor_id=req.username,
                details={"reason": "Invalid credentials provided."},
            )
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    # Issue Signed JWT
    user_role = user_record["role"]
    token = token_engine.issue_token(username=req.username, role=user_role)

    audit_logger.log(
        AuditEvent(
            event_type=AuditEventType.AUTH_LOGIN_SUCCESS,
            actor_id=req.username,
            details={"role": user_role.value},
        )
    )

    return LoginResponse(
        access_token=token,
        role=user_role.value,
        username=req.username,
    )
