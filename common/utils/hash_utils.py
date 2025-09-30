"""
Hash utilities used across services.
"""

from __future__ import annotations

import hashlib
from typing import Union


def sha256_bytes_to_hex(data: Union[bytes, bytearray, memoryview]) -> str:
    """Return hex digest of SHA-256 for given bytes-like object."""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


