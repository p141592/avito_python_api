"""Устаревший модуль совместимости — импортируйте из `avito.config` напрямую."""

import warnings

from avito.config import AvitoSettings
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts

warnings.warn(
    "avito.settings устарел и будет удалён. Используйте `avito.config.AvitoSettings` напрямую.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ("ApiTimeouts", "AvitoSettings", "RetryPolicy")
