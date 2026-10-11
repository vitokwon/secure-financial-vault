"""
app/domains/crypto/__init__.py
Public facade interface for the crypto domain.
Exposes core contracts and concrete implementations for encryption and hashing.
"""

from .protocols import CipherEngineProtocol, HashEngineProtocol
from .aes_engine import AesGcmCipherEngine
from .hasher import Sha256Hasher

__all__ = [
    "CipherEngineProtocol",
    "HashEngineProtocol",
    "AesGcmCipherEngine",
    "Sha256Hasher",
]