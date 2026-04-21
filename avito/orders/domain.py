"""Доменные объекты пакета orders."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.orders.client import (
    DeliveryClient,
    DeliveryTasksClient,
    LabelsClient,
    OrdersClient,
    SandboxDeliveryClient,
    StockManagementClient,
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
class Order(DomainObject):
    """Доменный объект заказа."""

    user_id: int | str | None = None

    def list(self) -> OrdersResult:
        return OrdersClient(self.transport).list_orders()

    def update_markings(self, *, order_id: str, codes: Sequence[str]) -> OrderActionResult:
        return OrdersClient(self.transport).update_markings(
            OrderMarkingsRequest(order_id=order_id, codes=list(codes))
        )

    def accept_return_order(self, *, order_id: str, postal_office_id: str) -> OrderActionResult:
        return OrdersClient(self.transport).accept_return_order(
            OrderAcceptReturnRequest(order_id=order_id, postal_office_id=postal_office_id)
        )

    def apply(self, *, order_id: str, transition: str) -> OrderActionResult:
        return OrdersClient(self.transport).apply_transition(
            OrderApplyTransitionRequest(order_id=order_id, transition=transition)
        )

    def check_confirmation_code(self, *, order_id: str, code: str) -> OrderActionResult:
        return OrdersClient(self.transport).check_confirmation_code(
            OrderConfirmationCodeRequest(order_id=order_id, code=code)
        )

    def set_cnc_details(self, *, order_id: str, pickup_point_id: str) -> OrderActionResult:
        return OrdersClient(self.transport).set_cnc_details(
            OrderCncDetailsRequest(order_id=order_id, pickup_point_id=pickup_point_id)
        )

    def get_courier_delivery_range(self) -> CourierRangesResult:
        return OrdersClient(self.transport).get_courier_delivery_range()

    def set_courier_delivery_range(self, *, order_id: str, interval_id: str) -> OrderActionResult:
        return OrdersClient(self.transport).set_courier_delivery_range(
            OrderCourierRangeRequest(order_id=order_id, interval_id=interval_id)
        )

    def update_tracking_number(self, *, order_id: str, tracking_number: str) -> OrderActionResult:
        return OrdersClient(self.transport).set_tracking_number(
            OrderTrackingNumberRequest(order_id=order_id, tracking_number=tracking_number)
        )


@dataclass(slots=True, frozen=True)
class OrderLabel(DomainObject):
    """Доменный объект генерации и загрузки этикеток."""

    task_id: int | str | None = None
    user_id: int | str | None = None

    def create(self, *, order_ids: Sequence[str], extended: bool = False) -> LabelTaskResult:
        client = LabelsClient(self.transport)
        request = OrderLabelsRequest(order_ids=list(order_ids))
        if extended:
            return client.create_generate_labels_extended(request)
        return client.create_generate_labels(request)

    def download(self, *, task_id: str | None = None) -> LabelPdfResult:
        resolved_task_id = task_id or self._require_task_id()
        return LabelsClient(self.transport).get_download_label(task_id=resolved_task_id)

    def _require_task_id(self) -> str:
        if self.task_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.task_id)


@dataclass(slots=True, frozen=True)
class DeliveryOrder(DomainObject):
    """Доменный объект production API доставки."""

    user_id: int | str | None = None

    def create_announcement(self, *, order_id: str) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_announcement(
            DeliveryAnnouncementRequest(order_id=order_id)
        )

    def delete(self, *, order_id: str) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).cancel_announcement(
            DeliveryAnnouncementRequest(order_id=order_id)
        )

    def create(self, *, order_id: str, parcel_id: str) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).create_parcel(
            DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id)
        )

    def update_change_parcels(self, *, parcel_ids: Sequence[str]) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).update_change_parcels(
            DeliveryParcelIdsRequest(parcel_ids=list(parcel_ids))
        )

    def create_change_parcel_result(self, *, parcel_id: str, result: str) -> DeliveryEntityResult:
        return DeliveryClient(self.transport).change_parcel_result(
            DeliveryParcelResultRequest(parcel_id=parcel_id, result=result)
        )


@dataclass(slots=True, frozen=True)
class SandboxDelivery(DomainObject):
    """Доменный объект sandbox API доставки."""

    user_id: int | str | None = None

    def create_announcement(self, *, order_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_announcement(
            DeliveryAnnouncementRequest(order_id=order_id)
        )

    def track_announcement(self, *, order_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).track_announcement(
            DeliveryAnnouncementRequest(order_id=order_id)
        )

    def update_custom_area_schedule(
        self, *, items: Sequence[CustomAreaScheduleEntry]
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_custom_area_schedule(
            CustomAreaScheduleRequest(items=list(items))
        )

    def cancel_parcel(self, *, parcel_id: str, actor: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).cancel_parcel(
            CancelParcelRequest(parcel_id=parcel_id, actor=actor)
        )

    def check_confirmation_code(self, *, parcel_id: str, confirm_code: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).check_confirmation_code(
            SandboxConfirmationCodeRequest(parcel_id=parcel_id, confirm_code=confirm_code)
        )

    def set_order_properties(
        self, *, order_id: str, properties: OrderDeliveryProperties
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_properties(
            SetOrderPropertiesRequest(order_id=order_id, properties=properties)
        )

    def set_order_real_address(self, *, order_id: str, address: RealAddress) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).set_order_real_address(
            SetOrderRealAddressRequest(order_id=order_id, address=address)
        )

    def tracking(
        self,
        *,
        order_id: str,
        avito_status: str,
        avito_event_type: str,
        provider_event_code: str,
        date: str,
        location: str,
        comment: str | None = None,
        options: DeliveryTrackingOptions | None = None,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).tracking(
            DeliveryTrackingRequest(
                order_id=order_id,
                avito_status=avito_status,
                avito_event_type=avito_event_type,
                provider_event_code=provider_event_code,
                date=date,
                location=location,
                comment=comment,
                options=options,
            )
        )

    def prohibit_order_acceptance(self, *, order_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).prohibit_order_acceptance(
            ProhibitOrderAcceptanceRequest(order_id=order_id)
        )

    def list_sorting_center(self) -> DeliverySortingCentersResult:
        return SandboxDeliveryClient(self.transport).list_sorting_center()

    def add_sorting_center(self, *, items: Sequence[SortingCenterUpload]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_sorting_center(
            AddSortingCentersRequest(items=list(items))
        )

    def add_areas(self, *, tariff_id: str, areas: Sequence[SandboxArea]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_areas(
            tariff_id=tariff_id,
            request=SandboxAreasRequest(areas=list(areas)),
        )

    def add_tags_to_sorting_center(
        self, *, tariff_id: str, items: Sequence[TaggedSortingCenter]
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tags_to_sorting_center(
            tariff_id=tariff_id,
            request=TaggedSortingCentersRequest(items=list(items)),
        )

    def add_terminals(
        self, *, tariff_id: str, items: Sequence[TerminalUpload]
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_terminals(
            tariff_id=tariff_id,
            request=AddTerminalsRequest(items=list(items)),
        )

    def update_terms(self, *, tariff_id: str, items: Sequence[DeliveryTermsZone]) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).update_terms(
            tariff_id=tariff_id,
            request=UpdateTermsRequest(items=list(items)),
        )

    def add_tariff(
        self,
        *,
        name: str,
        delivery_provider_tariff_id: str,
        directions: Sequence[DeliveryDirection],
        tariff_zones: Sequence[DeliveryTariffZone],
        terms_zones: Sequence[DeliveryTermsZone],
        tariff_type: str | None = None,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).add_tariff(
            AddTariffV2Request(
                name=name,
                delivery_provider_tariff_id=delivery_provider_tariff_id,
                directions=list(directions),
                tariff_zones=list(tariff_zones),
                terms_zones=list(terms_zones),
                tariff_type=tariff_type,
            )
        )

    def create_parcel(self, *, order_id: str, parcel_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_parcel(
            DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id)
        )

    def cancel_sandbox_announcement(
        self,
        *,
        announcement_id: str,
        date: str,
        options: SandboxCancelAnnouncementOptions,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).cancel_sandbox_announcement(
            SandboxCancelAnnouncementRequest(
                announcement_id=announcement_id,
                date=date,
                options=options,
            )
        )

    def cancel_sandbox_parcel(
        self,
        *,
        parcel_id: str,
        options: CancelSandboxParcelOptions | None = None,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).cancel_sandbox_parcel(
            CancelSandboxParcelRequest(parcel_id=parcel_id, options=options)
        )

    def change_sandbox_parcel(
        self,
        *,
        type: str,
        parcel_id: str,
        application: ChangeParcelApplication | None = None,
        options: ChangeParcelOptions | None = None,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).change_sandbox_parcel(
            ChangeParcelRequest(
                type=type,
                parcel_id=parcel_id,
                application=application,
                options=options,
            )
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
        packages: Sequence[SandboxAnnouncementPackage],
        options: SandboxCreateAnnouncementOptions,
    ) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).create_sandbox_announcement(
            SandboxCreateAnnouncementRequest(
                announcement_id=announcement_id,
                barcode=barcode,
                sender=sender,
                receiver=receiver,
                announcement_type=announcement_type,
                date=date,
                packages=list(packages),
                options=options,
            )
        )

    def get_sandbox_announcement_event(self, *, announcement_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).get_sandbox_announcement_event(
            SandboxGetAnnouncementEventRequest(announcement_id=announcement_id)
        )

    def get_sandbox_change_parcel_info(self, *, application_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).get_sandbox_change_parcel_info(
            GetChangeParcelInfoRequest(application_id=application_id)
        )

    def get_sandbox_parcel_info(self, *, parcel_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).get_sandbox_parcel_info(
            GetSandboxParcelInfoRequest(parcel_id=parcel_id)
        )

    def get_sandbox_registered_parcel_id(self, *, order_id: str) -> DeliveryEntityResult:
        return SandboxDeliveryClient(self.transport).get_sandbox_registered_parcel_id(
            GetRegisteredParcelIdRequest(order_id=order_id)
        )


@dataclass(slots=True, frozen=True)
class DeliveryTask(DomainObject):
    """Доменный объект задачи доставки."""

    task_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, task_id: str | None = None) -> DeliveryTaskInfo:
        resolved_task_id = task_id or self._require_task_id()
        return DeliveryTasksClient(self.transport).get_task(task_id=resolved_task_id)

    def _require_task_id(self) -> str:
        if self.task_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.task_id)


@dataclass(slots=True, frozen=True)
class Stock(DomainObject):
    """Доменный объект управления остатками."""

    user_id: int | str | None = None

    def get(self, *, item_ids: Sequence[int]) -> StockInfoResult:
        return StockManagementClient(self.transport).get_info(
            StockInfoRequest(item_ids=list(item_ids))
        )

    def update(self, *, stocks: Sequence[StockUpdateEntry]) -> StockUpdateResult:
        return StockManagementClient(self.transport).update_stocks(
            StockUpdateRequest(stocks=list(stocks))
        )


__all__ = (
    "DeliveryOrder",
    "DeliveryTask",
    "Order",
    "OrderLabel",
    "SandboxDelivery",
    "Stock",
)
