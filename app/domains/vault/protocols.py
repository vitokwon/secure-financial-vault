"""
app/domains/vault/protocols.py
Defines abstract contracts for secure file storage operations and path resolution.
"""

from pathlib import Path
from typing import Protocol, runtime_checkable
from app.domains.vault.models import EncryptedEnvelope


@runtime_checkable
class VaultStorageProtocol(Protocol):
    """
    Contract defining isolated file persistence and canonical validation.
    """

    def save_blob(self, file_id: str, encrypted_bytes: bytes, envelope: EncryptedEnvelope) -> Path:
        """
        Persists encrypted binary data and its metadata envelope inside the vault.

        :param file_id: Unique UUID string.
        :param encrypted_bytes: AEAD encrypted ciphertext bytes.
        :param envelope: Associated EncryptedEnvelope metadata.
        :return: Canonical Path of the stored binary file.
        """
        ...

    def read_blob(self, file_id: str) -> tuple[bytes, EncryptedEnvelope]:
        """
        Reads encrypted binary data and associated envelope by file ID.

        :param file_id: Unique UUID string.
        :return: Tuple of (encrypted_bytes, EncryptedEnvelope).
        """
        ...

    def resolve_safe_path(self, unsafe_filename: str) -> Path:
        """
        Sanitizes and canonicalizes paths to prevent Directory Traversal (../) attacks.

        :param unsafe_filename: Untrusted file identifier or filename from user request.
        :return: Resolved Path strictly confined within the vault directory boundary.
        :raises ValueError: If path jailbreaking or traversal is detected.
        """
        ...