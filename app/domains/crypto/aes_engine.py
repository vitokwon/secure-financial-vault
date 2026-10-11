"""
app/domains/crypto/aes_engine.py
Concrete implementation of CipherEngineProtocol using AES-256-GCM (AEAD).
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from app.domains.crypto.protocols import CipherEngineProtocol


class AesGcmCipherEngine(CipherEngineProtocol):
    """
    AES-256 Authenticated Encryption with Associated Data (AEAD) engine.
    Satisfies CipherEngineProtocol.
    """

    # NIST recommendation for GCM initialization vector (Nonce): 96 bits (12 bytes)
    NONCE_SIZE_BYTES = 12

    def __init__(self, key: bytes):
        """
        Initializes the AES-GCM engine with a 256-bit symmetric key.

        :param key: Exactly 32 bytes (256 bits) of raw key data.
        """
        if len(key) != 32:
            raise ValueError("[CRYPTO ERROR] AES-256 requires a 32-byte (256-bit) key.")
        self._key = key
        self._engine = AESGCM(self._key)

    def encrypt(self, plain_text: bytes) -> bytes:
        """
        Encrypts plaintext bytes and prefixes the random Nonce to the payload.
        Output format: [12-byte Nonce] + [Ciphertext] + [16-byte Auth Tag]
        """
        if not isinstance(plain_text, bytes):
            raise TypeError("Plaintext must be in bytes format.")

        # Cryptographically secure random 12-byte Nonce
        nonce = os.urandom(self.NONCE_SIZE_BYTES)
        
        # AESGCM automatically appends a 16-byte authentication tag to the ciphertext
        ciphertext_with_tag = self._engine.encrypt(nonce, plain_text, associated_data=None)
        
        return nonce + ciphertext_with_tag

    def decrypt(self, cipher_text: bytes) -> bytes:
        """
        Extracts the Nonce and decrypts ciphertext while verifying the authentication tag.
        """
        if not isinstance(cipher_text, bytes):
            raise TypeError("Ciphertext must be in bytes format.")

        # Minimum required payload length: 12 bytes (Nonce) + 16 bytes (Tag) = 28 bytes
        if len(cipher_text) < self.NONCE_SIZE_BYTES + 16:
            raise ValueError("[CRYPTO ERROR] Ciphertext payload is too short or malformed.")

        nonce = cipher_text[: self.NONCE_SIZE_BYTES]
        actual_ciphertext = cipher_text[self.NONCE_SIZE_BYTES :]

        try:
            return self._engine.decrypt(nonce, actual_ciphertext, associated_data=None)
        except InvalidTag as exc:
            # Raised when the ciphertext/tag has been modified or the key is wrong
            raise ValueError("[SECURITY ALERT] Decryption failed: Data tampering or invalid key.") from exc