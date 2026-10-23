"""app/domains/vault/router.py

Controller handling secure financial document uploads, AES-256-GCM encryption,
and SHA-256 integrity verification.
"""

import hashlib
import io
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.dependencies import (
    RequireRoles,
    get_audit_logger,
    get_cipher_engine,
    get_vault_storage,
)
from app.domains.auth.models import TokenPayload, UserRole
from app.domains.crypto.protocols import CipherEngineProtocol
from app.domains.vault.models import EncryptedEnvelope
from app.domains.vault.protocols import VaultStorageProtocol
from app.telemetry.models import AuditEvent, AuditEventType
from app.telemetry.protocols import AuditLoggerProtocol

router = APIRouter(prefix="/vault", tags=["Secure Financial Vault"])


class DocumentUploadResponse(BaseModel):
    """Response payload returned upon successful encrypted file persistence."""

    file_id: str
    filename: str
    sha256_fingerprint: str
    uploaded_by: str
    created_at: str


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: TokenPayload = Depends(RequireRoles([UserRole.ADMIN, UserRole.STAFF])),
    cipher: CipherEngineProtocol = Depends(get_cipher_engine),
    storage: VaultStorageProtocol = Depends(get_vault_storage),
    audit_logger: AuditLoggerProtocol = Depends(get_audit_logger),
):
    """Uploads a plaintext document, calculates SHA-256 integrity digest,

    encrypts via AES-256-GCM, and persists ciphertext to isolated vault storage.
    """
    # 1. Read raw plaintext payload from multipart form
    plaintext_bytes = await file.read()
    if not plaintext_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # 2. Compute SHA-256 integrity digest directly to ensure standard compliance
    sha256_digest = hashlib.sha256(plaintext_bytes).hexdigest()

    # 3. Encrypt plaintext payload using AES-256-GCM authenticated cipher
    try:
        ciphertext = cipher.encrypt(plaintext_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cryptographic encryption failed: {str(exc)}",
        ) from exc

    # 4. Construct EncryptedEnvelope metadata matching schema validation constraints
    file_id = str(uuid.uuid4())
    now_utc = datetime.now(UTC)
    envelope = EncryptedEnvelope(
        file_id=file_id,
        original_filename=file.filename or "unknown",
        sha256_hash=sha256_digest,
        size_bytes=len(plaintext_bytes),
        content_type=file.content_type or "application/octet-stream",
        owner_id=current_user.sub,
        stored_at=now_utc,
    )

    # 5. Persist encrypted binary blob and metadata envelope to disk
    try:
        storage.save_blob(file_id, ciphertext, envelope)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vault persistence failed: {str(exc)}",
        ) from exc

    # 6. Record tamper-resistant audit event
    audit_logger.log(
        AuditEvent(
            event_type=AuditEventType.VAULT_UPLOAD,
            actor_id=current_user.sub,
            details={
                "file_id": file_id,
                "filename": file.filename,
                "sha256": sha256_digest,
            },
        )
    )

    return DocumentUploadResponse(
        file_id=file_id,
        filename=file.filename or "unknown",
        sha256_fingerprint=sha256_digest,
        uploaded_by=current_user.sub,
        created_at=now_utc.isoformat(),
    )


@router.get("/download/{file_id}")
def download_document(
    file_id: str,
    current_user: TokenPayload = Depends(
        RequireRoles([UserRole.ADMIN, UserRole.AUDITOR, UserRole.STAFF])
    ),
    cipher: CipherEngineProtocol = Depends(get_cipher_engine),
    storage: VaultStorageProtocol = Depends(get_vault_storage),
    audit_logger: AuditLoggerProtocol = Depends(get_audit_logger),
):
    """Reads ciphertext from vault, decrypts via AES-256-GCM,

    and verifies SHA-256 integrity digest prior to streaming plaintext back.
    """
    # 1. Fetch ciphertext binary and metadata envelope from isolated storage
    try:
        ciphertext, envelope = storage.read_blob(file_id)

        if current_user.role == UserRole.STAFF and envelope.owner_id != current_user.sub:
            audit_logger.log(
                AuditEvent(
                    event_type=AuditEventType.ACCESS_DENIED,
                    actor_id=current_user.sub,
                    target_resource_id=file_id,
                    status="BLOCKED",
                )
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    except FileNotFoundError:
        audit_logger.log(
            AuditEvent(
                event_type=AuditEventType.INTEGRITY_FAILURE,
                actor_id=current_user.sub,
                details={
                    "file_id": file_id,
                    "reason": "File not found or missing from storage.",
                },
            )
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' not found.",
        ) from None

    # 2. Decrypt ciphertext and authenticate AEAD tag
    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception:
        audit_logger.log(
            AuditEvent(
                event_type=AuditEventType.INTEGRITY_FAILURE,
                actor_id=current_user.sub,
                details={
                    "file_id": file_id,
                    "reason": "Decryption failed. AEAD tag mismatch or tampering.",
                },
            )
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decryption failed. File may have been tampered with.",
        ) from None

    # 3. Verify SHA-256 integrity fingerprint against recorded envelope digest
    current_digest = hashlib.sha256(plaintext).hexdigest()
    if current_digest != envelope.sha256_hash:
        audit_logger.log(
            AuditEvent(
                event_type=AuditEventType.INTEGRITY_FAILURE,
                actor_id=current_user.sub,
                details={
                    "file_id": file_id,
                    "reason": "SHA-256 fingerprint mismatch detected.",
                },
            )
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Integrity check failed: payload does not match recorded digest."),
        )

    # 4. Audit log successful retrieval event
    audit_logger.log(
        AuditEvent(
            event_type=AuditEventType.VAULT_DOWNLOAD,
            actor_id=current_user.sub,
            details={"file_id": file_id, "filename": envelope.original_filename},
        )
    )

    # 5. Stream decrypted plaintext bytes to authenticated caller
    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type=envelope.content_type,
        headers={"Content-Disposition": (f'attachment; filename="{envelope.original_filename}"')},
    )


@router.post("/tamper-simulate/{file_id}", tags=["Vault"])
def simulate_bit_flip_tampering(file_id: str):
    """[Demo Only] Actually flips one byte of the ciphertext
    within an actual .bin file stored on disk.
    """
    from app.dependencies import get_vault_storage

    storage = get_vault_storage()
    blob_path = storage.base_path / f"{file_id}.bin"
    if not blob_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    data = bytearray(blob_path.read_bytes())
    # Flip one bit (using ^= 1) of the first ciphertext byte
    # (at index 12) following the 12-byte nonce.
    data[12] ^= 0x01
    blob_path.write_bytes(data)
    return {"status": "success", "message": "1-bit flipped on disk at byte index 12"}
