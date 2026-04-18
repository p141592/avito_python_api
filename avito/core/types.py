"""Общие transport-типы и типизированные контейнеры ответов."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


class ApiTimeouts(BaseSettings):
    """Явные таймауты для HTTP-запросов SDK."""

    model_config = SettingsConfigDict(
        env_prefix="AVITO_TIMEOUT_",
        env_file=".env",
        extra="ignore",
    )

    connect: float = 5.0
    read: float = 15.0
    write: float = 15.0
    pool: float = 5.0


@dataclass(slots=True, frozen=True)
class RequestContext:
    """Контекст запроса transport-слоя с политиками retry и auth."""

    operation_name: str
    allow_retry: bool = False
    requires_auth: bool = True
    timeout: ApiTimeouts | None = None
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BinaryResponse:
    """Типизированный бинарный ответ API."""

    content: bytes
    content_type: str | None
    filename: str | None
    status_code: int
    headers: Mapping[str, str]


@dataclass(slots=True, frozen=True)
class TransportDebugInfo:
    """Безопасный снимок transport-конфигурации для диагностики интеграции."""

    base_url: str
    requires_auth: bool
    timeout_connect: float
    timeout_read: float
    timeout_write: float
    timeout_pool: float
    retry_max_attempts: int
    retryable_methods: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class JsonPage[ItemT]:
    """Типизированная страница результатов списочного ответа."""

    items: list[ItemT]
    total: int | None = None
    page: int | None = None
    per_page: int | None = None
    next_cursor: str | None = None

    @property
    def has_next(self) -> bool:
        """Показывает, есть ли следующая страница или курсор."""

        if self.next_cursor:
            return True
        if self.total is None or self.page is None or self.per_page is None:
            return False
        return self.page * self.per_page < self.total


__all__ = (
    "ApiTimeouts",
    "BinaryResponse",
    "HttpMethod",
    "JsonPage",
    "RequestContext",
    "TransportDebugInfo",
)
