"""Доменные объекты пакета orders."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import Transport
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
    JsonRequest,
    LabelPdfResult,
    LabelTaskResult,
    OrderActionResult,
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

    def update_markings(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).update_markings(JsonRequest(payload))

    def accept_return_order(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).accept_return_order(JsonRequest(payload))

    def apply(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).apply_transition(JsonRequest(payload))

    def check_confirmation_code(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).check_confirmation_code(JsonRequest(payload))

    def set_cnc_details(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).set_cnc_details(JsonRequest(payload))

    def get_courier_delivery_range(self) -> CourierRangesResult:
        return OrdersClient(self.transport).get_courier_delivery_range()

    def set_courier_delivery_range(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).set_courier_delivery_range(JsonRequest(payload))

    def update_tracking_number(self, *, payload: Mapping[str, object]) -> OrderActionResult:
        return OrdersClient(self.transport).set_tracking_number(JsonRequest(payload))


@dataclass(slots=True, frozen=True)
class OrderLabel(DomainObject):
    """Доменный объект генерации и загрузки этикеток."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create(self, *, payload: Mapping[str, object], extended: bool = False) -> LabelTaskResult:
        client = LabelsClient(self.transport)
        request = JsonRequest(payload)
        if extended:
            return client.create_generate_labels_extended(request)
        return client.create_generate_labels(request)

    def download(self, *, task_id: str | None = None) -> LabelPdfResult:
        resolved_task_id = task_id or self._require_task_id()
        return LabelsClient(self.transport).get_download_label(task_id=resolved_task_id)

    def _require_task_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `task_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class DeliveryOrder(DomainObject):
    """Доменный объект production API доставки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_announcement(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_announcement(JsonRequest(payload))

    def delete(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).cancel_announcement(JsonRequest(payload))

    def create(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_parcel(JsonRequest(payload))

    def update_change_parcels(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).update_change_parcels(JsonRequest(payload))

    def create_change_parcel_result(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).change_parcel_result(JsonRequest(payload))


@dataclass(slots=True, frozen=True)
class SandboxDelivery(DomainObject):
    """Доменный объект sandbox API доставки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_announcement(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_announcement(JsonRequest(payload))

    def track_announcement(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).track_announcement(JsonRequest(payload))

    def update_custom_area_schedule(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_custom_area_schedule(JsonRequest(payload))

    def cancel_parcel(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).cancel_parcel(JsonRequest(payload))

    def check_confirmation_code(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).check_confirmation_code(JsonRequest(payload))

    def set_order_properties(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_properties(JsonRequest(payload))

    def set_order_real_address(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_real_address(JsonRequest(payload))

    def tracking(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).tracking(JsonRequest(payload))

    def prohibit_order_acceptance(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).prohibit_order_acceptance(JsonRequest(payload))

    def list_sorting_center(self) -> DeliverySortingCentersResult:
        return SandboxDeliveryClient(self.transport).list_sorting_center()

    def add_sorting_center(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_sorting_center(JsonRequest(payload))

    def add_areas(self, *, tariff_id: str, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_areas(tariff_id=tariff_id, request=JsonRequest(payload))

    def add_tags_to_sorting_center(self, *, tariff_id: str, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tags_to_sorting_center(
            tariff_id=tariff_id,
            request=JsonRequest(payload),
        )

    def add_terminals(self, *, tariff_id: str, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_terminals(tariff_id=tariff_id, request=JsonRequest(payload))

    def update_terms(self, *, tariff_id: str, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_terms(tariff_id=tariff_id, request=JsonRequest(payload))

    def add_tariff_v2(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tariff_v2(JsonRequest(payload))

    def create_parcel(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_parcel_v2(JsonRequest(payload))

    def legacy_cancel_announcement(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_cancel_announcement(JsonRequest(payload))

    def legacy_cancel_parcel(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_cancel_parcel(JsonRequest(payload))

    def legacy_change_parcel(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_change_parcel(JsonRequest(payload))

    def legacy_create_announcement(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_create_announcement(JsonRequest(payload))

    def legacy_get_announcement_event(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_announcement_event(JsonRequest(payload))

    def legacy_get_change_parcel_info(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_change_parcel_info(JsonRequest(payload))

    def legacy_get_parcel_info(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_parcel_info(JsonRequest(payload))

    def legacy_get_registered_parcel_id(self, *, payload: Mapping[str, object]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).v1_get_registered_parcel_id(JsonRequest(payload))


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
            raise ValueError("Для операции требуется `task_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class Stock(DomainObject):
    """Доменный объект управления остатками."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, payload: Mapping[str, object]) -> StockInfoResult:
        return StockManagementClient(self.transport).get_info(JsonRequest(payload))

    def update(self, *, payload: Mapping[str, object]) -> StockUpdateResult:
        return StockManagementClient(self.transport).update_stocks(JsonRequest(payload))


__all__ = ("DeliveryOrder", "DeliveryTask", "DomainObject", "Order", "OrderLabel", "SandboxDelivery", "Stock")
