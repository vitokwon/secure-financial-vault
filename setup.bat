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
) else (
    echo [*] Virtual environment .venv already exists.
)

REM 3. Installing dependencies within virtual environment
echo [*] Installing all dependencies from requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

REM 4. Duplicate configuration file
if not exist ".env" (
    echo [*] Creating .env from .env.example...
    copy .env.example .env >nul
) else (
    echo [*] .env already exists.
)

REM 5. Create vault storage directory
if not exist "vault_storage" (
    echo [*] Initializing vault_storage directory...
    mkdir vault_storage
)

REM 6. Verification Self-Test
echo ========================================================
echo  [Step 1] Running Self-Verification Test...
echo ========================================================
python -c "import fastapi, cryptography, jose; print('[SUCCESS] Core packages loaded without errors!')"
if %errorlevel% neq 0 (
    echo [FAIL] Verification failed. Please check requirements.txt compatibility.
    pause
    exit /b 1
)

echo ========================================================
echo  [COMPLETE] Environment is ready for development and QA!
echo  Next step: Type '.venv\Scripts\activate' in terminal.
echo ========================================================
pause