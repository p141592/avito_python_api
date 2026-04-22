"""Enum-значения раздела realty."""

from __future__ import annotations

from enum import Enum


class RealtyStatus(str, Enum):
    """Статус сущности realty."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    SUCCESS = "success"


__all__ = ("RealtyStatus",)
