"""
app/domains/crypto/hasher.py
SHA-256 cryptographic hashing engine for integrity verification.
"""

import hashlib
import hmac


class Sha256Hasher:
    """
    SHA-256 hashing engine implementing HashEngineProtocol.
    Provides constant-time digest comparison to prevent timing attacks.
    """

    def compute_hash(self, data: bytes) -> str:
        """
        Calculates SHA-256 digest of input byte data.
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be in bytes format.")

        return hashlib.sha256(data).hexdigest()

    def verify_hash(self, data: bytes, expected_hash: str) -> bool:
        """
        Validates hash integrity using constant-time comparison.
        """
        if not isinstance(expected_hash, str):
            raise TypeError("Expected hash must be a string.")

        actual_hash = self.compute_hash(data)

        # hmac.compare_digest prevents timing attacks by checking strings in constant time
        return hmac.compare_digest(actual_hash.lower(), expected_hash.lower())
