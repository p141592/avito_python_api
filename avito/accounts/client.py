"""Внутренние section clients для раздела accounts."""

from __future__ import annotations

from dataclasses import dataclass

from avito.accounts.mappers import (
    map_account_balance,
    map_account_profile,
    map_action_result,
    map_ah_user_status,
    map_company_phones,
    map_employee_items,
    map_employees,
    map_operations_history,
)
from avito.accounts.models import (
    AccountBalance,
    AccountProfile,
    ActionResult,
    AhUserStatus,
    CompanyPhonesResult,
    EmployeeItemLinkRequest,
    EmployeeItemsRequest,
    EmployeeItemsResult,
    EmployeesResult,
    OperationsHistoryRequest,
    OperationsHistoryResult,
)
from avito.core import RequestContext, Transport
from avito.core.mapping import request_public_model


@dataclass(slots=True)
class AccountsClient:
    """Выполняет HTTP-операции по разделу информации о пользователе."""

    transport: Transport

    def get_self(self) -> AccountProfile:
        """Получает профиль авторизованного пользователя."""

        return request_public_model(
            self.transport,
            "GET",
            "/core/v1/accounts/self",
            context=RequestContext("accounts.get_self"),
            mapper=map_account_profile,
        )

    def get_balance(self, *, user_id: int) -> AccountBalance:
        """Получает баланс аккаунта."""

        return request_public_model(
            self.transport,
            "GET",
            f"/core/v1/accounts/{user_id}/balance/",
            context=RequestContext("accounts.get_balance"),
            mapper=map_account_balance,
        )

    def get_operations_history(self, request: OperationsHistoryRequest) -> OperationsHistoryResult:
        """Получает историю операций пользователя."""

        return request_public_model(
            self.transport,
            "POST",
            "/core/v1/accounts/operations_history/",
            context=RequestContext("accounts.get_operations_history", allow_retry=True),
            mapper=map_operations_history,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class HierarchyClient:
    """Выполняет HTTP-операции по иерархии аккаунтов."""

    transport: Transport

    def get_status(self) -> AhUserStatus:
        """Получает статус пользователя в ИА."""

        return request_public_model(
            self.transport,
            "GET",
            "/checkAhUserV1",
            context=RequestContext("accounts.hierarchy.get_status"),
            mapper=map_ah_user_status,
        )

    def list_employees(self) -> EmployeesResult:
        """Получает список сотрудников иерархии."""

        return request_public_model(
            self.transport,
            "GET",
            "/getEmployeesV1",
            context=RequestContext("accounts.hierarchy.list_employees"),
            mapper=map_employees,
        )

    def list_company_phones(self) -> CompanyPhonesResult:
        """Получает список телефонов компании."""

        return request_public_model(
            self.transport,
            "GET",
            "/listCompanyPhonesV1",
            context=RequestContext("accounts.hierarchy.list_company_phones"),
            mapper=map_company_phones,
        )

    def link_items(self, request: EmployeeItemLinkRequest) -> ActionResult:
        """Прикрепляет объявления к сотруднику."""

        return request_public_model(
            self.transport,
            "POST",
            "/linkItemsV1",
            context=RequestContext("accounts.hierarchy.link_items", allow_retry=True),
            mapper=map_action_result,
            json_body=request.to_payload(),
        )

    def list_items_by_employee(self, request: EmployeeItemsRequest) -> EmployeeItemsResult:
        """Получает список объявлений по сотруднику."""

        return request_public_model(
            self.transport,
            "POST",
            "/listItemsByEmployeeIdV1",
            context=RequestContext("accounts.hierarchy.list_items_by_employee", allow_retry=True),
            mapper=map_employee_items,
            json_body=request.to_payload(),
        )


__all__ = ("AccountsClient", "HierarchyClient")
