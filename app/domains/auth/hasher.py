"""
app/domains/auth/hasher.py
Hardened Bcrypt password hashing implementation fulfilling PasswordHasherProtocol.
"""

import bcrypt

from app.domains.auth.protocols import PasswordHasherProtocol


class BcryptPasswordHasher(PasswordHasherProtocol):
    """
    Direct Bcrypt implementation enforcing UTF-8 encoding and automatic salting.
    Defends against rainbow table attacks and credential stuffing (STRIDE S1).
    """

    def hash_password(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("[SECURITY ALERT] Password cannot be empty.")

        # Bcrypt limits input passwords to 72 bytes
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError("[SECURITY ALERT] Password cannot exceed 72 bytes.")

        # Generate salt with standard work factor and hash
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False

        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError):
            return False