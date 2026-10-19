"""
tests/unit/test_vault.py
Security QA test suite for Path Traversal defense and isolated vault disk storage.
"""

import pytest

from app.domains.vault.disk_storage import DiskVaultStorage
from app.domains.vault.models import EncryptedEnvelope
from app.domains.vault.protocols import VaultStorageProtocol


@pytest.fixture
def temp_vault(tmp_path):
    """Provides an isolated temporary vault storage directory."""
    vault_dir = tmp_path / "sandbox_vault"
    return DiskVaultStorage(base_directory=vault_dir)


@pytest.fixture
def sample_envelope():
    """Provides a sample EncryptedEnvelope instance."""
    return EncryptedEnvelope(
        file_id="550e8400-e29b-41d4-a716-446655440000",
        original_filename="confidential_q3_report.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        size_bytes=1024,
        content_type="application/pdf",
        owner_id="auditor_01",
    )


def test_vault_protocol_conformance(temp_vault):
    """Verifies that DiskVaultStorage fulfills VaultStorageProtocol contract."""
    assert isinstance(temp_vault, VaultStorageProtocol)


def test_safe_path_resolution(temp_vault):
    """Verifies canonical path resolution inside sandbox."""
    resolved = temp_vault.resolve_safe_path("invoice_2026.enc")
    assert resolved.parent == temp_vault.base_path
    assert resolved.name == "invoice_2026.enc"


@pytest.mark.parametrize(
    "malicious_path",
    [
        "../../etc/passwd",
        "..\\..\\Windows\\System32\\cmd.exe",
        "....//....//sensitive.key",
        "/etc/shadow",
        "C:\\Windows\\system.ini",
        "vault_storage/../../secret.txt",
        ".",
        "..",
    ],
)
def test_directory_traversal_mitigation(temp_vault, malicious_path):
    """
    STRIDE I2 Mitigation Test:
    Ensures that directory traversal payloads are either strictly sanitized into safe local names
    or rejected with ValueError/PermissionError, never escaping the sandbox boundary.
    """
    try:
        safe_path = temp_vault.resolve_safe_path(malicious_path)
        # If it didn't throw an error, it must strictly be resolved inside base_path
        assert safe_path.is_relative_to(temp_vault.base_path)
        assert safe_path.parent == temp_vault.base_path
    except (ValueError, PermissionError):
        # Explicit exception rejection is valid security behavior
        pass


def test_null_byte_injection_blocked(temp_vault):
    """Ensures poison null-byte injections are explicitly rejected."""
    with pytest.raises(ValueError, match="Null bytes are forbidden"):
        temp_vault.resolve_safe_path("safe_file.txt\x00.exe")


def test_envelope_and_blob_storage_roundtrip(temp_vault, sample_envelope):
    """Verifies isolated write and read cycle for ciphertext and metadata."""
    payload_bytes = b"\x01\x02\x03\x04\x05_ENCRYPTED_BLOB_MOCK"
    file_id = sample_envelope.file_id

    # 1. Save
    saved_path = temp_vault.save_blob(file_id, payload_bytes, sample_envelope)
    assert saved_path.exists()
    assert saved_path.name == f"{file_id}.bin"

    # 2. Read back
    read_bytes, read_envelope = temp_vault.read_blob(file_id)
    assert read_bytes == payload_bytes
    assert read_envelope.file_id == sample_envelope.file_id
    assert read_envelope.sha256_hash == sample_envelope.sha256_hash
    assert read_envelope.original_filename == sample_envelope.original_filename


def test_nonexistent_blob_read_raises(temp_vault):
    """Verifies clean FileNotFoundError when requesting non-existent file ID."""
    with pytest.raises(FileNotFoundError):
        temp_vault.read_blob("non-existent-uuid-9999")
