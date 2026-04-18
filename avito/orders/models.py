"""Типизированные модели раздела orders."""

from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from avito.core import BinaryResponse
from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class OrdersRequest:
    """Унифицированный typed request для Orders API."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class OrderSummary:
    """Краткая информация о заказе."""

    order_id: str | None
    status: str | None
    created_at: str | None
    buyer_name: str | None
    total_price: int | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class OrdersResult:
    """Список заказов."""

    items: list[OrderSummary]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class OrderActionResult:
    """Результат операции над заказом."""

    success: bool
    order_id: str | None = None
    status: str | None = None
    message: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CourierRange:
    """Доступный интервал курьерской доставки."""

    interval_id: str | None
    date: str | None
    start_at: str | None
    end_at: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CourierRangesResult:
    """Список доступных интервалов курьерской доставки."""

    items: list[CourierRange]
    address: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LabelTaskResult:
    """Результат генерации этикеток."""

    task_id: str | None
    status: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LabelPdfResult:
    """PDF-этикетка заказа."""

    binary: BinaryResponse

    @property
    def filename(self) -> str | None:
        """Имя PDF-файла."""

        return self.binary.filename

    def to_dict(self) -> dict[str, Any]:
        """Сериализует бинарный результат без transport-объекта."""

        return {
            "filename": self.binary.filename,
            "content_type": self.binary.content_type,
            "content_base64": b64encode(self.binary.content).decode("ascii"),
        }

    def model_dump(self) -> dict[str, Any]:
        return self.to_dict()


@dataclass(slots=True, frozen=True)
class DeliveryEntityResult:
    """Результат операции delivery API."""

    success: bool
    task_id: str | None = None
    order_id: str | None = None
    parcel_id: str | None = None
    status: str | None = None
    message: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DeliverySortingCenter:
    """Сортировочный центр доставки."""

    sorting_center_id: str | None
    name: str | None
    city: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DeliverySortingCentersResult:
    """Список сортировочных центров доставки."""

    items: list[DeliverySortingCenter]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DeliveryTaskInfo:
    """Информация о задаче доставки."""

    task_id: str | None
    status: str | None
    error: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StockInfo:
    """Информация по остаткам объявления."""

    item_id: int | None
    quantity: int | None
    is_multiple: bool | None
    is_unlimited: bool | None
    is_out_of_stock: bool | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StockInfoResult:
    """Список текущих остатков."""

    items: list[StockInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StockUpdateItem:
    """Результат обновления остатков объявления."""

    item_id: int | None
    external_id: str | None
    success: bool
    errors: list[str]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StockUpdateResult:
    """Результат изменения остатков."""

    items: list[StockUpdateItem]
    _payload: Mapping[str, object] = field(default_factory=dict)


enable_module_serialization(globals())
