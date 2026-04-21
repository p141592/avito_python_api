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
from avito.core import JsonPage, PaginatedList, Paginator, RequestContext, Transport
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

    def get_operations_history(self, request: OperationsHistoryRequest) -> PaginatedList[OperationRecord]:
        """Получает историю операций пользователя."""

        page_size = request.limit or 25
        base_offset = request.offset or 0

        def fetch_page(page: int | None, _cursor: str | None) -> JsonPage[OperationRecord]:
            current_page = page or 1
            current_offset = base_offset + (current_page - 1) * page_size
            paged_request = OperationsHistoryRequest(
                date_from=request.date_from,
                date_to=request.date_to,
                limit=page_size,
                offset=current_offset,
            )
            result = request_public_model(
                self.transport,
                "POST",
                "/core/v1/accounts/operations_history/",
                context=RequestContext("accounts.get_operations_history", allow_retry=True),
                mapper=map_operations_history,
                json_body=paged_request.to_payload(),
            )
            return JsonPage(
                items=result.operations,
                total=result.total,
                page=current_page,
                per_page=page_size,
            )

        return Paginator(fetch_page).as_list(first_page=fetch_page(1, None))


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

    def link_items(self, request: EmployeeItemLinkRequest) -> AccountActionResult:
        """Прикрепляет объявления к сотруднику."""

        return request_public_model(
            self.transport,
            "POST",
            "/linkItemsV1",
            context=RequestContext("accounts.hierarchy.link_items", allow_retry=True),
            mapper=map_action_result,
            json_body=request.to_payload(),
        )

    def list_items_by_employee(self, request: EmployeeItemsRequest) -> PaginatedList[EmployeeItem]:
        """Получает список объявлений по сотруднику."""

        page_size = request.limit or 25

        def fetch_page(page: int | None, _cursor: str | None) -> JsonPage[EmployeeItem]:
            current_page = page or 1
            current_offset = (request.offset or 0) + (current_page - 1) * page_size
            paged_request = EmployeeItemsRequest(
                employee_id=request.employee_id,
                limit=page_size,
                offset=current_offset,
            )
            result = request_public_model(
                self.transport,
                "POST",
                "/listItemsByEmployeeIdV1",
                context=RequestContext(
                    "accounts.hierarchy.list_items_by_employee", allow_retry=True
                ),
                mapper=map_employee_items,
                json_body=paged_request.to_payload(),
            )
            return JsonPage(
                items=result.items,
                total=result.total,
                page=current_page,
                per_page=page_size,
            )

        return Paginator(fetch_page).as_list(first_page=fetch_page(1, None))


__all__ = ("AccountsClient", "HierarchyClient")
