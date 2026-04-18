"""Иерархия исключений SDK Avito."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(slots=True)
class AvitoError(Exception):
    """Базовое исключение SDK с метаданными HTTP-ответа."""

    message: str
    status_code: int | None = None
    error_code: str | None = None
    payload: object | None = None
    headers: Mapping[str, str] | None = None

    def __str__(self) -> str:
        details: list[str] = [self.message]
        if self.status_code is not None:
            details.append(f"status={self.status_code}")
        if self.error_code is not None:
            details.append(f"code={self.error_code}")
        return " ".join(details)


class TransportError(AvitoError):
    """Сбой HTTP-транспорта до получения корректного ответа API."""


class AuthenticationError(AvitoError):
    """Ошибка аутентификации или получения access token."""


class PermissionDeniedError(AvitoError):
    """Недостаточно прав для выполнения операции."""


class NotFoundError(AvitoError):
    """Запрошенный ресурс не найден."""


class ValidationError(AvitoError):
    """API отклонил запрос из-за некорректных параметров."""


class RateLimitError(AvitoError):
    """Превышен лимит запросов API."""


class ClientError(AvitoError):
    """Прочая клиентская ошибка диапазона `4xx`."""


class ServerError(AvitoError):
    """Серверная ошибка диапазона `5xx`."""


class ResponseMappingError(AvitoError):
    """Не удалось безопасно преобразовать ответ API в ожидаемый тип."""


__all__ = (
    "AuthenticationError",
    "AvitoError",
    "ClientError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ResponseMappingError",
    "ServerError",
    "TransportError",
    "ValidationError",
)
