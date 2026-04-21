"""Типизированные модели аутентификации SDK."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True, frozen=True)
class AccessToken:
    """Токен доступа с моментом истечения срока действия."""

    value: str
    expires_at: datetime
    token_type: str = "Bearer"

    def is_expired(self, now: datetime, *, leeway: timedelta = timedelta(seconds=30)) -> bool:
        """Проверяет, что токен уже истек или почти истекает."""

        return now >= self.expires_at - leeway


@dataclass(slots=True, frozen=True)
class TokenResponse:
    """Нормализованный OAuth-ответ с access token и optional refresh token."""

    access_token: AccessToken
    refresh_token: str | None = None
    scope: str | None = None


@dataclass(slots=True, frozen=True)
class ClientCredentialsRequest:
    """Параметры запроса токена по `client_credentials`."""

    client_id: str
    client_secret: str
    scope: str | None = None


@dataclass(slots=True, frozen=True)
class RefreshTokenRequest:
    """Параметры запроса токена по `refresh_token`."""

    client_id: str
    client_secret: str
    refresh_token: str
    scope: str | None = None


__all__ = ("AccessToken", "ClientCredentialsRequest", "RefreshTokenRequest", "TokenResponse")
