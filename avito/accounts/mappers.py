"""Мапперы JSON -> dataclass для пакета accounts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.accounts.models import (
    AccountBalance,
    AccountProfile,
    ActionResult,
    AhUserStatus,
    CompanyPhone,
    CompanyPhonesResult,
    Employee,
    EmployeeItem,
    EmployeeItemsResult,
    EmployeesResult,
    OperationRecord,
    OperationsHistoryResult,
)
from avito.core.exceptions import ResponseMappingError

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _as_list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _as_str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _as_int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _as_float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _as_bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_account_profile(payload: object) -> AccountProfile:
    """Преобразует профиль аккаунта в dataclass."""

    data = _expect_mapping(payload)
    return AccountProfile(
        id=_as_int(data, "id", "user_id"),
        name=_as_str(data, "name", "title"),
        email=_as_str(data, "email"),
        phone=_as_str(data, "phone"),
        raw_payload=data,
    )


def map_account_balance(payload: object) -> AccountBalance:
    """Преобразует ответ баланса в dataclass."""

    data = _expect_mapping(payload)
    wallet = data.get("balance")
    wallet_data = wallet if isinstance(wallet, Mapping) else data
    wallet_data = cast(Payload, wallet_data)
    real = _as_float(wallet_data, "real", "amount", "balance")
    bonus = _as_float(wallet_data, "bonus")
    total = _as_float(wallet_data, "total") or (
        real + bonus if real is not None and bonus is not None else real
    )
    return AccountBalance(
        user_id=_as_int(data, "user_id", "userId", "id"),
        real=real,
        bonus=bonus,
        total=total,
        currency=_as_str(wallet_data, "currency"),
        raw_payload=data,
    )


def map_operations_history(payload: object) -> OperationsHistoryResult:
    """Преобразует историю операций в dataclass."""

    data = _expect_mapping(payload)
    operations = [
        OperationRecord(
            id=_as_str(item, "id", "operation_id"),
            created_at=_as_str(item, "created_at", "createdAt", "date"),
            amount=_as_float(item, "amount", "price", "sum"),
            operation_type=_as_str(item, "type", "operation_type", "operationType"),
            status=_as_str(item, "status"),
            description=_as_str(item, "description", "title"),
            raw_payload=item,
        )
        for item in _as_list(data, "operations", "items", "result")
    ]
    return OperationsHistoryResult(
        operations=operations,
        total=_as_int(data, "total", "count"),
        raw_payload=data,
    )


def map_ah_user_status(payload: object) -> AhUserStatus:
    """Преобразует статус пользователя в ИА."""

    data = _expect_mapping(payload)
    return AhUserStatus(
        user_id=_as_int(data, "user_id", "userId", "id"),
        is_active=_as_bool(data, "is_active", "isActive", "active"),
        role=_as_str(data, "role", "status"),
        raw_payload=data,
    )


def map_employees(payload: object) -> EmployeesResult:
    """Преобразует список сотрудников."""

    data = _expect_mapping(payload)
    items = [
        Employee(
            employee_id=_as_int(item, "employee_id", "employeeId", "id"),
            user_id=_as_int(item, "user_id", "userId"),
            name=_as_str(item, "name", "title"),
            phone=_as_str(item, "phone"),
            email=_as_str(item, "email"),
            raw_payload=item,
        )
        for item in _as_list(data, "employees", "items", "result")
    ]
    return EmployeesResult(items=items, total=_as_int(data, "total", "count"), raw_payload=data)


def map_company_phones(payload: object) -> CompanyPhonesResult:
    """Преобразует список телефонов компании."""

    data = _expect_mapping(payload)
    items = [
        CompanyPhone(
            id=_as_int(item, "id", "phone_id", "phoneId"),
            phone=_as_str(item, "phone", "value"),
            comment=_as_str(item, "comment", "description"),
            raw_payload=item,
        )
        for item in _as_list(data, "phones", "items", "result")
    ]
    return CompanyPhonesResult(items=items, raw_payload=data)


def map_employee_items(payload: object) -> EmployeeItemsResult:
    """Преобразует список объявлений сотрудника."""

    data = _expect_mapping(payload)
    items = [
        EmployeeItem(
            item_id=_as_int(item, "item_id", "itemId", "id"),
            title=_as_str(item, "title"),
            status=_as_str(item, "status"),
            price=_as_float(item, "price"),
            raw_payload=item,
        )
        for item in _as_list(data, "items", "result")
    ]
    return EmployeeItemsResult(items=items, total=_as_int(data, "total", "count"), raw_payload=data)


def map_action_result(payload: object) -> ActionResult:
    """Преобразует ответ мутационной операции в dataclass."""

    if isinstance(payload, Mapping):
        data = cast(Payload, payload)
        success = bool(data.get("success", True))
        message = _as_str(data, "message", "status")
        return ActionResult(success=success, message=message, raw_payload=data)
    return ActionResult(success=True, raw_payload={})


__all__ = (
    "map_account_balance",
    "map_account_profile",
    "map_action_result",
    "map_ah_user_status",
    "map_company_phones",
    "map_employee_items",
    "map_employees",
    "map_operations_history",
)
