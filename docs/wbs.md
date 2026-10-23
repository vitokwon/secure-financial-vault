# 📋 Team Action Items & Sprint Checklist (Final Due: Oct 24, 2026)

> **Academic Context**: Master of Information Security (MCSC-6002), Humber Polytechnic  
> **Final Submission Deadline**: **Saturday, October 24, 2026 (23:59 EDT)**  
> **Last Updated**: October 23, 2026

---

### 👤 OhUk Kwon (Lead System Architect & Core Developer)
- [x] **[Phase 1] Core Cryptographic Engine (10/08 - 10/12)**
  - [x] Implement authenticated AES-256-GCM cipher engine (`aes_engine.py`)
  - [x] Implement SHA-256 integrity hasher with constant-time verification (`hasher.py`)
  - [x] Write and verify 5 core baseline unit tests (`test_crypto.py`)
  - [x] Open GitHub PR #1 and provide technical onboarding notes for the team
- [x] **[Phase 2] Secure Vault Storage Domain (10/13 - 10/16)**
  - [x] Implement canonical path validation and directory traversal (`../`) defense
  - [x] Implement isolated disk I/O and encrypted envelope metadata models
  - [x] Vault storage/domain integration is present on `main`
- [x] **[Phase 3] 3-Tier RBAC & Authentication Lifecycle (10/17 - 10/19)**
  - [x] Implement password hashing service using salted Bcrypt
  - [x] Implement JWT token generation and HS256 signature verification
  - [x] Implement 3-tier authorization guards (`Admin`, `Auditor`, `Staff`)
  - [x] Authentication and RBAC routes/guards are integrated on `main`
- [x] **[Phase 4] Audit Logging & API Delivery (10/19 - 10/21)**
  - [x] Implement append-only telemetry logger for security events
  - [x] Mount FastAPI routers (`/vault`, `/auth`, `/audit`) and expose Swagger UI
  - [x] Assemble dependency injection via Composition Root (`dependencies.py`)
  - [x] Integration is present on `main`
- [ ] **[Phase 5] Final Delivery Support (10/21 - 10/24)**
  - [ ] Validate live attack demonstration scripts and integration flows
  - [ ] Complete production-hardening backlog (dependency pinning + operational safeguards)
  - [ ] Upgrade audit telemetry to cryptographic integrity (hash-chain/HMAC or equivalent)
  - [ ] Review system architecture and technical implementation specs in the final report

---

### 👤 Dhruvi Sorathiya (Security QA & Demonstration Lead)
- [x] **[Phase 1 QA] Crypto Core Test Validation (10/10 - 10/13)**
  - [x] Run `pytest tests/unit/test_crypto.py -v` locally and verify 100% pass rate
  - [x] Review cryptographic edge cases and propose additional test scenarios (PR #2 merged)
  - [x] Review PR #1 and submit formal approval
- [x] **[Phase 2 QA] Storage Path Traversal Testing (10/16 - 10/17)**
  - [x] Unit tests cover traversal payload rejection and safe path handling (`tests/unit/test_vault.py`)
  - [x] Integrity/tamper rejection is covered in vault-related tests
- [x] **[Phase 3 QA] RBAC & Token Security Testing (10/18 - 10/19)**
  - [x] Validate access denial when Staff attempts Admin/Auditor operations
  - [x] Negative tests cover invalid credentials and forged JWT rejection
- [x] **[Phase 4 QA] E2E Integration Suite (10/20 - 10/21)**
  - [x] End-to-end integration test suite exists (`tests/integration/test_api_flow.py`)
- [ ] **[Phase 5 Demo] Live Attack Demo Scripts (10/21 - 10/23)**
  - [ ] Develop/validate live exploit demonstration scripts (`scripts/demo_attack.py`)
  - [ ] Rehearse live demonstration for final presentation

---

### 👤 David Williams (Threat Modeling & Documentation Lead)
- [x] **[Phase 1 Docs] STRIDE Section 1: Tampering & Info Disclosure (10/10 - 10/14)**
  - [x] Document Tampering (T) mitigations using SHA-256 integrity verification
  - [x] Document Information Disclosure (I) mitigations using AES-256-GCM encryption
- [x] **[Phase 2 Docs] STRIDE Section 2: Storage Boundary Isolation (10/15 - 10/17)**
  - [x] Analyze storage boundary threats and path traversal defense mechanisms
- [x] **[Phase 3 Docs] STRIDE Section 3: Spoofing & Privilege Escalation (10/17 - 10/19)**
  - [x] Document Spoofing (S) mitigations via Bcrypt passwords & signed JWTs
  - [x] Document Elevation of Privilege (E) mitigations via 3-tier RBAC guards
- [x] **[Phase 4 Docs] STRIDE Section 4: Repudiation & Audit Trail (10/20 - 10/21)**
  - [x] Document current audit logging controls and limitations
- [ ] **[Phase 5 Deliverables] Comprehensive Technical Report & Slides (10/21 - 10/23)**
  - [ ] Assemble final STRIDE technical report (diagrams, threat matrix, test results)
  - [ ] Design final presentation slide deck (12-18 slides, 12-15 min talk)

---

### 👥 All Team Members (Final Milestone: Oct 24)
- [ ] **Final Dry-Run (10/23)**: Rehearse working system demonstration and slide presentation
- [ ] **Blackboard Submission (10/24 by 23:59 EDT)**:
  - [ ] Tag and submit GitHub repository source code
  - [ ] Submit Technical Report (PDF, originality < 20%, AI < 20%)
  - [ ] Submit Presentation Slide Deck (`.pptx` / `.pdf`)
