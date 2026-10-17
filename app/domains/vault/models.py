"""
app/domains/vault/models.py
Data models and envelope structures for securely stored vault documents.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EncryptedEnvelope(BaseModel):
    """
    Metadata envelope encapsulating cryptographic attributes and storage parameters.
    Stored alongside or wrapped around encrypted binary blobs.
    """

    file_id: str = Field(..., description="Unique UUID identifying the stored file.")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Sanitized original document name.")
    sha256_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 fingerprint of the raw plaintext.")
    size_bytes: int = Field(..., ge=0, description="Size of the raw unencrypted file in bytes.")
    content_type: str = Field(default="application/octet-stream", description="MIME type of the payload.")
    owner_id: Optional[str] = Field(default=None, description="User identifier associated with document ownership.")
    stored_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of ingestion.")

    @field_validator("sha256_hash")
    @classmethod
    def validate_sha256_hex(cls, value: str) -> str:
        """Validates that the SHA-256 string is a valid 64-character hexadecimal digest."""
        if not all(c in "0123456789abcdefABCDEF" for c in value):
            raise ValueError("[VALIDATION ERROR] sha256_hash must be a valid hexadecimal string.")
        return value.lower()