# Role-Based Secure Financial Document Vault

Enterprise-grade document repository tailored for financial environments featuring AES-256 encryption at rest, real-time SHA-256 integrity verification, JWT-based RBAC, and tamper-resistant audit logging.

## Team Members & RACI Matrix
- **OhUk Kwon**: Lead System Architect & Core Security Developer (Architecture, RBAC, Cryptography)
- **David Williams**: Threat Modeling & Technical Documentation Lead (STRIDE Model, Technical Report)
- **Dhruvi Sorathiya**: Security QA, Validation & Demonstration Lead (Input Validation, Audit Logging, Test Scenarios)

---

## Quick Start (Developer Setup)

### 1. Clone Repository
```bash
git clone [https://github.com/vitokwon/secure-financial-vault.git](https://github.com/vitokwon/secure-financial-vault.git)
cd secure-financial-vault

## Directory Layout & Module Responsibilities
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