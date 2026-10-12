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

"""
tests/unit/test_crypto.py
Extended test suite covering Security QA edge cases and boundary defense.
"""

# --------------------------------------------------------------------------
# Security QA Edge Cases Suite (Proposed by Dhruvi)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("invalid_key", [
    b"",                       # Empty byte sequence (0 bytes)
    b"short_16_bytes!!",      # Under-sized key (16 bytes / AES-128)
    b"a" * 31,                # Boundary check: 1 byte short (31 bytes)
    b"a" * 33,                # Boundary check: 1 byte over (33 bytes)
    b"a" * 64,                # Over-sized key (64 bytes)
])
def test_invalid_key_length_rejection(invalid_key: bytes):
    """
    [Edge Case 1: Key Boundary Validation]
    Ensure AesGcmCipherEngine strictly rejects master keys that are not 
    exactly 32 bytes (256 bits) during engine initialization.
    """
    with pytest.raises(ValueError, match="32-byte"):
        AesGcmCipherEngine(key=invalid_key)


def test_wrong_key_decryption_rejected():
    """
    [Edge Case 2: Cryptographic Isolation & Integrity]
    Verify that decrypting authenticated ciphertext with an invalid key 
    fails immediately due to authentication tag mismatch (AEAD property).
    """
    key_alice = os.urandom(32)
    key_bob = os.urandom(32)

    engine_alice = AesGcmCipherEngine(key=key_alice)
    engine_bob = AesGcmCipherEngine(key=key_bob)

    raw_data = b"CONFIDENTIAL_FINANCIAL_RECORD_2026"
    ciphertext = engine_alice.encrypt(raw_data)

    # Attempt to decrypt Alice's ciphertext using Bob's key
    with pytest.raises(ValueError, match="Decryption failed"):
        engine_bob.decrypt(ciphertext)


@pytest.mark.parametrize("invalid_payload", [
    "plain_string_data",       # String primitive
    123456789,                 # Integer primitive
    {"key": "value"},          # Dictionary
    ["list", "items"],         # List
    None,                      # NoneType
])
def test_non_byte_input_rejected(invalid_payload):
    """
    [Edge Case 3: Type Safety & Input Validation]
    Verify that non-byte types are rejected with a TypeError at the entry 
    boundary for both encryption and decryption pipelines.
    """
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)

    # 1. Reject non-byte input during encryption
    with pytest.raises(TypeError, match="bytes format"):
        engine.encrypt(invalid_payload)

    # 2. Reject non-byte input during decryption
    with pytest.raises(TypeError, match="bytes format"):
        engine.decrypt(invalid_payload)


@pytest.mark.parametrize("malformed_payload", [
    b"",                       # 0 bytes (Empty payload)
    b"too_short",              # 9 bytes (Header truncated)
    os.urandom(27),            # 27 bytes (1 byte short of minimum 28-byte GCM payload)
])
def test_malformed_ciphertext_rejected(malformed_payload: bytes):
    """
    [Edge Case 4: Truncated Payload Defense]
    Verify that ciphertexts shorter than the minimum header size 
    (12-byte Nonce + 16-byte Auth Tag = 28 bytes) are rejected before decryption.
    """
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)

    with pytest.raises(ValueError, match="too short or malformed"):
        engine.decrypt(malformed_payload)


def test_random_nonce_produces_unique_ciphertexts():
    """
    [Edge Case 5: CSPRNG Entropy Verification]
    Verify that encrypting identical plaintext multiple times yields unique 
    ciphertexts and unique nonces, preventing replay attacks and pattern leakage.
    """
    key = os.urandom(32)
    engine = AesGcmCipherEngine(key=key)
    identical_plaintext = b"CONFIDENTIAL_PAYROLL_DATA"

    # Encrypt identical data 10 times consecutively
    generated_ciphertexts = [engine.encrypt(identical_plaintext) for _ in range(10)]

    # 1. Assert all 10 ciphertext payloads are distinct
    unique_ciphertexts = set(generated_ciphertexts)
    assert len(unique_ciphertexts) == 10

    # 2. Assert all 10 extracted 12-byte nonces are distinct
    nonces = {ct[:12] for ct in generated_ciphertexts}
    assert len(nonces) == 10

    # 3. Assert all distinct ciphertexts decrypt back to the original plaintext
    for ct in generated_ciphertexts:
        assert engine.decrypt(ct) == identical_plaintext