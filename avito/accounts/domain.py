"""Доменные объекты пакета accounts."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from avito.accounts.client import AccountsClient, HierarchyClient
from avito.accounts.models import (
    AccountActionResult,
    AccountBalance,
    AccountProfile,
    AhUserStatus,
    CompanyPhonesResult,
    EmployeeItem,
    EmployeesResult,
    OperationRecord,
)
from avito.core import PaginatedList, ValidationError
from avito.core.domain import DomainObject


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass(slots=True, frozen=True)
class Account(DomainObject):
    """Доменный объект операций аккаунта."""

    user_id: int | str | None = None

    def get_self(self) -> AccountProfile:
        """Получает профиль авторизованного пользователя.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AccountsClient(self.transport).get_self()

    def get_balance(self, user_id: int | None = None) -> AccountBalance:
        """Получает баланс пользователя.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_user_id = user_id or (int(self.user_id) if self.user_id is not None else None)
        if resolved_user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return AccountsClient(self.transport).get_balance(user_id=resolved_user_id)

    def get_operations_history(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[OperationRecord]:
        """Получает историю операций пользователя.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AccountsClient(self.transport).get_operations_history(
            date_from=_serialize_datetime(date_from),
            date_to=_serialize_datetime(date_to),
            limit=limit,
            offset=offset,
        )


@dataclass(slots=True, frozen=True)
class AccountHierarchy(DomainObject):
    """Доменный объект иерархии аккаунтов."""

    user_id: int | str | None = None

    def get_status(self) -> AhUserStatus:
        """Получает статус пользователя в ИА.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).get_status()

    def list_employees(self) -> EmployeesResult:
        """Получает список сотрудников иерархии.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).list_employees()

    def list_company_phones(self) -> CompanyPhonesResult:
        """Получает список телефонов компании.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).list_company_phones()

    def link_items(
        self,
        *,
        employee_id: int,
        item_ids: Sequence[int],
        source_employee_id: int | None = None,
        idempotency_key: str | None = None,
    ) -> AccountActionResult:
        """Прикрепляет объявления к сотруднику.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).link_items(
            employee_id=employee_id,
            item_ids=list(item_ids),
            source_employee_id=source_employee_id,
            idempotency_key=idempotency_key,
        )

    def list_items_by_employee(
        self,
        *,
        employee_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[EmployeeItem]:
        """Получает список объявлений сотрудника.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).list_items_by_employee(
            employee_id=employee_id,
            limit=limit,
            offset=offset,
        )


__all__ = ("Account", "AccountHierarchy")
