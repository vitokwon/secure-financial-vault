# Test Matrix — Role-Based Secure Financial Document Vault

| Field | Value |
|---|---|
| Document owner | Dhruvi Sorathiya (Security QA & Demonstration Lead) |
| Reviewer | David Williams (Threat Modeling & Technical Documentation Lead) |
| Current version | **v0.4 — Draft** |
| Last updated | 2026-10-23 |
| Linked documents | [`THREAT_MODEL.md`](THREAT_MODEL.md) v1.0 · [`ARCHITECTURE.md`](ARCHITECTURE.md) v0.1 · [`DOCUMENTATION_GUIDE.md`](DOCUMENTATION_GUIDE.md) v0.9 |
| Code baseline | `main` at `96e6e76426ae3db4968bdaaa61389b7f47f4e0dc` |

---

## 1. Purpose

This matrix records the security tests for the vault and maps them to the threats in [`THREAT_MODEL.md`](THREAT_MODEL.md) §6. A threat or mitigation moves from `Implemented` to `Verified` only after its associated test has passed and the run evidence has been recorded here.

The current repository includes executable unit tests for auth/JWT, crypto, vault storage, config validation, and telemetry redaction, plus an integration suite in `tests/integration/test_api_flow.py`. This matrix records only status backed by documented run evidence; tests without recorded execution remain `Not run` even when test code exists.

## 2. Conventions

- **Test IDs** follow the threat model: `TC-01` through `TC-24`.
- **Threat IDs** use the STRIDE identifiers from the threat register (`S1`, `T1`, `I2`, and so on).
- **Type:** `Unit` · `Integration` · `Security` · `E2E` · `Inspection`.
- **Status:** `Not run` · `Pass` · `Fail` · `Blocked` · `Planned`.
- **Blocked** means the required implementation, test location, or repository evidence is not yet available.
- **Planned** means the test design is identified but implementation or verification work has not started.
- **Test location** must contain a repository path and test function once the test exists.
- After each run, update **Result**, **Status**, **Last run**, **Run by**, and **Commit** in the run log. Notify the threat-model owner when a threat status can change.
- A proposed test is not formal coverage until it has a row here and is included in the threat-coverage table.

## 3. Test Cases

| Test ID | Threat | Phase | What is tested | Type | Test location | Expected result | Result | Status | Last run |
|---|---|---:|---|---|---|---|---|---|---|
| TC-01 | S1 | 3 | Password hashing and generic login-failure handling for bad credentials (lockout/rate-limit excluded) | Security | `tests/unit/test_auth.py::test_password_hashing_and_verification`; `tests/integration/test_api_flow.py::test_auth_security_negative_cases` | Passwords are not stored in plaintext; invalid login attempts return rejection without account-existence details | Partial (login lockout/rate-limit not implemented) | Planned | 2026-10-20 |
| TC-02 | S2 | 3 | JWT tampering and algorithm abuse (`alg: none`, modified signature, expiry) | Security | `tests/unit/test_auth.py::test_tampered_token_rejected`; `::test_insecure_algorithm_token_rejected`; `::test_expired_token_rejected`; `tests/integration/test_api_flow.py::test_auth_security_negative_cases` | Invalid/tampered/expired tokens are rejected | Pass (unit evidence recorded) | Pass | 2026-10-20 |
| TC-03 | T1 | 2 | One-byte modification of encrypted ciphertext in `{file_id}.bin` | Security | `tests/unit/test_crypto.py::test_tamper_detection`; `tests/integration/test_api_flow.py::test_tampered_document_download_blocked` | AES-GCM authentication fails; no plaintext is returned | Pass (unit evidence recorded; integration run not recorded) | Pass | 2026-10-20 |
| TC-04 | T2 | 2 | Stored file and integrity hash are replaced together | Security | TBC — integrity/HMAC tests | Replacement is detected by authenticated integrity metadata; rollback remains separately documented as residual risk | | Planned | |
| TC-05 | T3 | 4 | Audit-log entry is edited or deleted | Security | TBC — audit tests | Hash-chain or HMAC verification reports the broken or missing entry | | Blocked | |
| TC-06 | R1 | 4 | Upload/download security events are written and retrievable by authorized auditor/admin roles | Integration | `tests/integration/test_api_flow.py::test_full_security_workflow_integration`; `tests/unit/test_telemetry.py::test_audit_log_append_and_retrieval` | Upload/download/auth events are persisted and retrievable; unauthorized log access is denied | Test code exists; integration execution evidence not recorded | Not run | |
| TC-07 | I1, I6 | 1 | `.env` is ignored and untracked; startup rejects missing/short JWT secrets, malformed or invalid-length encryption keys, non-HS256 algorithm values, and out-of-range token lifetimes | Inspection + Unit | `tests/unit/test_config.py`; `.gitignore`; `app/config.py` | `.env` is not tracked; invalid configuration is rejected without exposing secrets | Pass | Verified | 2026-10-18 |
| TC-08 | I2 | 2 | Traversal payloads, absolute paths, null bytes, and Windows-style paths | Unit | `tests/unit/test_vault.py::test_directory_traversal_mitigation`; `tests/unit/test_vault.py::test_null_byte_injection_blocked` | Input is rejected or reduced to a safe filename; no path escapes `vault_storage/` | Pass | Verified | 2026-10-18 |
| TC-09 | I4 | 4 | Error responses for invalid input and server errors | Security | TBC — API tests | Responses do not expose stack traces, SQL, filesystem paths, or secrets; `/docs` handling matches the deployment decision | | Blocked | |
| TC-10 | D1 | 4 | Oversized and repeated uploads | Security | TBC — API/rate-limit tests | Oversized files return 413 or equivalent; repeated requests are throttled | | Blocked | |
| TC-11 | D2 | 4 | Executable content renamed with an allowed document extension | Security | TBC — validation tests | Magic-byte mismatch is rejected; the file is not stored or executed | | Blocked | |
| TC-12 | E1 | 3 | Staff attempts Auditor-only operation (`/audit/logs`) | Security | `tests/integration/test_api_flow.py::test_full_security_workflow_integration` | Unauthorized staff access returns 403 | Integration test exists; execution evidence not recorded in run log | Not run | |
| TC-13 | E2 | 3 | Role claim tampering inside JWT payload | Security | `tests/unit/test_auth.py::test_tampered_token_rejected` | Edited JWT payload/signature is rejected | Pass (tampered-token unit evidence recorded) | Pass | 2026-10-20 |
| TC-14 | T4 | 3 | SQL injection payloads in login, search, and metadata fields | Security | TBC — database/API tests | No authentication bypass occurs and database contents remain unchanged | | Blocked | |
| TC-15 | I5 | 2 | Ciphertext and metadata are stored separately and can be read back through the storage adapter | Unit | `tests/unit/test_vault.py::test_envelope_and_blob_storage_roundtrip`; `tests/unit/test_vault.py::test_nonexistent_blob_read_raises` | `.bin` and `.meta.json` are separate; round-trip returns the stored bytes and envelope; missing files raise safely | Pass | Verified | 2026-10-18 |
| TC-16 | E1, T1, I5 | 4 | End-to-end login, upload, encryption, authorized download, and denied Auditor-only access by Staff | E2E | `tests/integration/test_api_flow.py::test_full_security_workflow_integration` | Happy-path workflow succeeds and restricted endpoint access is denied | Test exists; no integration run evidence recorded in run log | Not run | |
| TC-17 | I7 | 2 | Repeated encryption of identical plaintext produces unique nonces and ciphertexts | Unit | `tests/unit/test_crypto.py::test_random_nonce_produces_unique_ciphertexts` | Each encryption uses a unique 96-bit nonce and decrypts successfully | Pass | Pass | 2026-10-20 |
| TC-18 | S3 | 3 | A copied JWT is replayed after logout or expiry; revocation behavior is checked | Security | TBC — auth tests | Expired or revoked token is rejected; tokens are not written to logs | | Planned | |
| TC-19 | I8 | 4 | Audit events redact sensitive fields (password/token/authorization) from logged details | Security | `tests/unit/test_telemetry.py::test_sensitive_credential_redaction` | Sensitive values are replaced with `[REDACTED]` and never written in clear text | Pass | Pass | 2026-10-20 |
| TC-20 | D3 | 4 | Repeated failed requests flood the audit log | Security | TBC — API/audit/rate-limit tests | Rate limiting and log controls prevent uncontrolled growth or loss of meaningful events | | Blocked | |
| TC-21 | D4 | 4 | Missing, replaced, or corrupted encryption key; setup behavior with an existing `.env` | Security + Inspection | TBC — configuration/setup tests | Setup does not overwrite `.env`; invalid key prevents unsafe startup; recovery procedure is documented | | Planned | |
| TC-22 | T5 | 3–4 | Dependency versions, known vulnerabilities, package integrity, and dependency-review process | Inspection + Security | TBC — `pip-audit`/dependency workflow | Security-sensitive dependencies are reviewed and pinned or constrained safely; known high-risk issues are addressed | | Planned | |
| TC-23 | T6 | 4 | Branch protection, required reviews/checks, CODEOWNERS for workflows, action pinning, and MFA governance | Inspection | Repository settings and `.github/` configuration | Required repository controls are enabled and documented; workflow changes require review | | Not run | |
| TC-24 | E1 | 4 | Staff attempts to download a document owned by another Staff user | E2E / Security | `tests/integration/test_api_flow.py` (planned update) | Request returns `403 Forbidden`; document is not returned; `ACCESS_DENIED` is logged with `status: "BLOCKED"` | Not run | Planned | |

> TC-16 through TC-23 were introduced with threat-model v0.6. Integration and inspection cases remain `Not run` or `Planned` until execution evidence is recorded in §6.

## 4. Current Evidence and Execution Guidance

The following commands can be run against the current repository:

```bash
python -m pytest tests/unit/test_config.py tests/unit/test_vault.py -v
python -m pytest tests/unit/test_crypto.py -v
python -m pytest tests/unit -v
```

| Test ID | Current evidence | Action |
|---|---|---|
| TC-02 / TC-03 / TC-13 / TC-17 / TC-19 | Unit-test evidence recorded in `python -m pytest tests/unit/ -v` (2026-10-20, commit `c68d20e`) | Keep mapped to unit evidence until integration run evidence is added. |
| TC-07 | Configuration-validation tests in `tests/unit/test_config.py`, `.gitignore`, and `app/config.py` | Confirm the recorded commit and environment-inspection evidence. |
| TC-08 | `test_directory_traversal_mitigation` and `test_null_byte_injection_blocked` | Evidence is recorded for the listed run; retain output if rerun. |
| TC-15 | `test_envelope_and_blob_storage_roundtrip` and `test_nonexistent_blob_read_raises` | Evidence is recorded for the listed run; retain output if rerun. |
| TC-06 / TC-12 / TC-16 | Integration tests exist in `tests/integration/test_api_flow.py` | Execute and record a dedicated integration run before upgrading status from `Not run`. |

Do not mark a test `Pass` or a threat `Verified` based only on source inspection. A test run, result, executor, date, and commit evidence are required.

## 5. Threat Coverage

Every threat in [`THREAT_MODEL.md`](THREAT_MODEL.md) §6 is listed below. A threat without an executable test has a reason recorded in the final column.

| Threat | Short description | Risk | Test(s) | Coverage | Reason / next action |
|---|---|---|---|---|---|
| S1 | Password guessing / credential stuffing | High (9) | TC-01 | Planned | Auth service and rate limiting are TBC. |
| S2 | Forged JWT | High (6) | TC-02 | Pass | Unit evidence covers tampered/`alg:none`/expired token rejection; integration evidence is not yet recorded. |
| S3 | Stolen JWT replay | High (6) | TC-18 | Planned | Revocation and replay handling are TBC. |
| T1 | Ciphertext altered on disk | High (6) | TC-03, TC-16 | Partial | Unit tamper-detection evidence is recorded; end-to-end integration execution is not yet recorded. |
| T2 | File and hash replaced / rollback | Medium (3) | TC-04 | Planned | HMAC protection is not implemented; rollback remains residual risk. |
| T3 | Audit log edited or deleted | High (6) | TC-05 | Blocked | Audit logger and verification routine are TBC. |
| T4 | SQL injection | High (6) | TC-14 | Blocked | Database/API implementation is TBC. |
| T5 | Vulnerable or malicious dependency | High (6) | TC-22 | Planned | Dependency versions are not pinned and dependency audit is not yet configured. |
| T6 | CI workflow or branch tampering | Medium (3) | TC-23 | Not run | Repository settings and CODEOWNERS evidence require inspection. |
| R1 | User denies an action | Medium (4) | TC-06 | Not run | Audit logger is implemented, but integration execution evidence for endpoint-generated events is not yet recorded. |
| I1 | Keys exposed through the repository | High (6) | TC-07 | Verified | `.env` is ignored and configuration-validation evidence is recorded. |
| I2 | Path traversal | High (6) | TC-08 | Verified | Vault path-defense tests passed and are recorded. |
| I3 | Interception in transit | High (6) | — | Not tested | HTTPS is a deployment requirement under the threat-model assumptions. |
| I4 | Errors or API docs reveal internals | Low (2) | TC-09 | Blocked | API error behavior and production docs configuration are TBC; `/docs` is accepted for the demo. |
| I5 | Stolen disk or backup | High (6) | TC-15, TC-16 | Partial | Storage isolation is verified; complete upload/download integration remains planned. |
| I6 | Master-key compromise | Medium (3) residual | TC-07 | Partial | Configuration validation exists; no HSM or per-file wrapping exists. |
| I7 | AES-GCM nonce reuse | High (6) | TC-17 | Pass | Unit nonce-uniqueness evidence is recorded in the unit-suite run log entry (2026-10-20). |
| I8 | Sensitive audit-log content | Medium (4) | TC-19 | Pass | Unit redaction test evidence is recorded in the unit-suite run log entry (2026-10-20). |
| D1 | Oversized or repeated uploads | Medium (4) | TC-10 | Blocked | Upload limits and rate limiting are TBC. |
| D2 | Disguised file type | Medium (4) | TC-11 | Blocked | Magic-byte validation is TBC. |
| D3 | Audit-log flooding | Medium (4) | TC-20 | Blocked | Audit logger, rotation, and rate limiting are TBC. |
| D4 | Encryption-key loss | High (6) | TC-21 | Planned | Setup does not overwrite `.env`; backup, recovery, and canary checks are TBC. |
| E1 | IDOR / cross-owner access | High (9) | TC-12, TC-16, TC-24 | Partial | Staff ownership enforcement and denied-access auditing are implemented; execute and record TC-24 before any `Verified` claim. |
| E2 | Edited role claim | High (6) | TC-13 | Pass | Tampered-token rejection has unit run evidence; DB-backed role reload remains future hardening. |
| E3 | Insider administrator misuse | Medium (3) residual | — | Not tested | Residual risk mitigated by planned logging and least privilege. |
| E4 | Direct database role tampering | Medium (3) | — | N/A | No database in this build; roles are fixed in seed accounts. Re-assess when a persistent user store is added. |

## 6. Run Log

| Date | Run by | Command | Total | Pass | Fail | Blocked | Commit | Notes |
|---|---|---|---:|---:|---:|---:|---|---|
| 2026-10-18 | Copilot | `python -m pytest tests/unit/test_config.py tests/unit/test_vault.py -v` | 22 | 22 | 0 | 0 | `f2f3078` | Configuration, path-defense, and storage tests passed. |
| 2026-10-18 | Copilot | `python -m pytest tests/unit -v` | 42 | 42 | 0 | 0 | `f2f3078` | Full unit suite passed after the security-hardening changes. |
| 2026-10-18 | Copilot | `python -m pytest tests/unit/test_crypto.py -v` | TBC | TBC | TBC | TBC | TBC | Historical placeholder entry retained; superseded by 2026-10-20 full unit-suite evidence row. |
| 2026-10-20 | Dhruvi Sorathiya (Security QA & Demonstration Lead) | `python -m pytest tests/unit/test_crypto.py -v` | 20 | 20 | 0 | 0 | TBC | Independent local QA execution; crypto suite passed 20/20. |
| 2026-10-20 | Dhruvi Sorathiya (Security QA & Demonstration Lead) | `python -m pytest tests/unit/test_vault.py -v` | 13 | 13 | 0 | 0 | TBC | Independent local QA execution; vault storage and path-defense suite passed 13/13. |
| 2026-10-20 | Dhruvi Sorathiya (Security QA & Demonstration Lead) | `python -m pytest tests/unit/ -v` | 49 | 49 | 0 | 0 | `10a7ecd` | Auth/RBAC validation completed after latest PR #13 update; all 49 tests passed. |
| 2026-10-20 | Dhruvi Sorathiya (Security QA & Demonstration Lead) | `python -m pytest tests/unit/ -v` | 53 | 53 | 0 | 0 | `c68d20e` | Final local QA run including audit/telemetry; 53/53 tests passed. `python -m ruff check .` also reported `All checks passed!`. |
| 2026-10-23 | Copilot (documentation sync) | `tests/integration/test_api_flow.py` evidence review | n/a | n/a | n/a | n/a | `96e6e76` baseline | Integration test code exists for upload/download/RBAC/auth-negative/tamper flows, but no recorded execution evidence was found in this matrix; TC-06/TC-12/TC-16 remain `Not run` and TC-24 remains planned. |

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
| v0.2 | 2026-10-19 | D. Williams | Synchronized with threat-model v0.6: added TC-16 through TC-23, corrected TC-03/TC-07/TC-08/TC-15 evidence mappings, updated linked document versions and baseline commit, and added coverage for new supply-chain, CI, replay, nonce, audit-log, key-loss, and database-tampering threats. |
| v0.3 | 2026-10-22 | Dhruvi Sorathiya | Added independent QA execution evidence for crypto (20/20), vault (13/13), Auth/RBAC (49/49), and audit/telemetry (53/53), including Ruff validation results. |
| v0.3 | 2026-10-23 | Copilot | Synchronized header/baseline and linked versions (`main@ac6584d...`, threat model v1.0, documentation guide v0.9); reconciled TC status/location/evidence with current unit and integration sources; kept integration-only rows conservative as `Not run` without explicit run evidence. |
| v0.4 | 2026-10-23 | Copilot | Synchronized to `main@96e6e764...` after merged PR #22; added TC-24 for Staff cross-owner download denial (`403` + `ACCESS_DENIED`/`BLOCKED`) and kept its status as planned pending execution evidence. |
