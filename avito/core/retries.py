"""Политики retry и решения transport-слоя."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

RetryReason = Literal[
    "transport_error", "timeout", "rate_limit", "server_error", "unauthorized_refresh"
]


class RetryPolicy(BaseSettings):
    """Конфигурация повторных попыток для transport-слоя."""

    model_config = SettingsConfigDict(
        env_prefix="AVITO_RETRY_",
        env_file=".env",
        extra="ignore",
    )

    max_attempts: int = 3
    backoff_factor: float = 0.5
    retryable_methods: tuple[str, ...] = Field(default=("GET", "HEAD", "OPTIONS", "PUT", "DELETE"))
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True
    retry_on_transport_error: bool = True
    max_rate_limit_wait_seconds: float = 30.0

    def is_retryable_method(self, method: str, *, explicit_retry: bool = False) -> bool:
        """Определяет, можно ли повторять запрос указанного HTTP-метода."""

        return explicit_retry or method.upper() in self.retryable_methods

    def compute_backoff(self, attempt: int) -> float:
        """Возвращает backoff в секундах для номера попытки, начиная с единицы."""

        safe_attempt = max(attempt - 1, 0)
        return float(self.backoff_factor) * float(2**safe_attempt)


@dataclass(slots=True, frozen=True)
class RetryDecision:
    """Решение retry-слоя по результату очередной попытки запроса."""

    should_retry: bool
    reason: RetryReason | None = None
    delay_seconds: float = 0.0


__all__ = ("RetryDecision", "RetryPolicy", "RetryReason")
