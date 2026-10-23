# Role-Based Secure Financial Document Vault

Enterprise-grade document repository tailored for financial environments featuring AES-256 encryption at rest, real-time SHA-256 integrity verification, JWT-based RBAC, and tamper-resistant audit logging.

> **Academic Context**: Master of Information Security (MCSC-6002), Humber Polytechnic  
> **Target Due Date**: **Saturday, October 24, 2026 (23:59 EDT)**  
> **Master Schedule**: Detailed 2-week sprint tasks & RACI checklist are tracked in **[docs/wbs.md](docs/wbs.md)**.

---

## 👥 Team Roles & Responsibilities (RACI)

- **OhUk Kwon** (Lead System Architect & Core Developer)
  - System architecture, AES-256-GCM cipher engine, isolated vault storage, 3-tier RBAC guards, and API composition root.
- **Dhruvi Sorathiya** (Security QA & Demonstration Lead)
  - Security test suites (`pytest`), path traversal injection testing, negative test cases, and live attack demonstration scripts.
- **David Williams** (Threat Modeling & Documentation Lead)
  - STRIDE threat modeling, security architecture documentation, compliance mapping, and final presentation slide deck.

---

## 🗺️ High-Level Milestone Roadmap

- [x] **Phase 1: Core Cryptography (10/08 - 10/11)**: AES-256-GCM authenticated cipher, SHA-256 hasher, unit test suite (`PR #1`, `PR #2`)
- [x] **Phase 2: Secure Vault Storage (10/11 - 10/14)**: Canonical path traversal defense (`../`), encrypted envelope disk I/O (`PR #3`)
- [x] **Phase 3: 3-Tier RBAC & Auth (10/14 - 10/17)**: Bcrypt password hashing, JWT token lifecycle, role-based route guards (`PR #5`)
- [x] **Phase 4: Audit & Telemetry (10/17 - 10/20)**: Append-only JSONL logger, immutable audit schema, sensitive credential redaction (`PR #6`)
- [ ] **Phase 5: System Integration & Final Delivery (10/20 - 10/24)**: Partial completion — integration/security fixes are merged; final verification and delivery artifacts remain
  - [x] Composition root wiring and protected API route integration
  - [x] Swagger UI verification and automated E2E test suite implementation
  - [x] Staff object-level download authorization (`owner_id` check with 403 + `ACCESS_DENIED`/`BLOCKED`)
  - [x] AES-256 key handling corrected to use the validated decoded 32-byte key
  - [x] Demo telemetry viewer stored-XSS mitigation via HTML escaping
  - [ ] Record post-merge regression/inspection evidence (including TC-24 execution evidence)
  - [ ] Final STRIDE report, live demo rehearsal, presentation deck, dry run, and Blackboard submission

👉 *For individual daily task items and sprint deadlines, please see the full [Work Breakdown Structure (WBS)](docs/wbs.md).*

---

## 🚀 Quick Start (Local Setup)

For complete development environment setup instructions on Windows 11, please refer to our **[Setup Guideline](setup_guideline.md)**.

```cmd
# 1. Run automated environment setup
.\setup.bat

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Verify core packages and domain modules
python -c "import fastapi, cryptography, jose, pydantic, dotenv, pytest; from app.domains.vault.disk_storage import DiskVaultStorage; from app.domains.crypto.aes_engine import AesGcmCipherEngine; print('[SUCCESS] Core packages and vault modules loaded successfully!')"

# 4. Run automated test suite
pytest tests/unit/ -v
