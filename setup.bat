@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo  [Step 0] Checking System Prerequisites...
echo ========================================================

REM 1. Checking Python Installation and PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH!
    echo [ACTION] Please install Python and check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [*] Python installation detected.

REM 2. Create virtual environment
if not exist ".venv" (
    echo [*] Creating virtual environment .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [FAIL] Virtual environment creation failed.
        pause
        exit /b 1
    )
) else (
    echo [*] Virtual environment .venv already exists.
)

REM 3. Installing dependencies within virtual environment
echo [*] Installing all dependencies from requirements.txt...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [FAIL] Failed to activate .venv.
    pause
    exit /b 1
)
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [FAIL] pip upgrade failed.
    pause
    exit /b 1
)
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [FAIL] Dependency installation failed.
    pause
    exit /b 1
)

REM 4. Duplicate configuration file
if not exist ".env" (
    echo [*] Creating .env from .env.example...
    copy .env.example .env >nul
    if errorlevel 1 (
        echo [FAIL] Failed to create .env from .env.example.
        pause
        exit /b 1
    )
) else (
    echo [*] .env already exists.
)

REM 5. Create vault storage directory
if not exist "vault_storage" (
    echo [*] Initializing vault_storage directory...
    mkdir vault_storage
    if errorlevel 1 (
        echo [FAIL] Failed to create vault_storage directory.
        pause
        exit /b 1
    )
)

REM 6. Verification Self-Test
echo ========================================================
echo  [Step 1] Running Self-Verification Test...
echo ========================================================
python -c "import fastapi, cryptography, jose, pydantic, dotenv, pytest; from app.domains.vault.disk_storage import DiskVaultStorage; from app.domains.crypto.aes_engine import AesGcmCipherEngine; print('[SUCCESS] Core packages and vault modules loaded successfully!')"
if errorlevel 1 (
    echo [FAIL] Verification failed. Please check requirements.txt compatibility.
    pause
    exit /b 1
)

set "SECRETS_INCOMPLETE=0"
for %%V in (ENCRYPTION_KEY JWT_SECRET_KEY) do (
    findstr /R /C:"^%%V=$" .env >nul
    if not errorlevel 1 set "SECRETS_INCOMPLETE=1"
)

if "!SECRETS_INCOMPLETE!"=="1" (
    echo [WARN] Setup stopped because required secrets in .env are still empty.
    echo [ACTION] Update ENCRYPTION_KEY and JWT_SECRET_KEY in .env before running verification.
    echo [INFO] ENCRYPTION_KEY must be URL-safe base64 that decodes to exactly 32 bytes.
    echo [INFO] JWT_SECRET_KEY must be at least 32 bytes and ALGORITHM must remain HS256.
    pause
    exit /b 1
)

python -c "from app.config import AppSettings; AppSettings().validate_keys(); print('[SUCCESS] Configuration validation passed.')"
if errorlevel 1 (
    echo [WARN] Configuration validation failed. Required secrets may be missing or invalid.
    echo [ACTION] Verify ENCRYPTION_KEY, JWT_SECRET_KEY, ALGORITHM=HS256, and ACCESS_TOKEN_EXPIRE_MINUTES (1-15) in .env.
    pause
    exit /b 1
)

echo ========================================================
echo  [COMPLETE] Environment is ready for development and QA!
echo  Next step: Type '.venv\Scripts\activate' in terminal.
echo ========================================================
pause