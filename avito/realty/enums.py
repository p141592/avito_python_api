"""Enum-значения раздела realty."""

from __future__ import annotations

from enum import Enum


class RealtyStatus(str, Enum):
    """Статус сущности realty."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    SUCCESS = "success"
    CANCELED = "canceled"
    PENDING = "pending"


class RealtyBookingStatus(str, Enum):
    """Статус бронирования недвижимости."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    CANCELED = "canceled"
    PENDING = "pending"


class RealtyOperationStatus(str, Enum):
    """Статус результата операции realty API."""

    UNKNOWN = "__unknown__"
    SUCCESS = "success"


__all__ = ("RealtyBookingStatus", "RealtyOperationStatus", "RealtyStatus")
