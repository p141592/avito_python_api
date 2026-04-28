"""Политики retry и решения transport-слоя."""

from __future__ import annotations

import random as random_module
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Literal

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
        "max_delay": ("AVITO_RETRY_MAX_DELAY",),
        "rate_limit_enabled": ("AVITO_RATE_LIMIT_ENABLED",),
        "rate_limit_requests_per_second": ("AVITO_RATE_LIMIT_REQUESTS_PER_SECOND",),
        "rate_limit_burst": ("AVITO_RATE_LIMIT_BURST",),
    }

    max_attempts: int = 3
    backoff_factor: float = 0.5
    retryable_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS", "PUT", "DELETE")
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True
    retry_on_transport_error: bool = True
    max_rate_limit_wait_seconds: float = 30.0
    max_delay: float = 30.0
    rate_limit_enabled: bool = False
    rate_limit_requests_per_second: float = 8.0
    rate_limit_burst: int = 8
    random_source: random_module.Random = field(
        default_factory=random_module.Random,
        repr=False,
        compare=False,
    )

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = ".env") -> RetryPolicy:
        """Загружает retry-политику из process environment и optional `.env` файла."""

        resolved_values = resolve_env_aliases(cls.ENV_ALIASES, env_file=env_file)
        defaults = cls()
        max_attempts = defaults.max_attempts
        backoff_factor = defaults.backoff_factor
        retryable_methods = defaults.retryable_methods
        retry_on_rate_limit = defaults.retry_on_rate_limit
        retry_on_server_error = defaults.retry_on_server_error
        retry_on_transport_error = defaults.retry_on_transport_error
        max_rate_limit_wait_seconds = defaults.max_rate_limit_wait_seconds
        max_delay = defaults.max_delay
        rate_limit_enabled = defaults.rate_limit_enabled
        rate_limit_requests_per_second = defaults.rate_limit_requests_per_second
        rate_limit_burst = defaults.rate_limit_burst
        for field_name, value in resolved_values.items():
            if field_name == "max_attempts":
                max_attempts = parse_env_int(value, field_name=field_name)
            elif field_name == "rate_limit_burst":
                rate_limit_burst = parse_env_int(value, field_name=field_name)
            elif field_name in {
                "backoff_factor",
                "max_rate_limit_wait_seconds",
                "max_delay",
                "rate_limit_requests_per_second",
            }:
                parsed_float = parse_env_float(value, field_name=field_name)
                if field_name == "backoff_factor":
                    backoff_factor = parsed_float
                elif field_name == "max_rate_limit_wait_seconds":
                    max_rate_limit_wait_seconds = parsed_float
                elif field_name == "max_delay":
                    max_delay = parsed_float
                else:
                    rate_limit_requests_per_second = parsed_float
            elif field_name == "retryable_methods":
                retryable_methods = parse_env_str_tuple(value, field_name=field_name)
            else:
                parsed_bool = parse_env_bool(value, field_name=field_name)
                if field_name == "retry_on_rate_limit":
                    retry_on_rate_limit = parsed_bool
                elif field_name == "retry_on_server_error":
                    retry_on_server_error = parsed_bool
                elif field_name == "retry_on_transport_error":
                    retry_on_transport_error = parsed_bool
                else:
                    rate_limit_enabled = parsed_bool
        return cls(
            max_attempts=max_attempts,
            backoff_factor=backoff_factor,
            retryable_methods=retryable_methods,
            retry_on_rate_limit=retry_on_rate_limit,
            retry_on_server_error=retry_on_server_error,
            retry_on_transport_error=retry_on_transport_error,
            max_rate_limit_wait_seconds=max_rate_limit_wait_seconds,
            max_delay=max_delay,
            rate_limit_enabled=rate_limit_enabled,
            rate_limit_requests_per_second=rate_limit_requests_per_second,
            rate_limit_burst=rate_limit_burst,
        )

    def is_retryable_method(self, method: str, *, explicit_retry: bool = False) -> bool:
        """Определяет, можно ли повторять запрос указанного HTTP-метода."""

        return explicit_retry or method.upper() in self.retryable_methods

    def compute_backoff(self, attempt: int) -> float:
        """Возвращает backoff в секундах для номера попытки, начиная с единицы."""

        safe_attempt = max(attempt - 1, 0)
        base_delay = float(self.backoff_factor) * float(2**safe_attempt)
        capped_delay = min(base_delay, self.max_delay)
        return capped_delay * self.random_source.random()


@dataclass(slots=True, frozen=True)
class RetryDecision:
    """Решение retry-слоя по результату очередной попытки запроса."""

    should_retry: bool
    reason: RetryReason | None = None
    delay_seconds: float = 0.0


__all__ = ("RetryDecision", "RetryPolicy", "RetryReason")
