import base64
import binascii
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class AppSettings(BaseModel):
    # Application Configuration
    project_name: str = Field(
        default_factory=lambda: os.getenv("PROJECT_NAME", "Role-Based Secure Financial Document Vault")
    )
    api_v1_str: str = Field(default_factory=lambda: os.getenv("API_V1_STR", "/api/v1"))

    # Cryptographic Keys
    encryption_key: str = Field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", os.getenv("FERNET_SECRET_KEY", "")))
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    algorithm: str = Field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = Field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    )

    # Database & Storage
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./vault.db"))
    storage_dir: str = Field(default_factory=lambda: os.getenv("STORAGE_DIR", "./vault_storage"))

    @staticmethod
    def _decode_encryption_key(key_value: str) -> bytes:
        normalized = key_value.strip()
        if not normalized:
            raise ValueError("[CRITICAL] ENCRYPTION_KEY (or legacy FERNET_SECRET_KEY) is not set.")
        padding = "=" * (-len(normalized) % 4)
        try:
            decoded = base64.urlsafe_b64decode(f"{normalized}{padding}")
        except (binascii.Error, ValueError) as exc:
            raise ValueError("[CRITICAL] ENCRYPTION_KEY must be valid URL-safe base64.") from exc
        if len(decoded) != 32:
            raise ValueError(
                "[CRITICAL] ENCRYPTION_KEY must decode to exactly 32 bytes for AES-256-GCM."
            )
        return decoded

    def validate_keys(self) -> None:
        """Checks the validity of the default security keys."""
        self._decode_encryption_key(self.encryption_key)
        if len(self.jwt_secret_key.encode("utf-8")) < 32:
            raise ValueError("[CRITICAL] JWT_SECRET_KEY must be at least 32 bytes.")
        if self.algorithm != "HS256":
            raise ValueError("[CRITICAL] ALGORITHM must be HS256.")
        if self.access_token_expire_minutes < 1 or self.access_token_expire_minutes > 15:
            raise ValueError("[CRITICAL] ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 15.")

settings = AppSettings()
settings.validate_keys()