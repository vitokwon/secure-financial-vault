"""
tests/unit/test_crypto.py
Unit tests verifying AES-256-GCM cipher engine operations.
"""

import os
import pytest
from app.domains.crypto.protocols import CipherEngineProtocol
from app.domains.crypto.aes_engine import AesGcmCipherEngine

from app.domains.crypto.hasher import Sha256Hasher
from app.domains.crypto.protocols import HashEngineProtocol

# protocl test
def test_cipher_protocol_conformance():
    """Verify that AesGcmCipherEngine satisfies CipherEngineProtocol."""
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)
    
    # CipherEngineProtocol 규격을 통과했는지 런타임 검증
    assert isinstance(engine, CipherEngineProtocol)

# aes crypto test
def test_encryption_and_decryption_cycle():
    """Verify that encrypted bytes can be accurately decrypted back to plaintext."""
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)

    raw_data = b"STUDENT_FINANCIAL_RECORD_2026"
    encrypted_payload = engine.encrypt(raw_data)

    # 1. Verify encryption changed the raw data
    assert encrypted_payload != raw_data

    # 2. Verify decryption recovers exact original data
    decrypted_payload = engine.decrypt(encrypted_payload)
    assert decrypted_payload == raw_data


def test_tamper_detection():
    """Verify that modified ciphertext raises a security ValueError."""
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)

    raw_data = b"TRANSFER_APPROVED"
    tampered_bytes = bytearray(engine.encrypt(raw_data))

    # Flip the last byte to simulate a malicious tampering attempt
    tampered_bytes[-1] ^= 0x01

    with pytest.raises(ValueError, match="Decryption failed"):
        engine.decrypt(bytes(tampered_bytes))

# Hasher test
def test_hash_protocol_implementation():
    """Verify that Sha256Hasher satisfies HashEngineProtocol."""
    hasher = Sha256Hasher()
    assert isinstance(hasher, HashEngineProtocol)


def test_sha256_hash_computation_and_verification():
    """Verify SHA-256 digest generation and accurate integrity check."""
    hasher = Sha256Hasher()
    sample_data = b"CONFIDENTIAL_FINANCIAL_RECORD_2026"

    digest = hasher.compute_hash(sample_data)

    # 1. SHA-256 produces exactly 64 hexadecimal characters (256 bits)
    assert len(digest) == 64
    assert isinstance(digest, str)

    # 2. Integrity verification check
    assert hasher.verify_hash(sample_data, digest) is True

    # 3. Mismatch check when data is modified
    tampered_data = b"CONFIDENTIAL_FINANCIAL_RECORD_2027"
    assert hasher.verify_hash(tampered_data, digest) is False