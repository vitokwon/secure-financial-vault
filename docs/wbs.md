# 📋 Team Action Items & Sprint Checklist (Final Due: Oct 24, 2026)

> **Academic Context**: Master of Information Security (MCSC-6002), Humber Polytechnic  
> **Final Submission Deadline**: **Saturday, October 24, 2026 (23:59 EDT)**

---

### 👤 OhUk Kwon (Lead System Architect & Core Developer)
- [x] **[Phase 1] Core Cryptographic Engine (10/08 - 10/10)**
  - [x] Implement authenticated AES-256-GCM cipher engine (`aes_engine.py`)
  - [x] Implement SHA-256 integrity hasher with constant-time verification (`hasher.py`)
  - [x] Write and verify 5 core baseline unit tests (`test_crypto.py`)
  - [x] Open GitHub PR #1 and provide technical onboarding notes for the team
- [ ] **[Phase 2] Secure Vault Storage Domain (10/11 - 10/13)**
  - [ ] Implement canonical path validation and directory traversal (`../`) defense
  - [ ] Implement isolated disk I/O and encrypted envelope metadata models
  - [ ] Open PR #2 and merge changes into `main`
- [ ] **[Phase 3] 3-Tier RBAC & Authentication Lifecycle (10/14 - 10/16)**
  - [ ] Implement password hashing service using salted Bcrypt
  - [ ] Implement JWT token generation and HS256 signature verification
  - [ ] Implement 3-tier authorization guards (`Admin`, `Auditor`, `Staff`)
  - [ ] Open PR #3 and merge changes into `main`
- [ ] **[Phase 4] Tamper-Resistant Audit Logging & API Delivery (10/17 - 10/19)**
  - [ ] Implement append-only telemetry logger for security events
  - [ ] Mount FastAPI routers (`/vault`, `/auth`, `/audit`) and expose Swagger UI
  - [ ] Assemble dependency injection via Composition Root (`dependencies.py`)
- [ ] **[Phase 5] Final Delivery Support (10/20 - 10/24)**
  - [ ] Validate live attack demonstration scripts and integration flows
  - [ ] Review system architecture and technical implementation specs in the final report

---

### 👤 Dhruvi Sorathiya (Security QA & Demonstration Lead)
- [ ] **[Phase 1 QA] Crypto Core Test Validation (10/10 - 10/12)**
  - [ ] Run `pytest tests/unit/test_crypto.py -v` locally and verify 100% pass rate
  - [ ] Review cryptographic edge cases and propose additional test scenarios
  - [ ] Review PR #1 and submit formal approval
- [ ] **[Phase 2 QA] Storage Path Traversal Testing (10/13 - 10/14)**
  - [ ] Write unit tests for malicious traversal payloads (`../../etc/passwd`, absolute paths)
  - [ ] Write test cases verifying SHA-256 integrity rejection on tampered files
- [ ] **[Phase 3 QA] RBAC & Token Security Testing (10/16 - 10/17)**
  - [ ] Validate access denial when Staff attempts Admin/Auditor operations
  - [ ] Write negative tests for tampered JWT signatures and expired tokens
- [ ] **[Phase 4 QA] E2E Integration Suite (10/19 - 10/20)**
  - [ ] Build end-to-end integration test suite (Login → Upload/Encrypt → Role-based Download)
- [ ] **[Phase 5 Demo] Live Attack Demo Scripts (10/21 - 10/23)**
  - [ ] Develop live exploit demonstration scripts (`scripts/demo_attack.py`)
  - [ ] Rehearse live demonstration for final presentation

---

### 👤 David Williams (Threat Modeling & Documentation Lead)
- [ ] **[Phase 1 Docs] STRIDE Section 1: Tampering & Info Disclosure (10/10 - 10/14)**
  - [ ] Document Tampering (T) mitigations using SHA-256 integrity verification
  - [ ] Document Information Disclosure (I) mitigations using AES-256-GCM encryption
- [ ] **[Phase 2 Docs] STRIDE Section 2: Storage Boundary Isolation (10/14 - 10/16)**
  - [ ] Analyze storage boundary threats and path traversal defense mechanisms
- [ ] **[Phase 3 Docs] STRIDE Section 3: Spoofing & Privilege Escalation (10/16 - 10/18)**
  - [ ] Document Spoofing (S) mitigations via Bcrypt passwords & signed JWTs
  - [ ] Document Elevation of Privilege (E) mitigations via 3-tier RBAC guards
- [ ] **[Phase 4 Docs] STRIDE Section 4: Repudiation & Audit Trail (10/19 - 10/20)**
  - [ ] Document Repudiation (R) mitigations via immutable audit logging
- [ ] **[Phase 5 Deliverables] Comprehensive Technical Report & Slides (10/20 - 10/23)**
  - [ ] Assemble final STRIDE technical report (diagrams, threat matrix, test results)
  - [ ] Design final presentation slide deck (12-18 slides, 12-15 min talk)

---

### 👥 All Team Members (Final Milestone: Oct 24)
- [ ] **Final Dry-Run (10/23)**: Rehearse working system demonstration and slide presentation
- [ ] **Blackboard Submission (10/24 by 23:59 EDT)**:
  - [ ] Tag and submit GitHub repository source code
  - [ ] Submit Technical Report (PDF, originality < 20%, AI < 20%)
  - [ ] Submit Presentation Slide Deck (`.pptx` / `.pdf`)