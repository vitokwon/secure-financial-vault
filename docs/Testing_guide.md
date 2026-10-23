# End-to-End Security Verification & Testing Guide

## 1. Overview & Architectural Scope
This document outlines the step-by-step verification pipeline for the **Role-Based Secure Financial Document Vault**. It covers interactive validation via Swagger UI as well as automated regression testing through `pytest`.

### Verified Security Controls (Current Implementation)
1. **Authentication & Token Lifecycle**: Salted Bcrypt password hashing and HS256 JWT issuance with expiration.
2. **Confidentiality (Encryption at Rest)**: AES-256-GCM authenticated encryption for vault payloads.
3. **Integrity Verification**: SHA-256 fingerprint computation on the **server side** during upload, then verification on download.
4. **Audit Traceability (Prototype Level)**: Append-only JSONL audit logging with sensitive-field redaction.
5. **Role-Based Access Control (RBAC)**: Role separation across `admin`, `auditor`, and `staff`.
6. **Path Traversal Defense**: Isolated storage access through vault storage abstraction and file-id based retrieval.

### Prototype / Demonstration Limitations
- Authentication currently uses **in-memory seeded users** (`admin_user`, `auditor_user`, `staff_user`) rather than a persistent identity store.
- The audit logger writes append-only JSON lines and redacts sensitive keys, but does **not** implement cryptographic hash chaining, HMAC signing, or external integrity attestation.
- `/api/v1/vault/tamper-simulate/{file_id}` is a **demo-only endpoint** for forced ciphertext corruption testing.

---

## 2. Interactive Verification Walkthrough (Swagger UI)

Base URL: `http://127.0.0.1:8000/api/v1/docs`

---

### Step 1. Staff Authentication & Token Issuance
- **Endpoint**: `POST /api/v1/auth/login`
- **Objective**: Authenticate as staff and receive a signed JWT access token.
- **Request Payload**:
  ```json
  {
    "username": "staff_user",
    "password": "AdminPass123!"
  }
  ```
- **Execution**: Click **Try it out** -> Paste payload -> **Execute**.
- **Expected Outcome**:
  - **HTTP Status**: `200 OK`
  - **Response Body**:
    ```json
    {
      "access_token": "<JWT_STRING>",
      "token_type": "Bearer",
      "role": "staff",
      "username": "staff_user"
    }
    ```
- **Authorization Setup**:
  1. Copy `access_token`.
  2. Click **Authorize 🔒** in Swagger UI.
  3. Enter `****** and authorize.

---

### Step 2. Authenticated Document Upload & Encryption
- **Endpoint**: `POST /api/v1/vault/upload`
- **Objective**: Upload plaintext; the server computes SHA-256, encrypts content, stores ciphertext/metadata, and records an audit event.
- **Execution**:
  1. Expand `POST /api/v1/vault/upload` -> Click **Try it out**.
  2. Under `file`, select a local document (e.g., `sample_upload.txt`).
  3. Click **Execute**.
- **Expected Outcome**:
  - **HTTP Status**: `201 Created`
  - **Response Payload**:
    ```json
    {
      "file_id": "<UUID_STRING>",
      "filename": "sample_upload.txt",
      "sha256_fingerprint": "<64_CHAR_HEX_DIGEST>",
      "uploaded_by": "staff_user",
      "created_at": "<ISO8601_TIMESTAMP>"
    }
    ```
- **Disk Persistence Verification**:
  Check `vault_storage/` (or the configured `storage_dir`) for:
  - `{file_id}.bin` (ciphertext)
  - `{file_id}.meta.json` (metadata envelope)
  - `audit.log` (appended JSONL record, e.g., `VAULT_UPLOAD`)

---

### Step 3. Document Retrieval & Roundtrip Verification
- **Endpoint**: `GET /api/v1/vault/download/{file_id}`
- **Objective**: Decrypt ciphertext, verify SHA-256 against metadata, then stream original plaintext.
- **Execution**:
  1. Paste generated `file_id`.
  2. Click **Execute**.
- **Expected Outcome**:
  - **HTTP Status**: `200 OK`
  - **Response Header**: `content-disposition: attachment; filename="sample_upload.txt"`
  - **File Validation**: Downloaded bytes should match uploaded bytes.

---

### Step 4. Tamper Demonstration (Bit-Flipping Attack)
- **Objective**: Show tamper detection on ciphertext modification.
- **Execution (Manual file edit)**:
  1. Open `{file_id}.bin` in `vault_storage/`.
  2. Modify one byte and save.
  3. Re-run `GET /api/v1/vault/download/{file_id}`.
- **Alternative Demo Endpoint**:
  - `POST /api/v1/vault/tamper-simulate/{file_id}`
- **Expected Outcome**:
  - **HTTP Status**: `400 Bad Request`
  - **Response Body**:
    ```json
    {
      "detail": "Decryption failed. File may have been tampered with."
    }
    ```
  - **Audit Trail Check**: `audit.log` should contain an appended `INTEGRITY_FAILURE` record.

---

### Step 5. RBAC Guard Verification (Privilege Enforcement)
- **Endpoint**: `GET /api/v1/audit/logs`
- **Objective**: Verify that `staff` cannot access auditor/admin audit-log endpoint.
- **Execution**:
  1. Keep `staff_user` token active.
  2. Execute `GET /api/v1/audit/logs` (default `limit=50`).
- **Expected Outcome**:
  - **HTTP Status**: `403 Forbidden`
  - **Response Body**:
    ```json
    {
      "detail": "Access denied: Role 'staff' lacks required permissions."
    }
    ```

---

### Step 6. Auditor Access & Audit Log Retrieval
- **Objective**: Authenticate as `auditor_user` and inspect audit records.
- **Execution**:
  1. Authenticate via `POST /api/v1/auth/login`:
     ```json
     {
       "username": "auditor_user",
       "password": "AdminPass123!"
     }
     ```
  2. Authorize with the auditor bearer token.
  3. Execute `GET /api/v1/audit/logs`.
- **Expected Outcome**:
  - **HTTP Status**: `200 OK`
  - **Response Body**: List of records (returned newest-first by current implementation), including events such as:
    - `AUTH_LOGIN_SUCCESS`
    - `VAULT_UPLOAD`
    - `VAULT_DOWNLOAD`
    - `INTEGRITY_FAILURE`

---

### Step 7. Path Traversal / Invalid Identifier Handling
- **Endpoint**: `GET /api/v1/vault/download/{file_id}`
- **Objective**: Confirm non-existent or malicious identifiers do not expose arbitrary filesystem paths.
- **Execution**:
  1. Try invalid IDs (e.g., `not-a-real-id`, traversal-like inputs).
  2. Execute request.
- **Expected Outcome**:
  - **HTTP Status**: `404 Not Found` when storage lookup fails.
  - No file outside configured vault storage should be returned.

---

## 3. Automated Regression Testing (`pytest`)

Use automated tests to validate behavior without manual UI steps.

### 1. Run Unit Test Suite
```powershell
python -m pytest tests/unit/ -v
```

### 2. Run End-to-End Integration Suite
```powershell
python -m pytest tests/integration/test_api_flow.py -v
```

Current integration coverage includes:
1. `test_full_security_workflow_integration`
2. `test_tampered_document_download_blocked`
3. `test_auth_security_negative_cases`

> Note: This guide documents expected behavior based on current route and test implementations; execute the commands locally/CI to produce run evidence for submission records.
