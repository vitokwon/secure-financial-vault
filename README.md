# Role-Based Secure Financial Document Vault

Enterprise-grade document repository tailored for financial environments featuring AES-256 encryption at rest, real-time SHA-256 integrity verification, JWT-based RBAC, and tamper-resistant audit logging.

> **Academic Context**: Master of Information Security (MCSC-6002), Humber Polytechnic  
> **Target Due Date**: **Saturday, October 24, 2026 (23:59 EDT)**  
> **Master Schedule**: Detailed 2-week sprint tasks & RACI checklist are tracked in **[docs/WBS.md](docs/WBS.md)**.

---

## 👥 Team Roles & Responsibilities (RACI)

- **OhUk Kwon** (Lead System Architect & Core Developer)
  - System architecture, AES-256-GCM cipher engine, isolated vault storage, 3-tier RBAC guards, API composition root.
- **Dhruvi Sorathiya** (Security QA & Demonstration Lead)
  - Security test suites (`pytest`), path traversal injection testing, negative test cases, live attack demonstration scripts.
- **David Williams** (Threat Modeling & Documentation Lead)
  - STRIDE threat modeling, security architecture documentation, compliance mapping, final presentation slide deck.

---

## 🗺️ High-Level Milestone Roadmap

- [x] **Phase 1: Core Cryptography (10/08 - 10/11)**: AES-256-GCM, SHA-256 hasher, unit test suite (`PR #1`)
- [ ] **Phase 2: Secure Vault Storage (10/11 - 10/14)**: Path traversal defense (`../`), encrypted envelope disk I/O
- [ ] **Phase 3: 3-Tier RBAC & Auth (10/14 - 10/17)**: Bcrypt hashing, JWT token lifecycle, role-based guards
- [ ] **Phase 4: Audit & API Delivery (10/17 - 10/20)**: Tamper-resistant logger, FastAPI routers, Swagger UI
- [ ] **Phase 5: Final Submission Sprint (10/20 - 10/24)**: Technical report (10%), live demo (25%), slides (5%)

👉 *For individual daily task items and sprint deadlines, please see the full [Work Breakdown Structure (WBS)](docs/WBS.md).*

---

## 🚀 Quick Start (Local Setup)

For complete development environment setup instructions on Windows 11, please refer to our **[Setup Guideline](setup_guideline.md)**.

```cmd
# 1. Run automated environment setup
.\setup.bat

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Verify setup
python -c "import fastapi, cryptography, jose; print('ALL GREEN')"
```


## Directory Layout & Module Responsibilities
```
1_humber_project/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Bootstrap & route registration
│   ├── config.py                   # Pydantic Settings (.env injection)
│   ├── dependencies.py             # Composition Root (Wires implementations)
│   │
│   ├── domains/                    # Clean business boundaries
│   │   ├── crypto/
│   │   │   ├── __init__.py
│   │   │   ├── protocols.py        # The Contracts (CipherEngine & HashEngine)
│   │   │   ├── aes_engine.py       # Authenticated Encryption (AES-256-GCM)
│   │   │   └── hasher.py           # Integrity Hashing (SHA-256)
│   │   │
│   │   ├── vault/
│   │   │   ├── __init__.py
│   │   │   ├── protocols.py        # The Contract (VaultStorageProtocol)
│   │   │   ├── disk_storage.py     # Concrete file writer (targets vault_storage/)
│   │   │   └── router.py           # HTTP endpoints for vault
│   │   │
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── security.py         # JWT and password hashing
│   │       └── router.py           # /auth endpoints
│   │
│   └── telemetry/                  # Cross-cutting concerns
│       └── audit_logger.py         # Security event logger
│
├── tests/                          # Clean test suite
│   ├── conftest.py
│   ├── unit/                       # Isolated tests with mock engines
│   └── integration/                # End-to-end API tests
│
├── vault_storage/                  # Binary vault directory
├── .env
├── .env.example
├── requirements.txt
├── setup.bat
├── setup_guideline.md
└── README.md
```