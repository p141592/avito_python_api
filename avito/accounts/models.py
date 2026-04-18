"""Типизированные модели раздела accounts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core.serialization import SerializableModel, enable_module_serialization


@dataclass(slots=True, frozen=True)
class AccountProfile(SerializableModel):
    """Профиль авторизованного пользователя."""

    id: int | None
    name: str | None
    email: str | None
    phone: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AccountBalance:
    """Баланс кошелька пользователя."""

    user_id: int | None
    real: float | None
    bonus: float | None
    total: float | None
    currency: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class OperationRecord:
    """Операция по аккаунту."""

    id: str | None
    created_at: str | None
    amount: float | None
    operation_type: str | None
    status: str | None
    description: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class OperationsHistoryRequest:
    """Фильтр истории операций аккаунта."""

    date_from: str | None = None
    date_to: str | None = None
    limit: int | None = None
    offset: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует фильтр в JSON body."""

        return {
            key: value
            for key, value in {
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
                "limit": self.limit,
                "offset": self.offset,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class OperationsHistoryResult(SerializableModel):
    """История операций пользователя."""

    operations: list[OperationRecord]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AhUserStatus:
    """Статус пользователя в иерархии аккаунтов."""

    user_id: int | None
    is_active: bool | None
    role: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Employee:
    """Сотрудник иерархии аккаунтов."""

    employee_id: int | None
    user_id: int | None
    name: str | None
    phone: str | None
    email: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EmployeesResult:
    """Список сотрудников иерархии."""

    items: list[Employee]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CompanyPhone:
    """Телефон компании."""

    id: int | None
    phone: str | None
    comment: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CompanyPhonesResult:
    """Список телефонов компании."""

    items: list[CompanyPhone]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EmployeeItemLinkRequest:
    """Запрос на привязку объявлений к сотруднику."""

    employee_id: int
    item_ids: list[int]
    source_employee_id: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос привязки в JSON body."""

        return {
            key: value
            for key, value in {
                "employeeId": self.employee_id,
                "itemIds": self.item_ids,
                "sourceEmployeeId": self.source_employee_id,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class EmployeeItemsRequest:
    """Запрос списка объявлений сотрудника."""

    employee_id: int
    limit: int | None = None
    offset: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует фильтр объявлений сотрудника."""

        return {
            key: value
            for key, value in {
                "employeeId": self.employee_id,
                "limit": self.limit,
                "offset": self.offset,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class EmployeeItem:
    """Объявление сотрудника в иерархии."""

    item_id: int | None
    title: str | None
    status: str | None
    price: float | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EmployeeItemsResult:
    """Список объявлений сотрудника."""

    items: list[EmployeeItem]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ActionResult:
    """Результат мутационной операции accounts."""

    success: bool
    message: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


__all__ = (
    "AccountBalance",
    "AccountProfile",
    "ActionResult",
    "AhUserStatus",
    "CompanyPhone",
    "CompanyPhonesResult",
    "Employee",
    "EmployeeItem",
    "EmployeeItemLinkRequest",
    "EmployeeItemsRequest",
    "EmployeeItemsResult",
    "EmployeesResult",
    "OperationRecord",
    "OperationsHistoryRequest",
    "OperationsHistoryResult",
)

enable_module_serialization(globals())
