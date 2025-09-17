"""
Dependency utilities used by public API routers.

Provides AuthContext and require_auth_context to match existing imports.
This minimal version trusts the caller and extracts "user_id" from headers
or query for development purposes. Replace with real auth as needed.
"""

from __future__ import annotations

from typing import TypedDict
from fastapi import Depends, HTTPException, Request


class AuthContext(TypedDict):
    user_id: str


async def require_auth_context(request: Request) -> AuthContext:
    # Minimal implementation for development: accept X-User-ID header
    user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: missing user context")
    return {"user_id": user_id}


def require_internal_auth(func):  # shim to preserve import if needed elsewhere
    from shared.auth import require_internal_auth as real

    return real(func)


