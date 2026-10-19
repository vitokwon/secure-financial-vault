"""
app/domains/vault/disk_storage.py
Production-grade isolated disk storage implementation featuring strict canonical path validation.
"""

import json
from pathlib import Path

from app.domains.vault.models import EncryptedEnvelope
from app.domains.vault.protocols import VaultStorageProtocol


class DiskVaultStorage(VaultStorageProtocol):
    """
    Secure disk persistence adapter ensuring all file operations remain strictly
    confined within a designated base storage directory.
    """

    def __init__(self, base_directory: Path | str = "vault_storage"):
        """
        Initializes disk storage engine and verifies directory sandboxing.

        :param base_directory: Target physical directory for vault files.
        """
        # 1. Fix the relative path to a 'full absolute path' based on the OS.
        self.base_path = Path(base_directory).resolve()
        # 2. Automatically create the folder if it does not exist
        self.base_path.mkdir(parents=True, exist_ok=True)

    def resolve_safe_path(self, unsafe_filename: str) -> Path:
        """
        Canonicalizes an untrusted filename and prevents Directory Traversal (../).
        Enforces sandboxed confinement within self.base_path.
        """
        if not unsafe_filename or not isinstance(unsafe_filename, str):
            raise ValueError("[SECURITY ALERT] Filename must be a non-empty string.")

        # Defense 1: Reject Null-Byte injections (CVE-style poison null byte)
        if "\x00" in unsafe_filename:
            raise ValueError("[SECURITY ALERT] Null bytes are forbidden in paths.")

        # Defense 2: Strip directory components using Path.name
        sanitized_name = Path(unsafe_filename).name

        if not sanitized_name or sanitized_name in (".", ".."):
            raise ValueError("[SECURITY ALERT] Invalid path traversal payload detected.")

        # Defense 3: Canonical resolution against base vault boundary
        target_path = (self.base_path / sanitized_name).resolve()

        # Defense 4: Sandbox confinement verification
        if not target_path.is_relative_to(self.base_path):
            raise PermissionError(
                "[SECURITY ALERT] Path traversal attempt detected outside vault sandbox."
            )

        return target_path

    def save_blob(self, file_id: str, encrypted_bytes: bytes, envelope: EncryptedEnvelope) -> Path:
        """
        Safely writes encrypted binary and metadata envelope to isolated disk storage.
        """
        # Validate that file_id does not contain path traversal vectors
        bin_path = self.resolve_safe_path(f"{file_id}.bin")
        meta_path = self.resolve_safe_path(f"{file_id}.meta.json")

        # Atomic/isolated writes
        with open(bin_path, "wb") as f_bin:
            f_bin.write(encrypted_bytes)

        # Save Shipping Label (JSON Text)
        with open(meta_path, "w", encoding="utf-8") as f_meta:
            f_meta.write(envelope.model_dump_json(indent=2))

        return bin_path

    def read_blob(self, file_id: str) -> tuple[bytes, EncryptedEnvelope]:
        """
        Reads stored ciphertext and recovers metadata envelope from disk.
        """
        bin_path = self.resolve_safe_path(f"{file_id}.bin")
        meta_path = self.resolve_safe_path(f"{file_id}.meta.json")

        # 1. Check if the file actually exists (error if it doesn't)
        if not bin_path.exists() or not meta_path.exists():
            raise FileNotFoundError(f"[STORAGE ERROR] Target vault document {file_id} not found.")

        # 2. Reading Ciphertext Binary Bytes
        with open(bin_path, "rb") as f_bin:
            encrypted_bytes = f_bin.read()

        # 3. Read the metadata JSON and restore it back into an EncryptedEnvelope object!
        with open(meta_path, encoding="utf-8") as f_meta:
            envelope_data = json.load(f_meta)
            envelope = EncryptedEnvelope.model_validate(envelope_data)

        # 4. Returns the ciphertext bytes and the waybill object as a tuple (pair).
        return encrypted_bytes, envelope
