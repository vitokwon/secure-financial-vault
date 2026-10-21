"""
tests/integration/test_api_flow.py
Comprehensive End-to-End integration test suite:
- Happy Path (Full Security Workflow)
- Attack Mitigation 1: Ciphertext Tampering / Bit-flipping Detection
- Attack Mitigation 2: Auth Failures & Forged JWT Rejection
"""

import io
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_full_security_workflow_integration():
    """
    Scenario 1: Full Happy Path Security Workflow
    1. Authenticate as staff_user -> Receive JWT.
    2. Upload document -> Encrypted with AES-256-GCM.
    3. Download document -> Verified against SHA-256 and decrypted.
    4. Access /audit/logs with staff token -> Rejected with 403 Forbidden.
    5. Authenticate as auditor_user -> Retrieve audit telemetry logs.
    """
    # 1. Staff Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "staff_user", "password": "AdminPass123!"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    staff_token = login_resp.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # 2. Upload Document
    test_content = b"INTEGRATION_TEST_SECRET_FINANCIAL_PAYLOAD_2026"
    test_filename = "integration_test_doc.txt"
    files = {"file": (test_filename, io.BytesIO(test_content), "text/plain")}

    upload_resp = client.post("/api/v1/vault/upload", files=files, headers=staff_headers)
    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    upload_data = upload_resp.json()
    file_id = upload_data["file_id"]

    # 3. Download Document
    download_resp = client.get(f"/api/v1/vault/download/{file_id}", headers=staff_headers)
    assert download_resp.status_code == 200
    assert download_resp.content == test_content

    # 4. RBAC 403 Forbidden Check
    forbidden_resp = client.get("/api/v1/audit/logs", headers=staff_headers)
    assert forbidden_resp.status_code == 403

    # 5. Auditor Login & Logs Inspection
    auditor_login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "auditor_user", "password": "AdminPass123!"},
    )
    assert auditor_login_resp.status_code == 200
    auditor_token = auditor_login_resp.json()["access_token"]
    auditor_headers = {"Authorization": f"Bearer {auditor_token}"}

    audit_resp = client.get("/api/v1/audit/logs", headers=auditor_headers)
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert len(events) > 0


def test_tampered_document_download_blocked():
    """
    Scenario 2: Tamper Resistance (Bit-flipping Attack Mitigation)
    1. Upload a document as staff.
    2. Directly modify 1 byte of the encrypted .bin file in vault storage.
    3. Attempt download -> Assert 400 Bad Request with integrity error.
    """
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "staff_user", "password": "AdminPass123!"},
    )
    staff_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Upload clean document
    upload_resp = client.post(
        "/api/v1/vault/upload",
        files={
            "file": ("tamper_test.txt", io.BytesIO(b"CLEAN_DATA_BEFORE_TAMPERING"), "text/plain")
        },
        headers=staff_headers,
    )
    assert upload_resp.status_code == 201
    file_id = upload_resp.json()["file_id"]

    # Simulate physical bit-flipping attack on disk
    bin_path = Path(settings.storage_dir) / f"{file_id}.bin"
    assert bin_path.exists(), "Binary file must exist on disk"
    corrupted_bytes = bytearray(bin_path.read_bytes())
    corrupted_bytes[-1] ^= 0x01  # Flip 1 bit of AEAD authentication tag
    bin_path.write_bytes(bytes(corrupted_bytes))

    # Attempt download
    tampered_download_resp = client.get(f"/api/v1/vault/download/{file_id}", headers=staff_headers)
    assert tampered_download_resp.status_code == 400
    assert "tampered" in tampered_download_resp.json()["detail"].lower()


def test_auth_security_negative_cases():
    """
    Scenario 3: Authentication & Token Security Guards
    1. Reject invalid credentials with 401.
    2. Reject forged / unsigned JWT bearer tokens with 401.
    """
    # 1. Invalid Password
    bad_login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "staff_user", "password": "WrongPassword999!"},
    )
    assert bad_login_resp.status_code == 401

    # 2. Forged Bearer Token
    forged_headers = {"Authorization": "Bearer forged.invalid.token.payload"}
    unauthorized_vault_resp = client.get(
        "/api/v1/vault/download/some-dummy-id", headers=forged_headers
    )
    assert unauthorized_vault_resp.status_code == 401
