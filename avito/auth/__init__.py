"""Пакет аутентификации."""

from __future__ import annotations

from typing import TYPE_CHECKING

from avito.auth.models import (
    AccessToken,
    ClientCredentialsRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from avito.auth.settings import AuthSettings

if TYPE_CHECKING:
    from avito.auth.provider import AlternateTokenClient, AuthProvider, TokenClient

__all__ = (
    "AccessToken",
    "AlternateTokenClient",
    "AuthProvider",
    "AuthSettings",
    "ClientCredentialsRequest",
    "RefreshTokenRequest",
    "TokenClient",
    "TokenResponse",
)


def __getattr__(name: str) -> object:
    if name in {"AlternateTokenClient", "AuthProvider", "TokenClient"}:
        from avito.auth.provider import AlternateTokenClient, AuthProvider, TokenClient

        exports = {
            "AlternateTokenClient": AlternateTokenClient,
            "AuthProvider": AuthProvider,
            "TokenClient": TokenClient,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
