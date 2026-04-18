"""Мапперы low-level auth payload -> dataclass."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from avito.auth.models import AccessToken, TokenResponse
from avito.core.exceptions import ResponseMappingError


def map_token_response(payload: object, *, now: datetime | None = None) -> TokenResponse:
    """Преобразует OAuth payload в типизированную модель токена."""

    if not isinstance(payload, dict):
        raise ResponseMappingError("OAuth-ответ должен быть JSON-объектом.", payload=payload)

    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise ResponseMappingError("В OAuth-ответе отсутствует `access_token`.", payload=payload)

    raw_expires_in = payload.get("expires_in", 0)
    if not isinstance(raw_expires_in, int):
        raise ResponseMappingError("Поле `expires_in` должно быть целым числом.", payload=payload)

    refresh_token = payload.get("refresh_token")
    if refresh_token is not None and not isinstance(refresh_token, str):
        raise ResponseMappingError("Поле `refresh_token` должно быть строкой.", payload=payload)

    token_type = payload.get("token_type", "Bearer")
    if not isinstance(token_type, str):
        raise ResponseMappingError("Поле `token_type` должно быть строкой.", payload=payload)

    issued_at = now or datetime.now(UTC)
    return TokenResponse(
        access_token=AccessToken(
            value=access_token,
            expires_at=issued_at + timedelta(seconds=raw_expires_in),
            token_type=token_type,
        ),
        refresh_token=refresh_token,
        scope=payload.get("scope") if isinstance(payload.get("scope"), str) else None,
    )


__all__ = ("map_token_response",)
