import os
import base64
import binascii
import re
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
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

    # Database & Storage
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vault.db")
    storage_dir: str = os.getenv("STORAGE_DIR", "./vault_storage")

    def validate_keys(self) -> None:
        """Checks the validity of the default security keys."""
        if not self.fernet_secret_key:
            raise ValueError("[CRITICAL] FERNET_SECRET_KEY (compatibility name for AES-GCM key) has not been set.")
        try:
            decoded_aes_key = self._decode_aes_gcm_key(self.fernet_secret_key)
        except ValueError as exc:
            raise ValueError(
                "[CRITICAL] FERNET_SECRET_KEY (compatibility name for AES-GCM key) must be valid URL-safe Base64."
            ) from exc
        if len(decoded_aes_key) != 32:
            raise ValueError(
                "[CRITICAL] FERNET_SECRET_KEY (compatibility name for AES-GCM key) must decode to exactly 32 bytes for AES-256-GCM."
            )
        if not self.jwt_secret_key:
            raise ValueError("[CRITICAL] JWT_SECRET_KEY is not set.")
        if len(self.jwt_secret_key.encode("utf-8")) < 32:
            raise ValueError("[CRITICAL] JWT_SECRET_KEY must be at least 32 UTF-8 bytes.")
        if self.algorithm != "HS256":
            raise ValueError("[CRITICAL] ALGORITHM must be HS256.")
        if not 1 <= self.access_token_expire_minutes <= 15:
            raise ValueError("[CRITICAL] ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 15.")

    @staticmethod
    def _decode_aes_gcm_key(encoded_key: str) -> bytes:
        normalized_key = encoded_key.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", normalized_key):
            raise ValueError("Invalid AES-GCM key encoding.")
        padding = "=" * (-len(normalized_key) % 4)
        padded_key = normalized_key + padding
        try:
            return base64.b64decode(padded_key.encode("ascii"), altchars=b"-_", validate=True)
        except (ValueError, UnicodeEncodeError, binascii.Error) as exc:
            raise ValueError("Invalid AES-GCM key encoding.") from exc

settings = AppSettings()
settings.validate_keys()