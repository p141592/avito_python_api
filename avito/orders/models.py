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
    """Временный generic request для ещё не мигрированных endpoints orders."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class OrderMarkingsRequest:
    """Запрос обновления маркировок заказа."""

    order_id: str
    codes: list[str]

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "codes": list(self.codes)}


@dataclass(slots=True, frozen=True)
class OrderAcceptReturnRequest:
    """Запрос подтверждения возврата заказа."""

    order_id: str
    postal_office_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "postalOfficeId": self.postal_office_id}


@dataclass(slots=True, frozen=True)
class OrderApplyTransitionRequest:
    """Запрос перехода заказа в другой статус."""

    order_id: str
    transition: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "transition": self.transition}


@dataclass(slots=True, frozen=True)
class OrderConfirmationCodeRequest:
    """Запрос проверки кода подтверждения заказа."""

    order_id: str
    code: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "code": self.code}


@dataclass(slots=True, frozen=True)
class OrderCncDetailsRequest:
    """Запрос установки деталей cnc-заказа."""

    order_id: str
    pickup_point_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "pickupPointId": self.pickup_point_id}


@dataclass(slots=True, frozen=True)
class OrderCourierRangeRequest:
    """Запрос установки интервала курьерской доставки."""

    order_id: str
    interval_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "intervalId": self.interval_id}


@dataclass(slots=True, frozen=True)
class OrderTrackingNumberRequest:
    """Запрос установки трек-номера."""

    order_id: str
    tracking_number: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "trackingNumber": self.tracking_number}


@dataclass(slots=True, frozen=True)
class OrderLabelsRequest:
    """Запрос генерации этикеток."""

    order_ids: list[str]

    def to_payload(self) -> dict[str, object]:
        return {"orderIds": list(self.order_ids)}


@dataclass(slots=True, frozen=True)
class DeliveryAnnouncementRequest:
    """Запрос создания или отмены анонса доставки."""

    order_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id}


@dataclass(slots=True, frozen=True)
class DeliveryParcelRequest:
    """Запрос создания посылки."""

    order_id: str
    parcel_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "parcelId": self.parcel_id}


@dataclass(slots=True, frozen=True)
class DeliveryParcelResultRequest:
    """Запрос передачи результата по посылке."""

    parcel_id: str
    result: str

    def to_payload(self) -> dict[str, object]:
        return {"parcelId": self.parcel_id, "result": self.result}


@dataclass(slots=True, frozen=True)
class DeliveryParcelIdsRequest:
    """Запрос пакетной операции по посылкам."""

    parcel_ids: list[str]

    def to_payload(self) -> dict[str, object]:
        return {"parcelIds": list(self.parcel_ids)}


@dataclass(slots=True, frozen=True)
class SandboxArea:
    """Зона sandbox-доставки."""

    city: str

    def to_payload(self) -> dict[str, object]:
        return {"city": self.city}


@dataclass(slots=True, frozen=True)
class SandboxAreasRequest:
    """Запрос добавления зон sandbox-доставки."""

    areas: list[SandboxArea]

    def to_payload(self) -> dict[str, object]:
        return {"areas": [area.to_payload() for area in self.areas]}


@dataclass(slots=True, frozen=True)
class StockInfoRequest:
    """Запрос текущих остатков."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        return {"itemIds": list(self.item_ids)}


@dataclass(slots=True, frozen=True)
class StockUpdateEntry:
    """Остаток по одному объявлению."""

    item_id: int
    quantity: int

    def to_payload(self) -> dict[str, object]:
        return {"item_id": self.item_id, "quantity": self.quantity}


@dataclass(slots=True, frozen=True)
class StockUpdateRequest:
    """Запрос обновления остатков."""

    stocks: list[StockUpdateEntry]

    def to_payload(self) -> dict[str, object]:
        return {"stocks": [stock.to_payload() for stock in self.stocks]}


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
