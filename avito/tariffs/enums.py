"""Enum-значения раздела tariffs."""

from __future__ import annotations

from enum import Enum


class TariffLevel(str, Enum):
    """Уровень тарифного контракта."""

    UNKNOWN = "__unknown__"
    MAX = "Тариф Максимальный"
    BASE = "Тариф Базовый"


__all__ = ("TariffLevel",)
