"""Enum-значения раздела jobs."""

from __future__ import annotations

from enum import Enum


class JobActionStatus(str, Enum):
    """Статус мутационной операции jobs."""

    UNKNOWN = "__unknown__"
    VIEWED = "viewed"
    INVITED = "invited"
    CREATED = "created"
    UPDATED = "updated"
    ARCHIVED = "archived"
    PROLONGATED = "prolongated"
    AUTO_RENEWAL_UPDATED = "auto-renewal-updated"


class ApplicationStatus(str, Enum):
    """Статус отклика."""

    UNKNOWN = "__unknown__"
    NEW = "new"


class VacancyStatus(str, Enum):
    """Статус вакансии."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    CREATED = "created"
    UPDATED = "updated"


__all__ = ("ApplicationStatus", "JobActionStatus", "VacancyStatus")
