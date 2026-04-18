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


@dataclass(slots=True)
class AccountsClient:
    """Выполняет HTTP-операции по разделу информации о пользователе."""

    transport: Transport

    def get_self(self) -> AccountProfile:
        """Получает профиль авторизованного пользователя."""

        payload = self.transport.request_json(
            "GET",
            "/core/v1/accounts/self",
            context=RequestContext("accounts.get_self"),
        )
        return map_account_profile(payload)

    def get_balance(self, *, user_id: int) -> AccountBalance:
        """Получает баланс аккаунта."""

        payload = self.transport.request_json(
            "GET",
            f"/core/v1/accounts/{user_id}/balance/",
            context=RequestContext("accounts.get_balance"),
        )
        return map_account_balance(payload)

    def get_operations_history(self, request: OperationsHistoryRequest) -> OperationsHistoryResult:
        """Получает историю операций пользователя."""

        payload = self.transport.request_json(
            "POST",
            "/core/v1/accounts/operations_history/",
            context=RequestContext("accounts.get_operations_history", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_operations_history(payload)


@dataclass(slots=True)
class HierarchyClient:
    """Выполняет HTTP-операции по иерархии аккаунтов."""

    transport: Transport

    def get_status(self) -> AhUserStatus:
        """Получает статус пользователя в ИА."""

        payload = self.transport.request_json(
            "GET",
            "/checkAhUserV1",
            context=RequestContext("accounts.hierarchy.get_status"),
        )
        return map_ah_user_status(payload)

    def list_employees(self) -> EmployeesResult:
        """Получает список сотрудников иерархии."""

        payload = self.transport.request_json(
            "GET",
            "/getEmployeesV1",
            context=RequestContext("accounts.hierarchy.list_employees"),
        )
        return map_employees(payload)

    def list_company_phones(self) -> CompanyPhonesResult:
        """Получает список телефонов компании."""

        payload = self.transport.request_json(
            "GET",
            "/listCompanyPhonesV1",
            context=RequestContext("accounts.hierarchy.list_company_phones"),
        )
        return map_company_phones(payload)

    def link_items(self, request: EmployeeItemLinkRequest) -> ActionResult:
        """Прикрепляет объявления к сотруднику."""

        payload = self.transport.request_json(
            "POST",
            "/linkItemsV1",
            context=RequestContext("accounts.hierarchy.link_items", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action_result(payload)

    def list_items_by_employee(self, request: EmployeeItemsRequest) -> EmployeeItemsResult:
        """Получает список объявлений по сотруднику."""

        payload = self.transport.request_json(
            "POST",
            "/listItemsByEmployeeIdV1",
            context=RequestContext("accounts.hierarchy.list_items_by_employee", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_employee_items(payload)


__all__ = ("AccountsClient", "HierarchyClient")
