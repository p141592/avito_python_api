"""Enum-значения раздела ads."""

from __future__ import annotations

from enum import Enum


class ListingStatus(str, Enum):
    """Статус объявления."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    REMOVED = "removed"
    OLD = "old"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    NOT_FOUND = "not_found"
    ANOTHER_USER = "another_user"


class AdsActionStatus(str, Enum):
    """Статус мутационной операции ads."""

    UNKNOWN = "__unknown__"
    APPLIED = "applied"
    UPDATED = "updated"


class AutoloadFieldType(str, Enum):
    """Тип поля автозагрузки."""

    UNKNOWN = "__unknown__"
    STRING = "string"


class AutoloadReportStatus(str, Enum):
    """Статус отчета автозагрузки."""

    UNKNOWN = "__unknown__"
    DONE = "done"


__all__ = (
    "AdsActionStatus",
    "AutoloadFieldType",
    "AutoloadReportStatus",
    "ListingStatus",
)
