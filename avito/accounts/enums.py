"""Enum-значения раздела accounts."""

from __future__ import annotations

from enum import Enum


class OperationType(str, Enum):
    """Тип операции по аккаунту."""

    UNKNOWN = "__unknown__"
    PAYMENT = "payment"


class OperationStatus(str, Enum):
    """Статус операции по аккаунту."""

    UNKNOWN = "__unknown__"
    DONE = "done"


class AccountHierarchyRole(str, Enum):
    """Роль пользователя в иерархии аккаунтов."""

    UNKNOWN = "__unknown__"
    MANAGER = "manager"


class EmployeeItemStatus(str, Enum):
    """Статус объявления сотрудника."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"


__all__ = (
    "AccountHierarchyRole",
    "EmployeeItemStatus",
    "OperationStatus",
    "OperationType",
)
