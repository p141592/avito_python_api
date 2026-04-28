"""Enum-значения раздела promotion."""

from __future__ import annotations

from enum import Enum


class PromotionStatus(str, Enum):
    """Статус promotion-объекта или операции."""

    UNKNOWN = "__unknown__"
    UPSTREAM_UNKNOWN = "unknown"
    AVAILABLE = "available"
    ACTIVE = "active"
    CREATED = "created"
    INITIALIZED = "initialized"
    WAITING = "waiting"
    IN_PROCESS = "in_process"
    PROCESSED = "processed"
    CANCELED = "canceled"
    ERROR = "error"
    REMOVED = "removed"
    AUTO = "auto"
    MANUAL = "manual"
    APPLIED = "applied"
    PARTIAL = "partial"
    FAILED = "failed"
    PREVIEW = "preview"


class PromotionOrderStatus(str, Enum):
    """Статус заявки на продвижение."""

    UNKNOWN = "__unknown__"
    UPSTREAM_UNKNOWN = "unknown"
    APPLIED = "applied"
    CREATED = "created"
    AUTO = "auto"
    MANUAL = "manual"
    PARTIAL = "partial"
    INITIALIZED = "initialized"
    WAITING = "waiting"
    IN_PROCESS = "in_process"
    PROCESSED = "processed"


class PromotionOrderServiceStatus(str, Enum):
    """Статус услуги внутри заявки на продвижение."""

    UNKNOWN = "__unknown__"
    UPSTREAM_UNKNOWN = "unknown"
    AVAILABLE = "available"
    ACTIVE = "active"
    ERROR = "error"
    CANCELED = "canceled"
    PROCESSED = "processed"


class TargetActionBudgetType(str, Enum):
    """Тип бюджета цены целевого действия."""

    UNKNOWN = "__unknown__"
    DAILY = "1d"
    WEEKLY = "7d"
    MONTHLY = "30d"


class TargetActionSelectedType(str, Enum):
    """Выбранный тип продвижения цены целевого действия."""

    UNKNOWN = "__unknown__"
    AUTO = "auto"
    MANUAL = "manual"


class CampaignType(str, Enum):
    """Тип автокампании."""

    UNKNOWN = "__unknown__"
    AUTOSTRATEGY = "AS"


__all__ = (
    "CampaignType",
    "PromotionOrderServiceStatus",
    "PromotionOrderStatus",
    "PromotionStatus",
    "TargetActionBudgetType",
    "TargetActionSelectedType",
)
