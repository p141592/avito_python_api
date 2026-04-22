"""Enum-значения раздела promotion."""

from __future__ import annotations

from enum import Enum


class PromotionStatus(str, Enum):
    """Статус promotion-объекта или операции."""

    UNKNOWN = "__unknown__"
    AVAILABLE = "available"
    CREATED = "created"
    PROCESSED = "processed"
    REMOVED = "removed"
    AUTO = "auto"
    MANUAL = "manual"
    APPLIED = "applied"
    PARTIAL = "partial"
    FAILED = "failed"
    PREVIEW = "preview"


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
    "PromotionStatus",
    "TargetActionBudgetType",
    "TargetActionSelectedType",
)
