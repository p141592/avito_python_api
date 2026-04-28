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
    ACTIVATED = "activated"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    CLOSED = "closed"
    EXPIRED = "expired"
    REJECTED = "rejected"
    UNBLOCKED = "unblocked"


class VacancyModerationStatus(str, Enum):
    """Статус модерации вакансии."""

    UNKNOWN = "__unknown__"
    IN_PROGRESS = "in_progress"
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class JobEnrichmentStatus(str, Enum):
    """Статус обогащения параметров вакансии."""

    UNKNOWN = "__unknown__"
    IN_PROGRESS = "in_progress"
    NOT_COMPLETED = "not_completed"
    COMPLETED_NO_CRITERIA = "completed_no_criteria"
    COMPLETED_MATCHED = "completed_matched"
    COMPLETED_MISMATCHED = "completed_mismatched"


class JobMatchingStatus(str, Enum):
    """Статус сопоставления критерия вакансии."""

    UNKNOWN = "__unknown__"
    NO_CRITERIA = "no_criteria"
    MATCHED = "matched"
    MISMATCHED = "mismatched"


__all__ = (
    "ApplicationStatus",
    "JobActionStatus",
    "JobEnrichmentStatus",
    "JobMatchingStatus",
    "VacancyModerationStatus",
    "VacancyStatus",
)
