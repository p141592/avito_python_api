"""Enum-значения раздела orders."""

from __future__ import annotations

from enum import Enum


class OrderStatus(str, Enum):
    """Статус заказа или операции над заказом."""

    UNKNOWN = "__unknown__"
    NEW = "new"
    MARKED = "marked"
    CONFIRMED = "confirmed"
    CODE_VALID = "code-valid"
    RANGE_SET = "range-set"
    TRACKING_SET = "tracking-set"
    RETURN_ACCEPTED = "return-accepted"


class LabelTaskStatus(str, Enum):
    """Статус задачи генерации этикеток."""

    UNKNOWN = "__unknown__"
    CREATED = "created"


class DeliveryStatus(str, Enum):
    """Статус операции или задачи delivery API."""

    UNKNOWN = "__unknown__"
    ANNOUNCEMENT_CREATED = "announcement-created"
    PARCEL_CREATED = "parcel-created"
    ANNOUNCEMENT_CANCELLED = "announcement-cancelled"
    CALLBACK_ACCEPTED = "callback-accepted"
    PARCELS_UPDATED = "parcels-updated"
    DONE = "done"


class TrackingAvitoStatus(str, Enum):
    """Статус Avito для sandbox tracking-события."""

    UNKNOWN = "__unknown__"


class TrackingAvitoEventType(str, Enum):
    """Тип Avito-события для sandbox tracking."""

    UNKNOWN = "__unknown__"


__all__ = (
    "DeliveryStatus",
    "LabelTaskStatus",
    "OrderStatus",
    "TrackingAvitoEventType",
    "TrackingAvitoStatus",
)
