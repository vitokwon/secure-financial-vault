# End-to-End Security Verification & Testing Guide

## 1. Overview & Architectural Scope
This document outlines the step-by-step verification pipeline for the **Role-Based Secure Financial Document Vault**. It covers interactive validation via Swagger UI as well as automated regression testing through `pytest`.

### Verified Security Controls:
1. **Authentication & Token Lifecycle**: Salted Bcrypt password hashing and cryptographic HS256 JWT issuance with session expiration.
2. **Confidentiality (Encryption at Rest)**: AES-256-GCM authenticated cipher with CSPRNG 12-byte nonces.
3. **Integrity & Non-Repudiation**: Pre-encryption SHA-256 integrity fingerprinting and append-only audit telemetry (`audit.log`).
4. **Tamper Resistance**: AEAD 16-byte authentication tag verification and bit-flipping detection.
5. **Role-Based Access Control (RBAC)**: Strict role separation across `admin`, `auditor`, and `staff`.
6. **Path Traversal Defense**: Strict directory containment and input sanitization (`resolve_safe_path`).

---

## 2. Interactive Verification Walkthrough (Swagger UI)ruff format .

Base URL: `http://127.0.0.1:8000/api/v1/docs`

---

### Step 1. Staff Authentication & Bearer Token Issuance
* **Endpoint**: `POST /api/v1/auth/login`
* **Objective**: Authenticate as standard operational staff and receive a signed JWT access token.
* **Request Payload**:
  ```json
  {
    "username": "staff_user",
    "password": "AdminPass123!"
  }
  ```
* **Execution**: Click **Try it out** -> Paste payload -> **Execute**.
* **Expected Outcome**:
  * **HTTP Status**: `200 OK`
  * **Response Body**:
    ```json
    {
      "access_token": "<JWT_STRING>",
      "token_type": "Bearer",
      "role": "staff",
      "username": "staff_user"
    }
    ```
* **Authorization Setup**:
  1. Copy the `access_token` string (excluding quotation marks).
  2. Click the **Authorize 🔒** button at the top right of the Swagger UI.
  3. Paste the token into the **Value** field and click **Authorize**, then **Close**.

---

### Step 2. Authenticated Document Upload & AES-256-GCM Encryption
* **Endpoint**: `POST /api/v1/vault/upload`
* **Objective**: Upload a plaintext document to trigger client-side hashing, symmetric encryption, isolated disk persistence, and audit logging.
* **Execution**:
  1. Expand `POST /api/v1/vault/upload` -> Click **Try it out**.
  2. Under the `file` parameter, select a local document (e.g., `sample_upload.txt`).
  3. Click **Execute**.
* **Expected Outcome**:
  * **HTTP Status**: `201 Created`
  * **Response Payload**:
    ```json
    {
      "file_id": "<UUID_STRING>",
      "filename": "sample_upload.txt",
      "sha256_fingerprint": "<64_CHAR_HEX_DIGEST>",
      "uploaded_by": "staff_user",
      "created_at": "<ISO8601_TIMESTAMP>"
    }
    ```
* **Disk Persistence Verification**:
  Check the `vault_storage/` directory in the project root:
  * `{file_id}.bin`: Ciphertext binary stream encrypted via AES-256-GCM.
  * `{file_id}.meta.json`: Envelope metadata containing original filename, owner, and SHA-256 digest.
  * `audit.log`: Contains an append-only entry with event type `VAULT_UPLOAD`.

---

### Step 3. Plaintext Document Retrieval & Roundtrip Verification
* **Endpoint**: `GET /api/v1/vault/download/{file_id}`
* **Objective**: Decrypt stored binary payload, verify SHA-256 checksum against recorded metadata, and stream original plaintext back to the client.
* **Execution**:
  1. Paste the generated `file_id` into the parameter field.
  2. Click **Execute**.
* **Expected Outcome**:
  * **HTTP Status**: `200 OK`
  * **Response Header**: `content-disposition: attachment; filename="sample_upload.txt"`
  * **File Validation**: Click **Download file** and verify that the file contents match the original uploaded bytes exactly.

---

### Step 4. Tamper Resistance Demonstration (Bit-Flipping Attack)
* **Objective**: Demonstrate that any modification to stored ciphertext causes immediate decryption rejection via the AEAD authentication tag.
* **Execution**:
  1. Open the generated `{file_id}.bin` file in an editor.
  2. Modify a single byte or character in the ciphertext and save (`Ctrl + S`).
  3. Re-run `GET /api/v1/vault/download/{file_id}` in Swagger UI with the same `file_id`.
* **Expected Outcome**:
  * **HTTP Status**: `400 Bad Request`
  * **Response Body**:
    ```json
    {
      "detail": "Decryption failed. File may have been tampered with."
    }
    ```
  * **Audit Log Trail**: Check `vault_storage/audit.log` to confirm an immutable entry with `event_type: "INTEGRITY_FAILURE"` was appended.

---

### Step 5. 3-Tier RBAC Guard Verification (Privilege Enforcement)
* **Endpoint**: `GET /api/v1/audit/logs`
* **Objective**: Verify that non-privileged roles (`staff`) cannot access auditor/admin compliance endpoints.
* **Execution**:
  1. Keep the `staff_user` bearer token active in Swagger UI.
  2. Expand `GET /api/v1/audit/logs` under **Security Telemetry & Compliance**.
  3. Click **Execute** (with `limit=50`).
* **Expected Outcome**:
  * **HTTP Status**: `403 Forbidden`
  * **Response Body**:
    ```json
    {
      "detail": "Access denied: Role 'staff' lacks required permissions."
    }
    ```

---

### Step 6. Auditor Access & Audit Log Retrieval
* **Objective**: Authenticate as `auditor_user` and inspect the tamper-resistant security audit trail.
* **Execution**:
  1. Authenticate via `POST /api/v1/auth/login` using:
     ```json
     {
       "username": "auditor_user",
       "password": "AdminPass123!"
     }
     ```
  2. Update Swagger UI authorization by clicking **Authorize 🔒**, logging out, and applying the new auditor token.
  3. Re-execute `GET /api/v1/audit/logs`.
* **Expected Outcome**:
  * **HTTP Status**: `200 OK`
  * **Response Body**: A chronological list of audit records detailing:
    * `AUTH_LOGIN_SUCCESS` (Logins for staff and auditor)
    * `VAULT_UPLOAD` (Document creation metadata)
    * `VAULT_DOWNLOAD` (Document retrieval access)
    * `INTEGRITY_FAILURE` (Recorded tamper detection attempt)

---

### Step 7. Path Traversal Attack Mitigation
* **Endpoint**: `GET /api/v1/vault/download/{file_id}`
* **Objective**: Attempt sandbox escape via directory traversal sequences (`../../etc/passwd`).
* **Execution**:
  1. Enter `../../etc/passwd` or `..` into the `file_id` path parameter.
  2. Click **Execute**.
* **Expected Outcome**:
  * **HTTP Status**: `404 Not Found` (Router rejection / Sandbox isolation)
  * System boundary enforcement guarantees no file outside `vault_storage/` is exposed.

---

## 3. Automated Regression Testing (`pytest`)

Automated test suites can be executed from the terminal without manual intervention.

### 1. Run Complete Unit Test Suite
```powershell
pytest tests/unit/ -v
```
* **Coverage**: Crypto cipher cycle, bit-flipping tamper detection, SHA-256 timing attack defense, Bcrypt hashing boundaries, and JWT lifecycle.

### 2. Run End-to-End Integration Suite
```powershell
pytest tests/integration/test_api_flow.py -v
```
* **Coverage**:
  1. `test_full_security_workflow_integration`: Full workflow from authentication to compliance inspection.
  2. `test_tampered_document_download_blocked`: Automated disk byte corruption and tamper rejection.
  3. `test_auth_security_negative_cases`: Rejection of invalid credentials and forged JWT signatures.

### 3. Pytest Configuration & Warning Suppression
To ensure clean output during CI/CD runs, warning suppression is maintained in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
filterwarnings = [
    "ignore::starlette.exceptions.StarletteDeprecationWarning",
]
```