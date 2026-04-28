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
    INTEGER = "integer"
    FLOAT = "float"
    INPUT = "input"
    SELECT = "select"
    CHECKBOX = "checkbox"


class AutoloadReportStatus(str, Enum):
    """Статус отчета автозагрузки."""

    UNKNOWN = "__unknown__"
    DONE = "done"
    PROCESSING = "processing"
    SUCCESS = "success"
    SUCCESS_WARNING = "success_warning"
    ERROR = "error"
    # Legacy item statuses kept for backward compatibility.
    PROBLEM = "problem"
    NOT_PUBLISH = "not_publish"
    WILL_PUBLISH_LATER = "will_publish_later"
    DUPLICATE = "duplicate"
    WITHOUT_ID = "without_id"
    DELETED = "deleted"
    UPSTREAM_UNKNOWN = "unknown"


class AutoloadItemStatus(str, Enum):
    """Статус объявления в отчете автозагрузки."""

    UNKNOWN = "__unknown__"
    SUCCESS = "success"
    PROBLEM = "problem"
    ERROR = "error"
    NOT_PUBLISH = "not_publish"
    WILL_PUBLISH_LATER = "will_publish_later"
    DUPLICATE = "duplicate"
    WITHOUT_ID = "without_id"
    DELETED = "deleted"
    UPSTREAM_UNKNOWN = "unknown"


class AutoloadItemStatusDetail(str, Enum):
    """Подробный статус объявления в отчете автозагрузки."""

    UNKNOWN = "__unknown__"
    SUCCESS_ADDED = "success_added"
    SUCCESS_ACTIVATED = "success_activated"
    SUCCESS_ACTIVATED_UPDATED = "success_activated_updated"
    SUCCESS_UPDATED = "success_updated"
    SUCCESS_SKIPPED = "success_skipped"
    PROBLEM_OBSOLETE = "problem_obsolete"
    PROBLEM_PARAMS_CRITICAL = "problem_params_critical"
    PROBLEM_PARAMS = "problem_params"
    PROBLEM_PHONE = "problem_phone"
    PROBLEM_IMAGES = "problem_images"
    PROBLEM_VAS = "problem_vas"
    PROBLEM_OTHER = "problem_other"
    PROBLEM_SEVERAL = "problem_several"
    ERROR_FEE = "error_fee"
    ERROR_PARAMS = "error_params"
    ERROR_PHONE = "error_phone"
    ERROR_REJECTED = "error_rejected"
    ERROR_BLOCKED = "error_blocked"
    ERROR_DELETED = "error_deleted"
    ERROR_OTHER = "error_other"
    ERROR_SEVERAL = "error_several"
    STOPPED_END_DATE_COMPLETE = "stopped_end_date_complete"
    STOPPED_END_DATE_ERROR = "stopped_end_date_error"
    DATE_IN_FUTURE = "date_in_future"
    PUBLISH_LATER = "publish_later"
    LINKER = "linker"
    REMOVED_COMPLETE = "removed_complete"
    REMOVED_ERROR = "removed_error"
    NEED_SYNC = "need_sync"
    DUPLICATE = "duplicate"
    WITHOUT_ID = "without_id"


class AutoloadAvitoStatus(str, Enum):
    """Статус объявления на Авито из отчета автозагрузки."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"
    OLD = "old"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    REMOVED = "removed"


__all__ = (
    "AdsActionStatus",
    "AutoloadAvitoStatus",
    "AutoloadFieldType",
    "AutoloadItemStatus",
    "AutoloadItemStatusDetail",
    "AutoloadReportStatus",
    "ListingStatus",
)
