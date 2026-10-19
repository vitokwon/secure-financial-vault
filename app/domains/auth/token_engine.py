"""
app/domains/auth/token_engine.py
JWT token creation and verification engine fulfilling TokenEngineProtocol.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.domains.auth.models import TokenPayload, UserRole
from app.domains.auth.protocols import TokenEngineProtocol


class JwtTokenEngine(TokenEngineProtocol):
    """
    Cryptographically signed JWT engine enforcing HS256 and strict expiration.
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256", expire_minutes: int = 15):
        if len(secret_key.encode("utf-8")) < 32:
            raise ValueError("[SECURITY CRITICAL] JWT secret key must be at least 32 bytes.")
        if algorithm != "HS256":
            raise ValueError("[SECURITY CRITICAL] Only HS256 algorithm is permitted.")

        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def issue_token(self, username: str, role: UserRole) -> str:
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=self._expire_minutes)

        claims = {
            "sub": username,
            "role": role.value,
            "exp": expire,
            "iat": now,
        }
        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": True, "verify_sub": True},
            )
            return TokenPayload(
                sub=payload["sub"],
                role=UserRole(payload["role"]),
                exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            )
        except JWTError as exc:
            raise ValueError(f"[AUTH ERROR] Invalid, tampered, or expired token: {exc}") from exc