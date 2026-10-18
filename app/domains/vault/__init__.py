"""
app/domains/vault/__init__.py
Public facade interface for the vault storage domain.
"""

from .models import EncryptedEnvelope
from .protocols import VaultStorageProtocol
from .disk_storage import DiskVaultStorage

__all__ = [
    "EncryptedEnvelope",
    "VaultStorageProtocol",
    "DiskVaultStorage",
]