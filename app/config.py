import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AppSettings(BaseModel):
    # Application Configuration
    project_name: str = os.getenv("PROJECT_NAME", "Role-Based Secure Financial Document Vault")
    api_v1_str: str = os.getenv("API_V1_STR", "/api/v1")

    # Cryptographic Keys
    fernet_secret_key: str = os.getenv("FERNET_SECRET_KEY", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Database & Storage
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vault.db")
    storage_dir: str = os.getenv("STORAGE_DIR", "./vault_storage")

    def validate_keys(self) -> None:
        """Checks the validity of the default security keys."""
        if not self.fernet_secret_key:
            raise ValueError("[CRITICAL] FERNET_SECRET_KEY has not been set.")
        if not self.jwt_secret_key:
            raise ValueError("[CRITICAL] JWT_SECRET_KEY is not set.")

settings = AppSettings()
settings.validate_keys()