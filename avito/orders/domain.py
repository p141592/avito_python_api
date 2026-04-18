"""Доменные объекты пакета orders."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import Transport, ValidationError
from avito.orders.client import (
    DeliveryClient,
    DeliveryTasksClient,
    LabelsClient,
    OrdersClient,
    SandboxDeliveryClient,
    StockManagementClient,
)
from avito.orders.models import (
    CourierRangesResult,
    DeliveryEntityResult,
    DeliverySortingCentersResult,
    DeliveryTaskInfo,
    LabelPdfResult,
    LabelTaskResult,
    OrderActionResult,
    OrdersRequest,
    OrdersResult,
    StockInfoResult,
    StockUpdateResult,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела orders."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class Order(DomainObject):
    """Доменный объект заказа."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list(self) -> OrdersResult:
        return OrdersClient(self.transport).list_orders()

    def update_markings(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).update_markings(request)

    def accept_return_order(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).accept_return_order(request)

    def apply(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).apply_transition(request)

    def check_confirmation_code(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).check_confirmation_code(request)

    def set_cnc_details(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).set_cnc_details(request)

    def get_courier_delivery_range(self) -> CourierRangesResult:
        return OrdersClient(self.transport).get_courier_delivery_range()

    def set_courier_delivery_range(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).set_courier_delivery_range(request)

    def update_tracking_number(self, *, request: OrdersRequest) -> OrderActionResult:
        return OrdersClient(self.transport).set_tracking_number(request)


@dataclass(slots=True, frozen=True)
class OrderLabel(DomainObject):
    """Доменный объект генерации и загрузки этикеток."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create(self, *, request: OrdersRequest, extended: bool = False) -> LabelTaskResult:
        client = LabelsClient(self.transport)
        if extended:
            return client.create_generate_labels_extended(request)
        return client.create_generate_labels(request)

    def download(self, *, task_id: str | None = None) -> LabelPdfResult:
        resolved_task_id = task_id or self._require_task_id()
        return LabelsClient(self.transport).get_download_label(task_id=resolved_task_id)

    def _require_task_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class DeliveryOrder(DomainObject):
    """Доменный объект production API доставки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_announcement(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_announcement(request)

    def delete(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).cancel_announcement(request)

    def create(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_parcel(request)

    def update_change_parcels(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).update_change_parcels(request)

    def create_change_parcel_result(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).change_parcel_result(request)


@dataclass(slots=True, frozen=True)
class SandboxDelivery(DomainObject):
    """Доменный объект sandbox API доставки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_announcement(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_announcement(request)

    def track_announcement(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).track_announcement(request)

    def update_custom_area_schedule(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_custom_area_schedule(request)

    def cancel_parcel(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).cancel_parcel(request)

    def check_confirmation_code(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).check_confirmation_code(request)

    def set_order_properties(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_properties(request)

    def set_order_real_address(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_real_address(request)

    def tracking(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).tracking(request)

    def prohibit_order_acceptance(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).prohibit_order_acceptance(request)

    def list_sorting_center(self) -> DeliverySortingCentersResult:
        return SandboxDeliveryClient(self.transport).list_sorting_center()

    def add_sorting_center(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_sorting_center(request)

    def add_areas(self, *, tariff_id: str, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_areas(
            tariff_id=tariff_id, request=request
        )

    def add_tags_to_sorting_center(
        self, *, tariff_id: str, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tags_to_sorting_center(
            tariff_id=tariff_id,
            request=request,
        )

    def add_terminals(
        self, *, tariff_id: str, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_terminals(
            tariff_id=tariff_id, request=request
        )

    def update_terms(
        self, *, tariff_id: str, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_terms(
            tariff_id=tariff_id, request=request
        )

    def add_tariff_v2(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tariff_v2(request)

    def create_parcel(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_parcel_v2(request)

    def cancel_announcement_v1(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_cancel_announcement(request)

    def cancel_parcel_v1(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_cancel_parcel(request)

    def change_parcel_v1(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_change_parcel(request)

    def create_announcement_v1(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_create_announcement(request)

    def get_announcement_event_v1(
        self, *, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_announcement_event(request)

    def get_change_parcel_info_v1(
        self, *, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_change_parcel_info(request)

    def get_parcel_info_v1(self, *, request: OrdersRequest) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_parcel_info(request)

    def get_registered_parcel_id_v1(
        self, *, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_registered_parcel_id(request)


@dataclass(slots=True, frozen=True)
class DeliveryTask(DomainObject):
    """Доменный объект задачи доставки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, task_id: str | None = None) -> DeliveryTaskInfo:
        resolved_task_id = task_id or self._require_task_id()
        return DeliveryTasksClient(self.transport).get_task(task_id=resolved_task_id)

    def _require_task_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class Stock(DomainObject):
    """Доменный объект управления остатками."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, request: OrdersRequest) -> StockInfoResult:
        return StockManagementClient(self.transport).get_info(request)

    def update(self, *, request: OrdersRequest) -> StockUpdateResult:
        return StockManagementClient(self.transport).update_stocks(request)


__all__ = (
    "DeliveryOrder",
    "DeliveryTask",
    "DomainObject",
    "Order",
    "OrderLabel",
    "SandboxDelivery",
    "Stock",
)
