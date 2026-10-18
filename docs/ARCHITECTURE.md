# Architecture Notes — Role-Based Secure Financial Document Vault

| Field | Value |
|---|---|
| Document owner | OhUk Kwon (Lead System Architect & Core Developer) |
| Reviewer | David Williams |
| Current version | **v0.1 — Draft** |
| Last updated | 2026-10-18 |
| Related docs | [`THREAT_MODEL.md`](THREAT_MODEL.md), [`TEST_MATRIX.md`](TEST_MATRIX.md), [`DOCUMENTATION_GUIDE.md`](DOCUMENTATION_GUIDE.md) |

---

## 1. System Status Overview

The intended vault design is a FastAPI backend that allows authenticated users to upload and download financial documents according to a three-tier role model.

The current repository implements AES-256-GCM encryption, SHA-256 integrity hashing, and isolated vault storage. Authentication, RBAC, audit logging, and full API delivery remain draft or planned components unless marked otherwise in code and tests.

## 2. Implemented vs Planned Components

| Component | Code location | Responsibility | Status |
|---|---|---|---|
| FastAPI app and config | `app/main.py`, `app/config.py` | App bootstrap, runtime settings, health endpoint, vault directory startup check | Implemented (scaffold) |
| Crypto engine | `app/domains/crypto/aes_engine.py` | AES-256-GCM authenticated encryption/decryption | Implemented |
| Integrity hasher | `app/domains/crypto/hasher.py` | SHA-256 digest generation and constant-time comparison | Implemented |
| Vault storage | `app/domains/vault/disk_storage.py`, `app/domains/vault/models.py` | Safe path confinement, encrypted blob storage, metadata envelope persistence | Implemented |
| Vault API routes | `app/domains/vault/router.py` | Upload/download HTTP routes for vault operations | TBC / planned |
| Auth service | `app/domains/auth/` | Password hashing, JWT lifecycle, user identity workflows | TBC / planned |
| RBAC guards | `app/domains/auth/` or route dependencies | Role-based authorization checks per protected route | TBC / planned |
| Audit logger | `app/telemetry/audit_logger.py` | Security event capture and tamper-evidence controls | TBC / planned |
| Composition root wiring | `app/dependencies.py`, domain routers | Dependency injection and domain router registration | TBC / planned |

## 3. Storage and Data Handling (Current)

1. The vault stores ciphertext in `{file_id}.bin` and metadata in `{file_id}.meta.json`.
2. Filenames are canonicalized and confined to the vault base directory (`resolve_safe_path`).
3. Null-byte payloads are rejected, and traversal payloads are sanitized/rejected by confinement checks.
4. Envelope metadata is validated through `EncryptedEnvelope` schema constraints.

## 4. Security Controls by Implementation State

| Control | State | Evidence |
|---|---|---|
| AES-GCM authenticated encryption at rest | Implemented | `app/domains/crypto/aes_engine.py`, `tests/unit/test_crypto.py` |
| SHA-256 integrity hashing with constant-time compare | Implemented | `app/domains/crypto/hasher.py`, `tests/unit/test_crypto.py` |
| Vault path traversal/null-byte defense | Implemented | `app/domains/vault/disk_storage.py`, `tests/unit/test_vault.py` |
| Ciphertext + envelope isolated storage | Implemented | `app/domains/vault/disk_storage.py`, `app/domains/vault/models.py`, `tests/unit/test_vault.py` |
| HMAC-protected integrity hashes | Planned / blocked | Not present in `Sha256Hasher` |
| Authentication + RBAC enforcement | Planned | No auth/RBAC route implementation currently present |
| Audit logging (append-only/hash-chain) | Planned | No logger implementation currently present |
| Request rate limiting and lockout | Planned | No limiter/lockout implementation currently present |
| Magic-byte file-type validation | Planned | No magic-byte validation module currently present |

## 5. Testability Notes

- Current executable tests are concentrated in unit suites:
  - `tests/unit/test_crypto.py`
  - `tests/unit/test_vault.py`
- Threat-linked coverage and run status are tracked in [`TEST_MATRIX.md`](TEST_MATRIX.md).
- Controls that remain planned should stay in `Planned`/`Blocked` status until implementation and executed test evidence exist.

## 6. Change Log

| Version | Date | Author | Changes |
|---|---|---|---|
| v0.1 | 2026-10-18 | O. Kwon | Added architecture notes grounded to current repository modules, clarified implemented vs planned controls, and linked to threat model and test matrix for status tracking. |
