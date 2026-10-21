"""
app/dependencies.py
Composition Root: Instantiates concrete security engines and provides
FastAPI dependency injection providers according to domain protocols.
"""

from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.domains.auth.hasher import BcryptPasswordHasher
from app.domains.auth.models import TokenPayload, UserRole
from app.domains.auth.token_engine import JwtTokenEngine
from app.domains.crypto.aes_engine import AesGcmCipherEngine
from app.domains.crypto.hasher import Sha256Hasher
from app.domains.crypto.protocols import CipherEngineProtocol, HashEngineProtocol
from app.domains.vault.disk_storage import DiskVaultStorage
from app.domains.vault.protocols import VaultStorageProtocol
from app.telemetry.audit_logger import FileAuditLogger
from app.telemetry.protocols import AuditLoggerProtocol

# HTTP Bearer Security Scheme for Swagger UI
security_bearer = HTTPBearer(auto_error=True)

# ---------------------------------------------------------
# Singletons / Core Providers
# ---------------------------------------------------------


def get_cipher_engine() -> CipherEngineProtocol:
    """Provides authenticated AES-256-GCM cipher engine using configured master key."""
    raw_key = settings.encryption_key.encode("utf-8")[:32]
    return AesGcmCipherEngine(key=raw_key)


def get_hash_engine() -> HashEngineProtocol:
    """Provides constant-time SHA-256 integrity hasher."""
    return Sha256Hasher()


def get_vault_storage() -> VaultStorageProtocol:
    """Provides isolated disk vault persistence targeting configured storage path."""
    return DiskVaultStorage(base_directory=Path(settings.storage_dir))


def get_audit_logger() -> AuditLoggerProtocol:
    """Provides append-only file audit logger with redaction."""
    log_path = Path(settings.storage_dir) / "audit.log"
    return FileAuditLogger(log_file_path=log_path)


def get_token_engine() -> JwtTokenEngine:
    """Provides signed JWT token verification and lifecycle engine."""
    return JwtTokenEngine(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )


def get_password_hasher() -> BcryptPasswordHasher:
    """Provides salted Bcrypt password hasher."""
    return BcryptPasswordHasher()


# ---------------------------------------------------------
# Authentication & RBAC Guards
# ---------------------------------------------------------


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    token_engine: JwtTokenEngine = Depends(get_token_engine),
) -> TokenPayload:
    """
    Validates bearer JWT token from Authorization header and yields caller identity.
    """
    token = credentials.credentials
    try:
        payload = token_engine.verify_token(token)
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired credentials: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class RequireRoles:
    """
    RBAC Authorization guard factory enforcing allowed roles.
    """

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: TokenPayload = Depends(get_current_user),
        audit_logger: AuditLoggerProtocol = Depends(get_audit_logger),
    ) -> TokenPayload:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{current_user.role.value}' "
                "lacks required permissions.",
            )
        return current_user
