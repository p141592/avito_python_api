"""Совместимые импорты конфигурации SDK."""

from avito.config import AvitoSettings
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts

__all__ = ("ApiTimeouts", "AvitoSettings", "RetryPolicy")
