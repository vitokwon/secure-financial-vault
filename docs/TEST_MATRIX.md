# Security Test Matrix — Role-Based Secure Financial Document Vault

| Field | Value |
|---|---|
| Document owner | Dhruvi Sorathiya (Security QA & Demonstration Lead) |
| Reviewer | David Williams |
| Current version | **v0.1 — Draft** |
| Last updated | 2026-10-18 |
| Related docs | [`THREAT_MODEL.md`](THREAT_MODEL.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`DOCUMENTATION_GUIDE.md`](DOCUMENTATION_GUIDE.md) |

---

## 1. Status Legend

| Status | Meaning |
|---|---|
| Not run | Implementation and test location exist, but this run has not been executed yet |
| Pass | Test executed successfully and evidence is recorded |
| Fail | Test executed but the expected security behavior did not hold |
| Blocked | Required implementation or runnable test location does not yet exist |
| Planned | Test design exists but implementation work has not started |
| Proposed | Candidate test is not yet in the formal threat register |

## 2. Threat-to-Test Coverage Matrix

| Test ID | Threat ID(s) | Security objective | Current test location / evidence | Type | Status |
|---|---|---|---|---|---|
| TC-01 | S1 | Login brute-force protection and lockout behavior | Auth module/lockout tests not present | Unit/Integration | Blocked |
| TC-02 | S2, E2 | JWT spoofing resistance (`alg` confusion, weak secret handling) | JWT validation tests not present | Unit | Blocked |
| TC-03 | T1 | Tampered ciphertext must fail decryption via AEAD tag validation | `tests/unit/test_crypto.py::test_tamper_detection` | Unit | Not run |
| TC-04 | T2 | Hash tamper/rollback resistance with keyed integrity protection | HMAC-protected hash control not implemented in `app/domains/crypto/hasher.py` | Unit | Blocked |
| TC-05 | T3 | Tamper-evident audit log chain validation | Audit logger tests not present | Unit/Integration | Blocked |
| TC-06 | R1 | Action accountability in audit events | Audit logger tests not present | Integration | Blocked |
| TC-07 | I1, I6 | Key strength/format validation at startup | No key-strength validation tests currently present | Unit | Blocked |
| TC-08 | I2 | Path traversal and null-byte payloads are blocked/confined | `tests/unit/test_vault.py::test_directory_traversal_mitigation`, `::test_null_byte_injection_blocked` | Unit | Pass |
| TC-09 | I4 | Internal details are not exposed in production errors/docs | Production-hardening tests not present | Integration | Planned |
| TC-10 | D1 | Upload size/rate controls prevent resource exhaustion | Rate-limit/size-guard tests not present | Integration | Blocked |
| TC-11 | D2 | Magic-byte validation blocks disguised executable uploads | Magic-byte validation tests not present | Unit/Integration | Blocked |
| TC-12 | E1 | RBAC denies cross-role document access (IDOR) | RBAC route tests not present | Integration | Blocked |
| TC-13 | E2 | Role claim tampering is denied at authorization boundary | RBAC/JWT integration tests not present | Integration | Blocked |
| TC-14 | T4 | SQL injection payloads are neutralized | DB/auth query hardening tests not present | Integration | Blocked |
| TC-15 | I5 | Ciphertext and metadata envelope storage isolation works and missing IDs fail safely | `tests/unit/test_vault.py::test_envelope_and_blob_storage_roundtrip`, `::test_nonexistent_blob_read_raises` | Unit | Pass |
| TC-16 (proposed) | (proposed) | Additional security control test candidate (not yet accepted into threat register) | Not in `docs/THREAT_MODEL.md` threat register | TBD | Proposed |

## 3. Currently Supported Executable Coverage

The repository currently provides implemented, runnable vault coverage for:

- **TC-08** (I2 path traversal/null-byte defenses)
- **TC-15** (I5 ciphertext + metadata envelope storage isolation)

These IDs remain linked to `tests/unit/test_vault.py` and should only be marked `Pass` when the run log includes execution evidence.

## 4. Test Run Log

| Date | Scope executed | Result summary | Evidence |
|---|---|---|---|
| 2026-10-18 | `pytest tests/unit/test_vault.py` | 13 passed | Validates TC-08 and TC-15 test evidence in `tests/unit/test_vault.py` |

## 5. Consistency Notes

- TC-16 remains **proposed** and is excluded from formal threat coverage until it is added to `docs/THREAT_MODEL.md` and implemented.
- TC-04 remains **blocked** until keyed (HMAC-based) integrity protection is implemented.
- Do not reclassify planned or blocked tests to pass/fail without executable evidence.

## 6. Change Log

| Version | Date | Author | Changes |
|---|---|---|---|
| v0.1 | 2026-10-18 | D. Sorathiya | Added repository-grounded threat-to-test matrix, separated executable vs blocked/planned coverage, preserved TC-16 as proposed, and recorded current vault unit test evidence. |
