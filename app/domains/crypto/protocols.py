"""
app/domains/crypto/protocols.py
Defines the abstract interface (contract) for cryptographic operations.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class CipherEngineProtocol(Protocol):
    """
    Standard interface for all encryption engines in the Vault system.
    Any cipher engine (e.g., AES-GCM, Fernet, KMS) must implement these methods.
    """

    def encrypt(self, plain_text: bytes) -> bytes:
        """
        Encrypts raw plaintext bytes and returns authenticated ciphertext.

        :param plain_text: Original byte data to encrypt.
        :return: Authenticated ciphertext payload.
        """
        ...

    def decrypt(self, cipher_text: bytes) -> bytes:
        """
        Decrypts ciphertext bytes and returns the original plaintext.

        :param cipher_text: Ciphertext payload containing authentication tags.
        :return: Recovered plaintext bytes.
        :raises ValueError: If data tampering is detected or the key is invalid.
        """
        ...


@runtime_checkable
class HashEngineProtocol(Protocol):
    """
    Standard interface for cryptographic hashing and integrity verification.
    """

    def compute_hash(self, data: bytes) -> str:
        """
        Computes the hexadecimal cryptographic hash digest of the input bytes.

        :param data: Raw byte payload.
        :return: Hexadecimal hash string.
        """
        ...

    def verify_hash(self, data: bytes, expected_hash: str) -> bool:
        """
        Verifies if the computed hash matches the expected hash digest securely.

        :param data: Raw byte payload to verify.
        :param expected_hash: Pre-calculated hexadecimal digest.
        :return: True if identical, False otherwise.
        """
        ...
