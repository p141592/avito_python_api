"""Enum-значения раздела orders."""

from __future__ import annotations

from enum import Enum


class OrderStatus(str, Enum):
    """Статус заказа."""

    UNKNOWN = "__unknown__"
    ON_CONFIRMATION = "on_confirmation"
    READY_TO_SHIP = "ready_to_ship"
    IN_TRANSIT = "in_transit"
    CANCELED = "canceled"
    DELIVERED = "delivered"
    ON_RETURN = "on_return"
    IN_DISPUTE = "in_dispute"
    CLOSED = "closed"
    # Legacy operation statuses kept for backward compatibility.
    NEW = "new"
    MARKED = "marked"
    CONFIRMED = "confirmed"
    CODE_VALID = "code-valid"
    RANGE_SET = "range-set"
    TRACKING_SET = "tracking-set"
    RETURN_ACCEPTED = "return-accepted"


class OrderActionStatus(str, Enum):
    """Статус результата операции над заказом."""

    UNKNOWN = "__unknown__"
    MARKED = "marked"
    CONFIRMED = "confirmed"
    CODE_VALID = "code-valid"
    RANGE_SET = "range-set"
    TRACKING_SET = "tracking-set"
    RETURN_ACCEPTED = "return-accepted"
    SUCCESS = "success"
    FAIL = "fail"
    EXPIRED = "expired"
    ATTEMPTS = "attempts"


class LabelTaskStatus(str, Enum):
    """Статус задачи генерации этикеток."""

    UNKNOWN = "__unknown__"
    CREATED = "created"


class DeliveryOperationStatus(str, Enum):
    """Статус результата операции delivery API."""

    UNKNOWN = "__unknown__"
    ANNOUNCEMENT_CREATED = "announcement-created"
    PARCEL_CREATED = "parcel-created"
    ANNOUNCEMENT_CANCELLED = "announcement-cancelled"
    CALLBACK_ACCEPTED = "callback-accepted"
    PARCELS_UPDATED = "parcels-updated"
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    FORBIDDEN = "forbidden"
    OK = "OK"
    OK_LOWER = "ok"


class DeliveryTaskState(str, Enum):
    """Статус фоновой задачи delivery API."""

    UNKNOWN = "__unknown__"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"
    DECLINED = "declined"
    DONE = "done"


class DeliveryStatus(str, Enum):
    """Legacy-статус операции или задачи delivery API."""

    UNKNOWN = "__unknown__"
    ANNOUNCEMENT_CREATED = "announcement-created"
    PARCEL_CREATED = "parcel-created"
    ANNOUNCEMENT_CANCELLED = "announcement-cancelled"
    CALLBACK_ACCEPTED = "callback-accepted"
    PARCELS_UPDATED = "parcels-updated"
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    FORBIDDEN = "forbidden"
    OK = "OK"
    OK_LOWER = "ok"
    PROCESSING = "processing"
    PENDING_APPROVAL = "pending_approval"
    DECLINED = "declined"
    DONE = "done"


class TrackingAvitoStatus(str, Enum):
    """Статус Avito для sandbox tracking-события."""

    UNKNOWN = "__unknown__"
    CONFIRMED = "CONFIRMED"
    IN_TRANSIT = "IN_TRANSIT"
    ON_DELIVERY = "ON_DELIVERY"
    DELIVERED = "DELIVERED"
    IN_TRANSIT_RETURN = "IN_TRANSIT_RETURN"
    ON_DELIVERY_RETURN = "ON_DELIVERY_RETURN"
    RETURNED = "RETURNED"
    LOST = "LOST"
    DESTROYED = "DESTROYED"


class TrackingAvitoEventType(str, Enum):
    """Тип Avito-события для sandbox tracking."""

    UNKNOWN = "__unknown__"


__all__ = (
    "DeliveryOperationStatus",
    "DeliveryStatus",
    "DeliveryTaskState",
    "LabelTaskStatus",
    "OrderActionStatus",
    "OrderStatus",
    "TrackingAvitoEventType",
    "TrackingAvitoStatus",
)
