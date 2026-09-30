### 📋 Developer Onboarding Checklist (Before You Start QA/Docs)

Please follow this checklist step-by-step. If all 4 checkboxes pass, your environment is 100% synchronized with the Core Backend.

- [ ] **Check 1: Python Version**
  - Open terminal and run: `python --version`
  - Ensure version is **Python 3.10 or higher**.

- [ ] **Check 2: Run Setup Script**
  - **Windows**: Double-click `setup.bat` (or run `.\setup.bat` in CMD)
  - *Wait until you see the `[COMPLETE]` message at the end.*

- [ ] **Check 3: Activate Virtual Environment**
  - **Windows**: `.venv\Scripts\activate`
  - *Ensure `(.venv)` appears at the beginning of your terminal prompt.*
  - If PowerShell script error occurs, run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

- [ ] **Check 4: Final Sanity Check**
  - Run this command: `python -c "import fastapi, cryptography, jose; print('ALL GREEN')"`
  - If it prints **`ALL GREEN`**, you are ready to review PRs and execute test suites!

### 💡 Troubleshooting Tip
- If running `pip` outputs "command not found", use `python -m pip` instead: `python -m pip install -r requirements.txt`
- If pip is completely missing, restore it using: `python -m ensurepip --default-pip`