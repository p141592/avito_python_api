"""Политики retry и решения transport-слоя."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from typing import Literal

from avito._env import (
    parse_env_bool,
    parse_env_float,
    parse_env_int,
    parse_env_str_tuple,
    resolve_env_aliases,
)

RetryReason = Literal[
    "transport_error", "timeout", "rate_limit", "server_error", "unauthorized_refresh"
]


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    """Конфигурация повторных попыток для transport-слоя."""

    ENV_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "max_attempts": ("AVITO_RETRY_MAX_ATTEMPTS",),
        "backoff_factor": ("AVITO_RETRY_BACKOFF_FACTOR",),
        "retryable_methods": ("AVITO_RETRY_RETRYABLE_METHODS",),
        "retry_on_rate_limit": ("AVITO_RETRY_RETRY_ON_RATE_LIMIT",),
        "retry_on_server_error": ("AVITO_RETRY_RETRY_ON_SERVER_ERROR",),
        "retry_on_transport_error": ("AVITO_RETRY_RETRY_ON_TRANSPORT_ERROR",),
        "max_rate_limit_wait_seconds": ("AVITO_RETRY_MAX_RATE_LIMIT_WAIT_SECONDS",),
    }

    max_attempts: int = 3
    backoff_factor: float = 0.5
    retryable_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS", "PUT", "DELETE")
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True
    retry_on_transport_error: bool = True
    max_rate_limit_wait_seconds: float = 30.0

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = ".env") -> RetryPolicy:
        """Загружает retry-политику из process environment и optional `.env` файла."""

        resolved_values = resolve_env_aliases(cls.ENV_ALIASES, env_file=env_file)
        parsed_values: dict[str, object] = {}
        for field_name, value in resolved_values.items():
            if field_name == "max_attempts":
                parsed_values[field_name] = parse_env_int(value, field_name=field_name)
            elif field_name in {"backoff_factor", "max_rate_limit_wait_seconds"}:
                parsed_values[field_name] = parse_env_float(value, field_name=field_name)
            elif field_name == "retryable_methods":
                parsed_values[field_name] = parse_env_str_tuple(value, field_name=field_name)
            else:
                parsed_values[field_name] = parse_env_bool(value, field_name=field_name)
        return cls(**parsed_values)

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
