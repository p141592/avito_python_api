"""Иерархия исключений SDK Avito."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

_SECRET_KEYS = (
    "authorization",
    "access_token",
    "refresh_token",
    "token",
    "client_secret",
    "secret",
    "password",
)


def _is_secret_key(key: object) -> bool:
    return isinstance(key, str) and any(secret in key.lower() for secret in _SECRET_KEYS)


def sanitize_metadata(value: object) -> object:
    """Удаляет секреты из диагностических метаданных исключения."""

    if isinstance(value, Mapping):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            if _is_secret_key(key):
                sanitized[str(key)] = "***"
            else:
                sanitized[str(key)] = sanitize_metadata(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_metadata(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_metadata(item) for item in value)
    if isinstance(value, str) and any(secret in value.lower() for secret in _SECRET_KEYS):
        return "***"
    return value


@dataclass(slots=True)
class AvitoError(Exception):
    """Базовое исключение SDK с безопасными диагностическими метаданными."""

    message: str
    status_code: int | None = None
    error_code: str | None = None
    operation: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload: object | None = None
    headers: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        sanitized_payload = sanitize_metadata(self.payload)
        sanitized_headers = (
            sanitize_metadata(dict(self.headers)) if self.headers is not None else None
        )
        sanitized_metadata = sanitize_metadata(dict(self.metadata))
        object.__setattr__(self, "payload", sanitized_payload)
        object.__setattr__(self, "headers", sanitized_headers)
        object.__setattr__(self, "metadata", sanitized_metadata)

    def __str__(self) -> str:
        details: list[str] = [self.message]
        if self.operation is not None:
            details.append(f"operation={self.operation}")
        if self.status_code is not None:
            details.append(f"status={self.status_code}")
        if self.error_code is not None:
            details.append(f"code={self.error_code}")
        return " ".join(details)


class TransportError(AvitoError):
    """Сбой HTTP-транспорта до получения корректного ответа API."""


class AuthorizationError(AvitoError):
    """Ошибка авторизации или недостатка прав API."""


class AuthenticationError(AuthorizationError):
    """Совместимое имя ошибки аутентификации."""


class PermissionDeniedError(AuthorizationError):
    """Совместимое имя ошибки недостатка прав."""


class ValidationError(AvitoError):
    """API отклонил запрос из-за некорректных параметров."""


class ConfigurationError(ValidationError):
    """SDK сконфигурирован некорректно до выполнения HTTP-запроса."""


class RateLimitError(AvitoError):
    """Превышен лимит запросов API."""


class ConflictError(AvitoError):
    """Операция конфликтует с текущим состоянием upstream-ресурса."""


class UnsupportedOperationError(AvitoError):
    """Операция не поддерживается публичным Avito API или данным endpoint."""


class UpstreamApiError(AvitoError):
    """Неизвестная ошибка upstream API вне специализированных типов SDK."""


class ClientError(UpstreamApiError):
    """Совместимое имя прочей клиентской ошибки диапазона `4xx`."""


class ServerError(UpstreamApiError):
    """Совместимое имя серверной ошибки диапазона `5xx`."""


class NotFoundError(UpstreamApiError):
    """Запрошенный ресурс не найден."""


class ResponseMappingError(AvitoError):
    """Не удалось безопасно преобразовать ответ API в ожидаемый тип."""


__all__ = (
    "AuthenticationError",
    "AuthorizationError",
    "AvitoError",
    "ClientError",
    "ConfigurationError",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ResponseMappingError",
    "ServerError",
    "TransportError",
    "UnsupportedOperationError",
    "UpstreamApiError",
    "ValidationError",
    "sanitize_metadata",
)
