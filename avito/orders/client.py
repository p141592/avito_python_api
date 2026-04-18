"""Внутренние section clients для пакета orders."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.orders.mappers import (
    map_courier_ranges,
    map_delivery_entity,
    map_delivery_task,
    map_label_task,
    map_order_action,
    map_orders,
    map_sorting_centers,
    map_stock_info,
    map_stock_update,
)
from avito.orders.models import (
    CourierRangesResult,
    DeliveryAnnouncementRequest,
    DeliveryEntityResult,
    DeliveryParcelIdsRequest,
    DeliveryParcelRequest,
    DeliveryParcelResultRequest,
    DeliverySortingCentersResult,
    DeliveryTaskInfo,
    LabelPdfResult,
    LabelTaskResult,
    OrderAcceptReturnRequest,
    OrderActionResult,
    OrderApplyTransitionRequest,
    OrderCncDetailsRequest,
    OrderConfirmationCodeRequest,
    OrderCourierRangeRequest,
    OrderLabelsRequest,
    OrderMarkingsRequest,
    OrderTrackingNumberRequest,
    OrdersRequest,
    OrdersResult,
    SandboxAreasRequest,
    StockInfoRequest,
    StockInfoResult,
    StockUpdateRequest,
    StockUpdateResult,
)


@dataclass(slots=True)
class OrdersClient:
    """Выполняет HTTP-операции управления заказами."""

    transport: Transport

    def list_orders(self) -> OrdersResult:
        payload = self.transport.request_json(
            "GET",
            "/order-management/1/orders",
            context=RequestContext("orders.list_orders"),
        )
        return map_orders(payload)

    def update_markings(self, request: OrderMarkingsRequest) -> OrderActionResult:
        return self._post_action("/order-management/1/markings", "orders.update_markings", request)

    def accept_return_order(self, request: OrderAcceptReturnRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/acceptReturnOrder",
            "orders.accept_return_order",
            request,
        )

    def apply_transition(self, request: OrderApplyTransitionRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/applyTransition",
            "orders.apply_transition",
            request,
        )

    def check_confirmation_code(self, request: OrderConfirmationCodeRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/checkConfirmationCode",
            "orders.check_confirmation_code",
            request,
        )

    def set_cnc_details(self, request: OrderCncDetailsRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/cncSetDetails",
            "orders.set_cnc_details",
            request,
        )

    def get_courier_delivery_range(self) -> CourierRangesResult:
        payload = self.transport.request_json(
            "GET",
            "/order-management/1/order/getCourierDeliveryRange",
            context=RequestContext("orders.get_courier_delivery_range"),
        )
        return map_courier_ranges(payload)

    def set_courier_delivery_range(self, request: OrderCourierRangeRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/setCourierDeliveryRange",
            "orders.set_courier_delivery_range",
            request,
        )

    def set_tracking_number(self, request: OrderTrackingNumberRequest) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/setTrackingNumber",
            "orders.set_tracking_number",
            request,
        )

    def _post_action(
        self,
        path: str,
        operation: str,
        request: OrderMarkingsRequest
        | OrderAcceptReturnRequest
        | OrderApplyTransitionRequest
        | OrderConfirmationCodeRequest
        | OrderCncDetailsRequest
        | OrderCourierRangeRequest
        | OrderTrackingNumberRequest,
    ) -> OrderActionResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_order_action(payload)


@dataclass(slots=True)
class LabelsClient:
    """Выполняет операции генерации и загрузки PDF-этикеток."""

    transport: Transport

    def create_generate_labels(self, request: OrderLabelsRequest) -> LabelTaskResult:
        return self._create("/order-management/1/orders/labels", "orders.labels.create", request)

    def create_generate_labels_extended(self, request: OrderLabelsRequest) -> LabelTaskResult:
        return self._create(
            "/order-management/1/orders/labels/extended",
            "orders.labels.create_extended",
            request,
        )

    def get_download_label(self, *, task_id: str) -> LabelPdfResult:
        binary = self.transport.download_binary(
            f"/order-management/1/orders/labels/{task_id}/download",
            context=RequestContext("orders.labels.download"),
        )
        return LabelPdfResult(binary=binary)

    def _create(self, path: str, operation: str, request: OrderLabelsRequest) -> LabelTaskResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_label_task(payload)


@dataclass(slots=True)
class DeliveryClient:
    """Выполняет production-операции доставки."""

    transport: Transport

    def create_announcement(self, request: DeliveryAnnouncementRequest) -> DeliveryEntityResult:
        return self._post("/createAnnouncement", "orders.delivery.create_announcement", request)

    def cancel_announcement(self, request: DeliveryAnnouncementRequest) -> DeliveryEntityResult:
        return self._post("/cancelAnnouncement", "orders.delivery.cancel_announcement", request)

    def create_parcel(self, request: DeliveryParcelRequest) -> DeliveryEntityResult:
        return self._post("/createParcel", "orders.delivery.create_parcel", request)

    def change_parcel_result(self, request: DeliveryParcelResultRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery/order/changeParcelResult",
            "orders.delivery.change_parcel_result",
            request,
        )

    def update_change_parcels(self, request: DeliveryParcelIdsRequest) -> DeliveryEntityResult:
        return self._post(
            "/sandbox/changeParcels", "orders.delivery.update_change_parcels", request
        )

    def _post(
        self,
        path: str,
        operation: str,
        request: DeliveryAnnouncementRequest
        | DeliveryParcelRequest
        | DeliveryParcelResultRequest
        | DeliveryParcelIdsRequest,
    ) -> DeliveryEntityResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_delivery_entity(payload)


@dataclass(slots=True)
class SandboxDeliveryClient:
    """Выполняет sandbox-операции доставки."""

    transport: Transport

    def create_announcement(self, request: DeliveryAnnouncementRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/announcements/create", "orders.sandbox.create_announcement", request
        )

    def track_announcement(self, request: DeliveryAnnouncementRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/announcements/track", "orders.sandbox.track_announcement", request
        )

    def update_custom_area_schedule(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/areas/custom-schedule",
            "orders.sandbox.update_custom_area_schedule",
            request,
        )

    def cancel_parcel(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post("/delivery-sandbox/cancelParcel", "orders.sandbox.cancel_parcel", request)

    def check_confirmation_code(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/checkConfirmationCode",
            "orders.sandbox.check_confirmation_code",
            request,
        )

    def set_order_properties(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/properties",
            "orders.sandbox.set_order_properties",
            request,
        )

    def set_order_real_address(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/realAddress",
            "orders.sandbox.set_order_real_address",
            request,
        )

    def tracking(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post("/delivery-sandbox/order/tracking", "orders.sandbox.tracking", request)

    def prohibit_order_acceptance(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/prohibitOrderAcceptance",
            "orders.sandbox.prohibit_order_acceptance",
            request,
        )

    def list_sorting_center(self) -> DeliverySortingCentersResult:
        payload = self.transport.request_json(
            "GET",
            "/delivery-sandbox/sorting-center",
            context=RequestContext("orders.sandbox.list_sorting_center"),
        )
        return map_sorting_centers(payload)

    def add_sorting_center(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/tariffs/sorting-center",
            "orders.sandbox.add_sorting_center",
            request,
        )

    def add_areas(self, *, tariff_id: str, request: SandboxAreasRequest) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/areas",
            "orders.sandbox.add_areas",
            request,
        )

    def add_tags_to_sorting_center(
        self, *, tariff_id: str, request: OrdersRequest
    ) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers",
            "orders.sandbox.add_tags_to_sorting_center",
            request,
        )

    def add_terminals(self, *, tariff_id: str, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/terminals",
            "orders.sandbox.add_terminals",
            request,
        )

    def update_terms(self, *, tariff_id: str, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/terms",
            "orders.sandbox.update_terms",
            request,
        )

    def add_tariff_v2(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post("/delivery-sandbox/tariffsV2", "orders.sandbox.add_tariff_v2", request)

    def v1_cancel_announcement(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/cancelAnnouncement",
            "orders.sandbox.v1_cancel_announcement",
            request,
        )

    def v1_cancel_parcel(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/cancelParcel", "orders.sandbox.v1_cancel_parcel", request
        )

    def v1_change_parcel(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/changeParcel", "orders.sandbox.v1_change_parcel", request
        )

    def v1_create_announcement(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/createAnnouncement",
            "orders.sandbox.v1_create_announcement",
            request,
        )

    def v1_get_announcement_event(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getAnnouncementEvent",
            "orders.sandbox.v1_get_announcement_event",
            request,
        )

    def v1_get_change_parcel_info(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getChangeParcelInfo",
            "orders.sandbox.v1_get_change_parcel_info",
            request,
        )

    def v1_get_parcel_info(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getParcelInfo",
            "orders.sandbox.v1_get_parcel_info",
            request,
        )

    def v1_get_registered_parcel_id(self, request: OrdersRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getRegisteredParcelID",
            "orders.sandbox.v1_get_registered_parcel_id",
            request,
        )

    def create_parcel_v2(self, request: DeliveryParcelRequest) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v2/createParcel", "orders.sandbox.create_parcel_v2", request
        )

    def _post(
        self,
        path: str,
        operation: str,
        request: OrdersRequest
        | DeliveryAnnouncementRequest
        | SandboxAreasRequest
        | DeliveryParcelRequest,
    ) -> DeliveryEntityResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_delivery_entity(payload)


@dataclass(slots=True)
class DeliveryTasksClient:
    """Получает статус задач delivery API."""

    transport: Transport

    def get_task(self, *, task_id: str) -> DeliveryTaskInfo:
        payload = self.transport.request_json(
            "GET",
            f"/delivery-sandbox/tasks/{task_id}",
            context=RequestContext("orders.delivery_task.get_task", allow_retry=True),
        )
        return map_delivery_task(payload)


@dataclass(slots=True)
class StockManagementClient:
    """Выполняет операции управления остатками."""

    transport: Transport

    def get_info(self, request: StockInfoRequest) -> StockInfoResult:
        payload = self.transport.request_json(
            "POST",
            "/stock-management/1/info",
            context=RequestContext("orders.stock.get_info", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_stock_info(payload)

    def update_stocks(self, request: StockUpdateRequest) -> StockUpdateResult:
        payload = self.transport.request_json(
            "PUT",
            "/stock-management/1/stocks",
            context=RequestContext("orders.stock.update_stocks", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_stock_update(payload)


__all__ = (
    "DeliveryClient",
    "DeliveryTasksClient",
    "LabelsClient",
    "OrdersClient",
    "SandboxDeliveryClient",
    "StockManagementClient",
)
