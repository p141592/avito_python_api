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
from avito.core import PaginatedList
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass(slots=True, frozen=True)
class Account(DomainObject):
    """Доменный объект операций аккаунта."""

    __swagger_domain__ = "accounts"
    __sdk_factory__ = "account"
    __sdk_factory_args__ = {"user_id": "path.user_id"}

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/core/v1/accounts/self",
        spec="Информацияопользователе.json",
        operation_id="getUserInfoSelf",
    )
    def get_self(self) -> AccountProfile:
        """Получает профиль авторизованного пользователя.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AccountsClient(self.transport).get_self()

    @swagger_operation(
        "GET",
        "/core/v1/accounts/{user_id}/balance",
        spec="Информацияопользователе.json",
        operation_id="getUserBalance",
    )
    def get_balance(self, user_id: int | None = None) -> AccountBalance:
        """Получает баланс пользователя.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_user_id = self._resolve_user_id(user_id or self.user_id)
        return AccountsClient(self.transport).get_balance(user_id=resolved_user_id)

    @swagger_operation(
        "POST",
        "/core/v1/accounts/operations_history",
        spec="Информацияопользователе.json",
        operation_id="postOperationsHistory",
    )
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

    __swagger_domain__ = "accounts"
    __sdk_factory__ = "account_hierarchy"
    __sdk_factory_args__ = {"user_id": "path.user_id"}

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/checkAhUserV1",
        spec="ИерархияАккаунтов.json",
        operation_id="checkAhUserV1",
    )
    def get_status(self) -> AhUserStatus:
        """Получает статус пользователя в ИА.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).get_status()

    @swagger_operation(
        "GET",
        "/getEmployeesV1",
        spec="ИерархияАккаунтов.json",
        operation_id="getEmployeesV1",
    )
    def list_employees(self) -> EmployeesResult:
        """Получает список сотрудников иерархии.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).list_employees()

    @swagger_operation(
        "GET",
        "/listCompanyPhonesV1",
        spec="ИерархияАккаунтов.json",
        operation_id="listCompanyPhonesV1",
    )
    def list_company_phones(self) -> CompanyPhonesResult:
        """Получает список телефонов компании.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return HierarchyClient(self.transport).list_company_phones()

    @swagger_operation(
        "POST",
        "/linkItemsV1",
        spec="ИерархияАккаунтов.json",
        operation_id="linkItemsV1",
        method_args={"employee_id": "body.employee_id", "item_ids": "body.item_ids"},
    )
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

    @swagger_operation(
        "POST",
        "/listItemsByEmployeeIdV1",
        spec="ИерархияАккаунтов.json",
        operation_id="listItemsByEmployeeIdV1",
        method_args={"employee_id": "body.employee_id"},
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
