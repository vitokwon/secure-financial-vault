"""
app/domains/vault/__init__.py
Public facade interface for the vault storage domain.
"""

from .disk_storage import DiskVaultStorage
from .models import EncryptedEnvelope
from .protocols import VaultStorageProtocol

__all__ = [
    "EncryptedEnvelope",
    "VaultStorageProtocol",
    "DiskVaultStorage",
]
