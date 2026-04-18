"""Мапперы JSON -> dataclass для пакета orders."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.orders.models import (
    CourierRange,
    CourierRangesResult,
    DeliveryEntityResult,
    DeliverySortingCenter,
    DeliverySortingCentersResult,
    DeliveryTaskInfo,
    LabelTaskResult,
    OrderActionResult,
    OrdersResult,
    OrderSummary,
    StockInfo,
    StockInfoResult,
    StockUpdateItem,
    StockUpdateResult,
)

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_orders(payload: object) -> OrdersResult:
    """Преобразует список заказов."""

    data = _expect_mapping(payload)
    return OrdersResult(
        items=[
            OrderSummary(
                order_id=_str(item, "id", "order_id", "orderId"),
                status=_str(item, "status"),
                created_at=_str(item, "created", "created_at", "createdAt"),
                buyer_name=_str(_mapping(item, "buyerInfo"), "fullName"),
                total_price=_int(item, "totalPrice", "price"),
                raw_payload=item,
            )
            for item in _list(data, "orders", "items", "result")
        ],
        total=_int(data, "total", "count"),
        raw_payload=data,
    )


def map_order_action(payload: object) -> OrderActionResult:
    """Преобразует результат операции над заказом."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    source = result or data
    return OrderActionResult(
        success=bool(source.get("success", data.get("success", True))),
        order_id=_str(source, "orderId", "order_id", "id"),
        status=_str(source, "status"),
        message=_str(source, "message"),
        raw_payload=data,
    )


def map_courier_ranges(payload: object) -> CourierRangesResult:
    """Преобразует интервалы курьерской доставки."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    source = result or data
    return CourierRangesResult(
        items=[
            CourierRange(
                interval_id=_str(item, "id", "intervalId"),
                date=_str(item, "date"),
                start_at=_str(item, "startAt", "startDate"),
                end_at=_str(item, "endAt", "endDate"),
                raw_payload=item,
            )
            for item in _list(source, "timeIntervals", "intervals", "items", "result")
        ],
        address=_str(source, "address"),
        raw_payload=data,
    )


def map_label_task(payload: object) -> LabelTaskResult:
    """Преобразует задачу генерации этикеток."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result", "data")
    source = result or data
    task_id = _str(source, "taskId", "taskID", "id")
    task_int = _int(source, "taskId", "taskID")
    return LabelTaskResult(
        task_id=task_id or (str(task_int) if task_int is not None else None),
        status=_str(source, "status"),
        raw_payload=data,
    )


def map_delivery_entity(payload: object) -> DeliveryEntityResult:
    """Преобразует результат операции delivery API."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result", "data")
    source = result or data
    task_id = _str(source, "taskId", "taskID")
    task_int = _int(source, "taskId", "taskID")
    return DeliveryEntityResult(
        success=bool(source.get("success", data.get("success", True))),
        task_id=task_id or (str(task_int) if task_int is not None else None),
        order_id=_str(source, "orderId", "orderID"),
        parcel_id=_str(source, "parcelId", "parcelID"),
        status=_str(source, "status"),
        message=_str(_mapping(data, "error"), "message") or _str(source, "message"),
        raw_payload=data,
    )


def map_sorting_centers(payload: object) -> DeliverySortingCentersResult:
    """Преобразует список сортировочных центров."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result", "data")
    source = result or data
    return DeliverySortingCentersResult(
        items=[
            DeliverySortingCenter(
                sorting_center_id=_str(item, "id", "sortingCenterId", "sorting_center_id"),
                name=_str(item, "name"),
                city=_str(item, "city"),
                raw_payload=item,
            )
            for item in _list(source, "sortingCenters", "items", "result")
        ],
        raw_payload=data,
    )


def map_delivery_task(payload: object) -> DeliveryTaskInfo:
    """Преобразует информацию о задаче доставки."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result", "data")
    source = result or data
    task_id = _str(source, "taskId", "taskID", "id")
    task_int = _int(source, "taskId", "taskID")
    return DeliveryTaskInfo(
        task_id=task_id or (str(task_int) if task_int is not None else None),
        status=_str(source, "status"),
        error=_str(_mapping(data, "error"), "message") or _str(source, "error"),
        raw_payload=data,
    )


def map_stock_info(payload: object) -> StockInfoResult:
    """Преобразует информацию по остаткам."""

    data = _expect_mapping(payload)
    return StockInfoResult(
        items=[
            StockInfo(
                item_id=_int(item, "item_id", "itemId"),
                quantity=_int(item, "quantity"),
                is_multiple=_bool(item, "is_multiple", "isMultiple"),
                is_unlimited=_bool(item, "is_unlimited", "isUnlimited"),
                is_out_of_stock=_bool(item, "is_out_of_stock", "isOutOfStock"),
                raw_payload=item,
            )
            for item in _list(data, "stocks", "items", "result")
        ],
        raw_payload=data,
    )


def map_stock_update(payload: object) -> StockUpdateResult:
    """Преобразует результат изменения остатков."""

    data = _expect_mapping(payload)
    return StockUpdateResult(
        items=[
            StockUpdateItem(
                item_id=_int(item, "item_id", "itemId"),
                external_id=_str(item, "external_id", "externalId"),
                success=bool(item.get("success", True)),
                errors=_extract_errors(item),
                raw_payload=item,
            )
            for item in _list(data, "stocks", "items", "result")
        ],
        raw_payload=data,
    )


def _extract_errors(payload: Payload) -> list[str]:
    errors = payload.get("errors")
    if not isinstance(errors, list):
        return []
    return [str(error) for error in errors if isinstance(error, str)]
