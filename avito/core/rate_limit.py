"""Локальный rate limiter transport-слоя."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping

from avito.core.retries import RetryPolicy


class RateLimiter:
    """Token bucket для превентивного ограничения частоты запросов."""

    def __init__(
        self,
        policy: RetryPolicy,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._enabled = policy.rate_limit_enabled
        self._rate = max(policy.rate_limit_requests_per_second, 0.0)
        self._capacity = max(policy.rate_limit_burst, 0)
        self._tokens = float(self._capacity)
        self._updated_at = clock()
        self._blocked_until = 0.0
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()

    def acquire(self) -> float:
        """Ждёт, пока запрос можно безопасно отправить, и возвращает задержку."""

        if not self._enabled or self._rate <= 0.0 or self._capacity <= 0:
            return 0.0

        total_delay = 0.0
        while True:
            delay = self._reserve_or_delay()
            if delay <= 0.0:
                return total_delay
            self._sleep(delay)
            total_delay += delay

    def observe_response(self, *, headers: Mapping[str, str]) -> None:
        """Обновляет локальный cooldown по rate-limit headers upstream API."""

        if not self._enabled or self._rate <= 0.0:
            return

        remaining = _get_header(headers, "x-ratelimit-remaining")
        if remaining is None:
            return
        try:
            remaining_count = int(remaining)
        except ValueError:
            return
        if remaining_count <= 0:
            self._block_for(1.0 / self._rate)

    def _reserve_or_delay(self) -> float:
        with self._lock:
            now = self._clock()
            self._refill(now)
            blocked_delay = max(self._blocked_until - now, 0.0)
            if blocked_delay > 0.0:
                return blocked_delay
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return 0.0
            return (1.0 - self._tokens) / self._rate

    def _refill(self, now: float) -> None:
        elapsed = max(now - self._updated_at, 0.0)
        if elapsed > 0.0:
            self._tokens = min(float(self._capacity), self._tokens + elapsed * self._rate)
            self._updated_at = now

    def _block_for(self, delay: float) -> None:
        if delay <= 0.0:
            return
        with self._lock:
            self._blocked_until = max(self._blocked_until, self._clock() + delay)
            self._tokens = min(self._tokens, 0.0)


def _get_header(headers: Mapping[str, str], name: str) -> str | None:
    value = headers.get(name)
    if value is not None:
        return value
    lowered_name = name.lower()
    for key, item in headers.items():
        if key.lower() == lowered_name:
            return item
    return None


__all__ = ("RateLimiter",)
