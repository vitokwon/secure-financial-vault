# Test Matrix — Role-Based Secure Financial Document Vault

| Field | Value |
|---|---|
| Document owner | Dhruvi Sorathiya (Security QA & Demonstration Lead) |
| Reviewer | David Williams (Threat Modeling & Technical Documentation Lead) |
| Current version | **v0.1 — Draft** |
| Last updated | 2026-10-18 |
| Linked documents | [`THREAT_MODEL.md`](THREAT_MODEL.md) v0.3 · [`ARCHITECTURE.md`](ARCHITECTURE.md) v0.1 · [`DOCUMENTATION_GUIDE.md`](DOCUMENTATION_GUIDE.md) |
| Code baseline | `main` at the documentation update commit |

---

## 1. Purpose

This matrix records the security tests for the vault and maps them to the threats in [`THREAT_MODEL.md`](THREAT_MODEL.md) §6. A threat or mitigation moves from `Implemented` to `Verified` only after its associated test has passed and the run evidence has been recorded here.

The current repository has executable vault-storage tests. Authentication, RBAC, audit, API, and several configuration tests remain blocked or planned until the relevant modules are implemented.

## 2. Conventions

- **Test IDs** follow the threat model: `TC-01` through `TC-15`. `TC-16` is proposed only and is not part of the current formal register.
- **Threat IDs** use the STRIDE identifiers from the threat register (`S1`, `T1`, `I2`, and so on).
- **Type:** `Unit` · `Integration` · `Security` · `E2E` · `Inspection`.
- **Status:** `Not run` · `Pass` · `Fail` · `Blocked` · `Planned`.
- **Blocked** means the required implementation or test location is not yet available.
- **Planned** means the test design is identified but implementation work has not started.
- **Test location** must contain a repository path and test function once the test exists.
- After each run, update **Result**, **Status**, **Last run**, **Run by**, and **Commit** in the run log. Notify the threat-model owner when a threat status can change.

## 3. Test Cases

| Test ID | Threat | Phase | What is tested | Type | Test location | Expected result | Result | Status | Last run |
|---|---|---:|---|---|---|---|---|---|---|
| TC-01 | S1 | 3 | Login protection: bcrypt hashes are stored instead of plaintext; repeated failures are rate-limited or locked; unknown-user and wrong-password responses are generic | Security | TBC — auth module | Passwords are not stored in plaintext; repeated attempts are refused; error responses do not disclose account existence | | Blocked | |
| TC-02 | S2 | 3 | JWT tampering: modified signature, `alg: none`, wrong signing secret, and expired token | Security | TBC — auth tests | All invalid tokens are rejected with 401 | | Blocked | |
| TC-03 | T1 | 2 | One-byte modification of encrypted ciphertext in `{file_id}.bin` | Security | TBC — crypto tests | AES-GCM authentication fails; no plaintext is returned | | Blocked | |
| TC-04 | T2 | 2 | Stored file and integrity hash are replaced together | Security | TBC — integrity/HMAC tests | Replacement is detected by authenticated integrity metadata; rollback remains separately documented as residual risk | | Planned | |
| TC-05 | T3 | 4 | Audit-log entry is edited or deleted | Security | TBC — audit tests | Hash-chain or HMAC verification reports the broken or missing entry | | Blocked | |
| TC-06 | R1 | 4 | Upload, download, and delete each create an audit event | Integration | TBC — API/audit tests | Each event includes user ID, role, timestamp, IP, and action | | Blocked | |
| TC-07 | I1, I6 | 1 | `.env` is ignored and untracked; startup rejects missing, short, or malformed secrets | Inspection + Unit | `git ls-files .env`; TBC config test | `.env` is not tracked; invalid configuration prevents startup with a clear safe error | | Not run | |
| TC-08 | I2 | 2 | Traversal payloads, absolute paths, null bytes, and Windows-style paths | Unit | `tests/unit/test_vault.py::test_directory_traversal_mitigation`; `tests/unit/test_vault.py::test_null_byte_injection_blocked` | Input is rejected or reduced to a safe filename; no path escapes `vault_storage/` | | Not run | |
| TC-09 | I4 | 4 | Error responses for invalid input and server errors | Security | TBC — API tests | Responses do not expose stack traces, SQL, filesystem paths, or secrets; `/docs` handling matches the deployment decision | | Blocked | |
| TC-10 | D1 | 4 | Oversized and repeated uploads | Security | TBC — API/rate-limit tests | Oversized files return 413 or equivalent; repeated requests are throttled | | Blocked | |
| TC-11 | D2 | 4 | Executable content renamed with an allowed document extension | Security | TBC — validation tests | Magic-byte mismatch is rejected; the file is not stored or executed | | Blocked | |
| TC-12 | E1 | 3 | Staff attempts Admin/Auditor operations and requests another role's file by ID | Security | TBC — RBAC/API tests | Every unauthorized request returns 403 and the attempt is logged | | Blocked | |
| TC-13 | E2 | 3 | Role claim is changed from Staff to Admin inside a JWT | Security | TBC — auth/RBAC tests | Signature validation fails or the database role overrides the edited claim; access is denied | | Blocked | |
| TC-14 | T4 | 3 | SQL injection payloads in login, search, and metadata fields | Security | TBC — database/API tests | No authentication bypass occurs and database contents remain unchanged | | Blocked | |
| TC-15 | I5 | 2 | Ciphertext and metadata are stored separately and can be read back through the storage adapter | Unit | `tests/unit/test_vault.py::test_envelope_and_blob_storage_roundtrip`; `tests/unit/test_vault.py::test_nonexistent_blob_read_raises` | `.bin` and `.meta.json` are separate; round-trip returns the original stored bytes and envelope; missing files raise safely | | Not run | |
| TC-16 *(proposed)* | E1, T1, I5 | 4 | End-to-end login, upload, encryption, authorized download, and denied cross-role download | E2E | TBC — integration/API tests | Permitted role receives the original document; unauthorized role receives 403 | | Planned | |

> `TC-16` is proposed from the Phase 4 work breakdown. Before it is counted as formal coverage, add it to the threat register and update the threat-model summary consistently.

## 4. Current Evidence and Execution Guidance

The following tests have source locations in the current repository and can be run now:

```bash
pytest tests/unit/test_vault.py -v
```

| Test ID | Current evidence | Action |
|---|---|---|
| TC-08 | `test_directory_traversal_mitigation` and `test_null_byte_injection_blocked` | Run and record the result. |
| TC-15 | `test_envelope_and_blob_storage_roundtrip` and `test_nonexistent_blob_read_raises` | Run and record the result. |

The current repository also contains crypto implementations in `app/domains/crypto/aes_engine.py` and `app/domains/crypto/hasher.py`. Add concrete test locations for TC-03 and the remaining crypto tests when the corresponding test file is confirmed.

Do not mark TC-03, TC-04, or any other test as `Pass` based only on source inspection. A test run and evidence are required.

## 5. Threat Coverage

Every threat in [`THREAT_MODEL.md`](THREAT_MODEL.md) §6 is listed below. A threat without an executable test has a reason recorded in the final column.

| Threat | Short description | Risk | Test(s) | Coverage | Reason / next action |
|---|---|---|---|---|---|
| S1 | Password guessing / credential stuffing | High (9) | TC-01 | Planned | Auth service and rate limiting are TBC. |
| S2 | Forged JWT | High (6) | TC-02 | Planned | Auth implementation is TBC. |
| T1 | Ciphertext altered on disk | High (6) | TC-03, TC-16 | Planned | AES-GCM is implemented; tamper test and E2E flow remain to be added or located. |
| T2 | File and hash replaced / rollback | Medium (3) | TC-04 | Planned | HMAC protection is not implemented; rollback remains residual risk. |
| T3 | Audit log edited or deleted | High (6) | TC-05 | Blocked | Audit logger and verification routine are TBC. |
| T4 | SQL injection | High (6) | TC-14 | Blocked | Database/API implementation is TBC. |
| R1 | User denies an action | Medium (4) | TC-06 | Blocked | Audit logger is TBC. |
| I1 | Keys exposed through the repository | High (6) | TC-07 | Not run | Run repository and configuration inspection. |
| I2 | Path traversal | High (6) | TC-08 | Test exists — run | Vault path defenses and test locations exist. |
| I3 | Interception in transit | High (6) | — | Not tested | HTTPS is a deployment requirement under the threat-model assumptions. |
| I4 | Errors or API docs reveal internals | Low (2) | TC-09 | Blocked | API error behavior and production docs configuration are TBC; `/docs` is accepted for the demo. |
| I5 | Stolen disk or backup | High (6) | TC-15, TC-16 | Test exists — run | Separate blob/envelope storage exists; run the storage tests. |
| I6 | Master-key compromise | Medium (3) residual | TC-07 | Partial | Environment-only secret handling can be inspected; no HSM or per-file wrapping exists. |
| D1 | Oversized or repeated uploads | Medium (4) | TC-10 | Blocked | Upload limits and rate limiting are TBC. |
| D2 | Disguised file type | Medium (4) | TC-11 | Blocked | Magic-byte validation is TBC. |
| E1 | IDOR / cross-role access | High (9) | TC-12, TC-16 | Blocked | RBAC and API routes are TBC. |
| E2 | Edited role claim | High (6) | TC-13 | Blocked | JWT and database-backed role loading are TBC. |
| E3 | Insider administrator misuse | Medium (3) residual | — | Not tested | Residual risk mitigated by least privilege and planned audit review; no isolated automated test is currently defined. |

## 6. Run Log

| Date | Run by | Command | Total | Pass | Fail | Blocked | Commit | Notes |
|---|---|---|---:|---:|---:|---:|---|---|
| YYYY-MM-DD | | `pytest tests/unit/test_vault.py -v` | | | | | | |

## 7. Evidence Requirements

For every test marked `Pass`:

1. Record the exact command and test location.
2. Record the run date, executor, commit SHA, and result summary.
3. Preserve relevant failure output if the test later regresses.
4. Notify the threat-model owner before changing the corresponding threat status to `Verified`.
5. Never include secrets, tokens, personal information, or real financial documents in test evidence or screenshots.

## 8. Change Log

| Version | Date | Author | Changes |
|---|---|---|---|
| v0.1 | 2026-10-18 | D. Williams (draft for D. Sorathiya) | Corrected initial matrix to match the current threat register; separated executable vault tests from blocked/planned tests; documented exact current test locations, proposed TC-16 handling, and evidence requirements. |
