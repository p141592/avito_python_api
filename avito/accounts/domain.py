"""Доменные объекты пакета accounts."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.accounts.client import AccountsClient, HierarchyClient
from avito.accounts.models import (
    AccountActionResult,
    AccountBalance,
    AccountProfile,
    AhUserStatus,
    CompanyPhonesResult,
    EmployeeItem,
    EmployeeItemLinkRequest,
    EmployeeItemsRequest,
    EmployeesResult,
    OperationRecord,
    OperationsHistoryRequest,
)
from avito.core import PaginatedList, ValidationError
from avito.core.domain import DomainObject


@dataclass(slots=True, frozen=True)
class Account(DomainObject):
    """Доменный объект операций аккаунта."""

    user_id: int | str | None = None

    def get_self(self) -> AccountProfile:
        """Получает профиль авторизованного пользователя."""

        return AccountsClient(self.transport).get_self()

    def get_balance(self, user_id: int | None = None) -> AccountBalance:
        """Получает баланс пользователя."""

        resolved_user_id = user_id or (int(self.user_id) if self.user_id is not None else None)
        if resolved_user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return AccountsClient(self.transport).get_balance(user_id=resolved_user_id)

    def get_operations_history(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[OperationRecord]:
        """Получает историю операций пользователя."""

        return AccountsClient(self.transport).get_operations_history(
            OperationsHistoryRequest(
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        )


@dataclass(slots=True, frozen=True)
class AccountHierarchy(DomainObject):
    """Доменный объект иерархии аккаунтов."""

    user_id: int | str | None = None

    def get_status(self) -> AhUserStatus:
        """Получает статус пользователя в ИА."""

        return HierarchyClient(self.transport).get_status()

    def list_employees(self) -> EmployeesResult:
        """Получает список сотрудников иерархии."""

        return HierarchyClient(self.transport).list_employees()

    def list_company_phones(self) -> CompanyPhonesResult:
        """Получает список телефонов компании."""

        return HierarchyClient(self.transport).list_company_phones()

    def link_items(
        self,
        *,
        employee_id: int,
        item_ids: Sequence[int],
        source_employee_id: int | None = None,
    ) -> AccountActionResult:
        """Прикрепляет объявления к сотруднику."""

        return HierarchyClient(self.transport).link_items(
            EmployeeItemLinkRequest(
                employee_id=employee_id,
                item_ids=list(item_ids),
                source_employee_id=source_employee_id,
            )
        )

    def list_items_by_employee(
        self,
        *,
        employee_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[EmployeeItem]:
        """Получает список объявлений сотрудника."""

        return HierarchyClient(self.transport).list_items_by_employee(
            EmployeeItemsRequest(employee_id=employee_id, limit=limit, offset=offset)
        )


__all__ = ("Account", "AccountHierarchy")
