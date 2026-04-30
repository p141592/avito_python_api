"""Внутренние section clients для пакета orders."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.orders.enums import TrackingAvitoEventType, TrackingAvitoStatus
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
    AddSortingCentersRequest,
    AddTariffV2Request,
    AddTerminalsRequest,
    CancelParcelRequest,
    CancelSandboxParcelOptions,
    CancelSandboxParcelRequest,
    ChangeParcelApplication,
    ChangeParcelOptions,
    ChangeParcelRequest,
    CourierRangesResult,
    CustomAreaScheduleEntry,
    CustomAreaScheduleRequest,
    DeliveryAnnouncementRequest,
    DeliveryDirection,
    DeliveryEntityResult,
    DeliveryParcelIdsRequest,
    DeliveryParcelRequest,
    DeliveryParcelResultRequest,
    DeliverySortingCentersResult,
    DeliveryTariffZone,
    DeliveryTaskInfo,
    DeliveryTermsZone,
    DeliveryTrackingOptions,
    DeliveryTrackingRequest,
    GetChangeParcelInfoRequest,
    GetRegisteredParcelIdRequest,
    GetSandboxParcelInfoRequest,
    LabelPdfResult,
    LabelTaskResult,
    OrderAcceptReturnRequest,
    OrderActionResult,
    OrderApplyTransitionRequest,
    OrderCncDetailsRequest,
    OrderConfirmationCodeRequest,
    OrderCourierRangeRequest,
    OrderDeliveryProperties,
    OrderLabelsRequest,
    OrderMarkingsRequest,
    OrdersResult,
    OrderTrackingNumberRequest,
    ProhibitOrderAcceptanceRequest,
    RealAddress,
    SandboxAnnouncementPackage,
    SandboxAnnouncementParticipant,
    SandboxArea,
    SandboxAreasRequest,
    SandboxCancelAnnouncementOptions,
    SandboxCancelAnnouncementRequest,
    SandboxConfirmationCodeRequest,
    SandboxCreateAnnouncementOptions,
    SandboxCreateAnnouncementRequest,
    SandboxGetAnnouncementEventRequest,
    SetOrderPropertiesRequest,
    SetOrderRealAddressRequest,
    SortingCenterUpload,
    StockInfoRequest,
    StockInfoResult,
    StockUpdateEntry,
    StockUpdateRequest,
    StockUpdateResult,
    TaggedSortingCenter,
    TaggedSortingCentersRequest,
    TerminalUpload,
    UpdateTermsRequest,
)


@dataclass(slots=True, frozen=True)
class OrdersClient:
    """Выполняет HTTP-операции управления заказами."""

    transport: Transport

    def list_orders(self) -> OrdersResult:
        return self.transport.request_public_model(
            "GET",
            "/order-management/1/orders",
            context=RequestContext("orders.list_orders"),
            mapper=map_orders,
        )

    def update_markings(
        self, *, order_id: str, codes: list[str], idempotency_key: str | None = None
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/markings",
            "orders.update_markings",
            OrderMarkingsRequest(order_id=order_id, codes=codes),
            idempotency_key=idempotency_key,
        )

    def accept_return_order(
        self,
        *,
        order_id: str,
        postal_office_id: str,
        idempotency_key: str | None = None,
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/acceptReturnOrder",
            "orders.accept_return_order",
            OrderAcceptReturnRequest(order_id=order_id, postal_office_id=postal_office_id),
            idempotency_key=idempotency_key,
        )

    def apply_transition(
        self, *, order_id: str, transition: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/applyTransition",
            "orders.apply_transition",
            OrderApplyTransitionRequest(order_id=order_id, transition=transition),
            idempotency_key=idempotency_key,
        )

    def check_confirmation_code(
        self, *, order_id: str, code: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/checkConfirmationCode",
            "orders.check_confirmation_code",
            OrderConfirmationCodeRequest(order_id=order_id, code=code),
            idempotency_key=idempotency_key,
        )

    def set_cnc_details(
        self, *, order_id: str, pickup_point_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/cncSetDetails",
            "orders.set_cnc_details",
            OrderCncDetailsRequest(order_id=order_id, pickup_point_id=pickup_point_id),
            idempotency_key=idempotency_key,
        )

    def get_courier_delivery_range(
        self,
        *,
        order_id: str = "order-1",
        address: str | None = None,
    ) -> CourierRangesResult:
        params: dict[str, object] = {"orderId": order_id}
        if address is not None:
            params["address"] = address
        return self.transport.request_public_model(
            "GET",
            "/order-management/1/order/getCourierDeliveryRange",
            context=RequestContext("orders.get_courier_delivery_range"),
            mapper=map_courier_ranges,
            params=params,
        )

    def set_courier_delivery_range(
        self, *, order_id: str, interval_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/setCourierDeliveryRange",
            "orders.set_courier_delivery_range",
            OrderCourierRangeRequest(order_id=order_id, interval_id=interval_id),
            idempotency_key=idempotency_key,
        )

    def set_tracking_number(
        self,
        *,
        order_id: str,
        tracking_number: str,
        idempotency_key: str | None = None,
    ) -> OrderActionResult:
        return self._post_action(
            "/order-management/1/order/setTrackingNumber",
            "orders.set_tracking_number",
            OrderTrackingNumberRequest(order_id=order_id, tracking_number=tracking_number),
            idempotency_key=idempotency_key,
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
        idempotency_key: str | None = None,
    ) -> OrderActionResult:
        return self.transport.request_public_model(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=idempotency_key is not None),
            mapper=map_order_action,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class LabelsClient:
    """Выполняет операции генерации и загрузки PDF-этикеток."""

    transport: Transport

    def create_generate_labels(
        self, *, order_ids: list[str], idempotency_key: str | None = None
    ) -> LabelTaskResult:
        return self._create(
            "/order-management/1/orders/labels",
            "orders.labels.create",
            OrderLabelsRequest(order_ids=order_ids),
            idempotency_key=idempotency_key,
        )

    def create_generate_labels_extended(
        self, *, order_ids: list[str], idempotency_key: str | None = None
    ) -> LabelTaskResult:
        return self._create(
            "/order-management/1/orders/labels/extended",
            "orders.labels.create_extended",
            OrderLabelsRequest(order_ids=order_ids),
            idempotency_key=idempotency_key,
        )

    def get_download_label(self, *, task_id: str) -> LabelPdfResult:
        binary = self.transport.download_binary(
            f"/order-management/1/orders/labels/{task_id}/download",
            context=RequestContext("orders.labels.download"),
        )
        return LabelPdfResult(binary=binary)

    def _create(
        self,
        path: str,
        operation: str,
        request: OrderLabelsRequest,
        idempotency_key: str | None = None,
    ) -> LabelTaskResult:
        return self.transport.request_public_model(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=idempotency_key is not None),
            mapper=map_label_task,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class DeliveryClient:
    """Выполняет production-операции доставки."""

    transport: Transport

    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/createAnnouncement",
            "orders.delivery.create_announcement",
            DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def cancel_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/cancelAnnouncement",
            "orders.delivery.cancel_announcement",
            DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def create_parcel(
        self,
        *,
        order_id: str,
        parcel_id: str,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/createParcel",
            "orders.delivery.create_parcel",
            DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )

    def change_parcel_result(
        self, *, parcel_id: str, result: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery/order/changeParcelResult",
            "orders.delivery.change_parcel_result",
            DeliveryParcelResultRequest(parcel_id=parcel_id, result=result),
            idempotency_key=idempotency_key,
        )

    def update_change_parcels(
        self, *, parcel_ids: list[str], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/sandbox/changeParcels",
            "orders.delivery.update_change_parcels",
            DeliveryParcelIdsRequest(parcel_ids=parcel_ids),
            idempotency_key=idempotency_key,
        )

    def _post(
        self,
        path: str,
        operation: str,
        request: DeliveryAnnouncementRequest
        | DeliveryParcelRequest
        | DeliveryParcelResultRequest
        | DeliveryParcelIdsRequest,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self.transport.request_public_model(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=idempotency_key is not None),
            mapper=map_delivery_entity,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class SandboxDeliveryClient:
    """Выполняет sandbox-операции доставки."""

    transport: Transport

    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/announcements/create",
            "orders.sandbox.create_announcement",
            DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def track_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/announcements/track",
            "orders.sandbox.track_announcement",
            DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def update_custom_area_schedule(
        self, *, items: list[CustomAreaScheduleEntry], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/areas/custom-schedule",
            "orders.sandbox.update_custom_area_schedule",
            CustomAreaScheduleRequest(items=items),
            idempotency_key=idempotency_key,
        )

    def cancel_parcel(
        self, *, parcel_id: str, actor: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/cancelParcel",
            "orders.sandbox.cancel_parcel",
            CancelParcelRequest(parcel_id=parcel_id, actor=actor),
            idempotency_key=idempotency_key,
        )

    def check_confirmation_code(
        self, *, parcel_id: str, confirm_code: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/checkConfirmationCode",
            "orders.sandbox.check_confirmation_code",
            SandboxConfirmationCodeRequest(parcel_id=parcel_id, confirm_code=confirm_code),
            idempotency_key=idempotency_key,
        )

    def set_order_properties(
        self,
        *,
        order_id: str,
        properties: OrderDeliveryProperties,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/properties",
            "orders.sandbox.set_order_properties",
            SetOrderPropertiesRequest(order_id=order_id, properties=properties),
            idempotency_key=idempotency_key,
        )

    def set_order_real_address(
        self,
        *,
        order_id: str,
        address: RealAddress,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/realAddress",
            "orders.sandbox.set_order_real_address",
            SetOrderRealAddressRequest(order_id=order_id, address=address),
            idempotency_key=idempotency_key,
        )

    def tracking(
        self,
        *,
        order_id: str,
        avito_status: TrackingAvitoStatus | str,
        avito_event_type: TrackingAvitoEventType | str,
        provider_event_code: str,
        date: str,
        location: str,
        comment: str | None = None,
        options: DeliveryTrackingOptions | None = None,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/order/tracking",
            "orders.sandbox.tracking",
            DeliveryTrackingRequest(
                order_id=order_id,
                avito_status=avito_status,
                avito_event_type=avito_event_type,
                provider_event_code=provider_event_code,
                date=date,
                location=location,
                comment=comment,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )

    def prohibit_order_acceptance(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/prohibitOrderAcceptance",
            "orders.sandbox.prohibit_order_acceptance",
            ProhibitOrderAcceptanceRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def list_sorting_center(
        self,
        *,
        delivery_providers: list[str] | None = None,
    ) -> DeliverySortingCentersResult:
        providers = delivery_providers or ["pochta"]
        return self.transport.request_public_model(
            "GET",
            "/delivery-sandbox/sorting-center",
            context=RequestContext("orders.sandbox.list_sorting_center"),
            mapper=map_sorting_centers,
            params={"deliveryProviders": ",".join(providers)},
        )

    def add_sorting_center(
        self, *, items: list[SortingCenterUpload], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/tariffs/sorting-center",
            "orders.sandbox.add_sorting_center",
            AddSortingCentersRequest(items=items),
            idempotency_key=idempotency_key,
        )

    def add_areas(
        self,
        *,
        tariff_id: str,
        areas: list[SandboxArea],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/areas",
            "orders.sandbox.add_areas",
            SandboxAreasRequest(areas=areas),
            idempotency_key=idempotency_key,
        )

    def add_tags_to_sorting_center(
        self,
        *,
        tariff_id: str,
        items: list[TaggedSortingCenter],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers",
            "orders.sandbox.add_tags_to_sorting_center",
            TaggedSortingCentersRequest(items=items),
            idempotency_key=idempotency_key,
        )

    def add_terminals(
        self,
        *,
        tariff_id: str,
        items: list[TerminalUpload],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/terminals",
            "orders.sandbox.add_terminals",
            AddTerminalsRequest(items=items),
            idempotency_key=idempotency_key,
        )

    def update_terms(
        self,
        *,
        tariff_id: str,
        items: list[DeliveryTermsZone],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            f"/delivery-sandbox/tariffs/{tariff_id}/terms",
            "orders.sandbox.update_terms",
            UpdateTermsRequest(items=items),
            idempotency_key=idempotency_key,
        )

    def add_tariff(
        self,
        *,
        name: str,
        delivery_provider_tariff_id: str,
        directions: list[DeliveryDirection],
        tariff_zones: list[DeliveryTariffZone],
        terms_zones: list[DeliveryTermsZone],
        tariff_type: str | None = None,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/tariffsV2",
            "orders.sandbox.add_tariff",
            AddTariffV2Request(
                name=name,
                delivery_provider_tariff_id=delivery_provider_tariff_id,
                directions=directions,
                tariff_zones=tariff_zones,
                terms_zones=terms_zones,
                tariff_type=tariff_type,
            ),
            idempotency_key=idempotency_key,
        )

    def cancel_sandbox_announcement(
        self,
        *,
        announcement_id: str,
        date: str,
        options: SandboxCancelAnnouncementOptions,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/cancelAnnouncement",
            "orders.sandbox.cancel_sandbox_announcement",
            SandboxCancelAnnouncementRequest(
                announcement_id=announcement_id,
                date=date,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )

    def cancel_sandbox_parcel(
        self,
        *,
        parcel_id: str,
        options: CancelSandboxParcelOptions | None = None,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/cancelParcel",
            "orders.sandbox.cancel_sandbox_parcel",
            CancelSandboxParcelRequest(parcel_id=parcel_id, options=options),
            idempotency_key=idempotency_key,
        )

    def change_sandbox_parcel(
        self,
        *,
        type: str,
        parcel_id: str,
        application: ChangeParcelApplication | None = None,
        options: ChangeParcelOptions | None = None,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/changeParcel",
            "orders.sandbox.change_sandbox_parcel",
            ChangeParcelRequest(
                type=type,
                parcel_id=parcel_id,
                application=application,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )

    def create_sandbox_announcement(
        self,
        *,
        announcement_id: str,
        barcode: str,
        sender: SandboxAnnouncementParticipant,
        receiver: SandboxAnnouncementParticipant,
        announcement_type: str,
        date: str,
        packages: list[SandboxAnnouncementPackage],
        options: SandboxCreateAnnouncementOptions,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/createAnnouncement",
            "orders.sandbox.create_sandbox_announcement",
            SandboxCreateAnnouncementRequest(
                announcement_id=announcement_id,
                barcode=barcode,
                sender=sender,
                receiver=receiver,
                announcement_type=announcement_type,
                date=date,
                packages=packages,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )

    def get_sandbox_announcement_event(
        self, *, announcement_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getAnnouncementEvent",
            "orders.sandbox.get_sandbox_announcement_event",
            SandboxGetAnnouncementEventRequest(announcement_id=announcement_id),
            idempotency_key=idempotency_key,
        )

    def get_sandbox_change_parcel_info(
        self, *, application_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getChangeParcelInfo",
            "orders.sandbox.get_sandbox_change_parcel_info",
            GetChangeParcelInfoRequest(application_id=application_id),
            idempotency_key=idempotency_key,
        )

    def get_sandbox_parcel_info(
        self, *, parcel_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getParcelInfo",
            "orders.sandbox.get_sandbox_parcel_info",
            GetSandboxParcelInfoRequest(parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )

    def get_sandbox_registered_parcel_id(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v1/getRegisteredParcelID",
            "orders.sandbox.get_sandbox_registered_parcel_id",
            GetRegisteredParcelIdRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )

    def create_parcel(
        self,
        *,
        order_id: str,
        parcel_id: str,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self._post(
            "/delivery-sandbox/v2/createParcel",
            "orders.sandbox.create_parcel",
            DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )

    def _post(
        self,
        path: str,
        operation: str,
        request: CustomAreaScheduleRequest
        | CancelParcelRequest
        | SandboxConfirmationCodeRequest
        | SetOrderPropertiesRequest
        | SetOrderRealAddressRequest
        | DeliveryTrackingRequest
        | ProhibitOrderAcceptanceRequest
        | AddSortingCentersRequest
        | DeliveryAnnouncementRequest
        | SandboxAreasRequest
        | TaggedSortingCentersRequest
        | AddTerminalsRequest
        | UpdateTermsRequest
        | AddTariffV2Request
        | SandboxCancelAnnouncementRequest
        | CancelSandboxParcelRequest
        | ChangeParcelRequest
        | SandboxCreateAnnouncementRequest
        | SandboxGetAnnouncementEventRequest
        | GetChangeParcelInfoRequest
        | GetSandboxParcelInfoRequest
        | GetRegisteredParcelIdRequest
        | DeliveryParcelRequest,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        return self.transport.request_public_model(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=idempotency_key is not None),
            mapper=map_delivery_entity,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class DeliveryTasksClient:
    """Получает статус задач delivery API."""

    transport: Transport

    def get_task(self, *, task_id: str) -> DeliveryTaskInfo:
        return self.transport.request_public_model(
            "GET",
            f"/delivery-sandbox/tasks/{task_id}",
            context=RequestContext("orders.delivery_task.get_task", allow_retry=True),
            mapper=map_delivery_task,
        )


@dataclass(slots=True, frozen=True)
class StockManagementClient:
    """Выполняет операции управления остатками."""

    transport: Transport

    def get_info(
        self, *, item_ids: list[int], idempotency_key: str | None = None
    ) -> StockInfoResult:
        return self.transport.request_public_model(
            "POST",
            "/stock-management/1/info",
            context=RequestContext("orders.stock.get_info", allow_retry=idempotency_key is not None),
            mapper=map_stock_info,
            json_body=StockInfoRequest(item_ids=item_ids).to_payload(),
            idempotency_key=idempotency_key,
        )

    def update_stocks(
        self, *, stocks: list[StockUpdateEntry], idempotency_key: str | None = None
    ) -> StockUpdateResult:
        return self.transport.request_public_model(
            "PUT",
            "/stock-management/1/stocks",
            context=RequestContext(
                "orders.stock.update_stocks",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_stock_update,
            json_body=StockUpdateRequest(stocks=stocks).to_payload(),
            idempotency_key=idempotency_key,
        )


__all__ = (
    "DeliveryClient",
    "DeliveryTasksClient",
    "LabelsClient",
    "OrdersClient",
    "SandboxDeliveryClient",
    "StockManagementClient",
)
