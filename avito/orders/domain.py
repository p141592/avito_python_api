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
from avito.orders.enums import TrackingAvitoEventType, TrackingAvitoStatus
from avito.orders.models import (
    CancelSandboxParcelOptions,
    ChangeParcelApplication,
    ChangeParcelOptions,
    CourierRangesResult,
    CustomAreaScheduleEntry,
    DeliveryDirection,
    DeliveryEntityResult,
    DeliverySortingCentersResult,
    DeliveryTariffZone,
    DeliveryTaskInfo,
    DeliveryTermsZone,
    DeliveryTrackingOptions,
    LabelPdfResult,
    LabelTaskResult,
    OrderActionResult,
    OrderDeliveryProperties,
    OrdersResult,
    RealAddress,
    SandboxAnnouncementPackage,
    SandboxAnnouncementParticipant,
    SandboxArea,
    SandboxCancelAnnouncementOptions,
    SandboxCreateAnnouncementOptions,
    SortingCenterUpload,
    StockInfoResult,
    StockUpdateEntry,
    StockUpdateResult,
    TaggedSortingCenter,
    TerminalUpload,
)


@dataclass(slots=True, frozen=True)
class Order(DomainObject):
    """Доменный объект заказа."""

    user_id: int | str | None = None

    def list(self) -> OrdersResult:
        """Выполняет публичную операцию `Order.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).list_orders()

    def update_markings(
        self, *, order_id: str, codes: Sequence[str], idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.update_markings` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).update_markings(
            order_id=order_id,
            codes=list(codes),
            idempotency_key=idempotency_key,
        )

    def accept_return_order(
        self, *, order_id: str, postal_office_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.accept_return_order` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).accept_return_order(
            order_id=order_id,
            postal_office_id=postal_office_id,
            idempotency_key=idempotency_key,
        )

    def apply(
        self, *, order_id: str, transition: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.apply` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).apply_transition(
            order_id=order_id,
            transition=transition,
            idempotency_key=idempotency_key,
        )

    def check_confirmation_code(
        self, *, order_id: str, code: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.check_confirmation_code` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).check_confirmation_code(
            order_id=order_id,
            code=code,
            idempotency_key=idempotency_key,
        )

    def set_cnc_details(
        self, *, order_id: str, pickup_point_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.set_cnc_details` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).set_cnc_details(
            order_id=order_id,
            pickup_point_id=pickup_point_id,
            idempotency_key=idempotency_key,
        )

    def get_courier_delivery_range(self) -> CourierRangesResult:
        """Выполняет публичную операцию `Order.get_courier_delivery_range` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).get_courier_delivery_range()

    def set_courier_delivery_range(
        self, *, order_id: str, interval_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.set_courier_delivery_range` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).set_courier_delivery_range(
            order_id=order_id,
            interval_id=interval_id,
            idempotency_key=idempotency_key,
        )

    def update_tracking_number(
        self, *, order_id: str, tracking_number: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.update_tracking_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return OrdersClient(self.transport).set_tracking_number(
            order_id=order_id,
            tracking_number=tracking_number,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class OrderLabel(DomainObject):
    """Доменный объект генерации и загрузки этикеток."""

    task_id: int | str | None = None
    user_id: int | str | None = None

    def create(
        self,
        *,
        order_ids: Sequence[str],
        extended: bool = False,
        idempotency_key: str | None = None,
    ) -> LabelTaskResult:
        """Выполняет публичную операцию `OrderLabel.create` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        client = LabelsClient(self.transport)
        if extended:
            return client.create_generate_labels_extended(
                order_ids=list(order_ids),
                idempotency_key=idempotency_key,
            )
        return client.create_generate_labels(
            order_ids=list(order_ids),
            idempotency_key=idempotency_key,
        )

    def download(self, *, task_id: str | None = None) -> LabelPdfResult:
        """Выполняет публичную операцию `OrderLabel.download` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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

    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.create_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DeliveryClient(self.transport).create_announcement(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )

    def delete(self, *, order_id: str, idempotency_key: str | None = None) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.delete` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DeliveryClient(self.transport).cancel_announcement(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )

    def create(
        self,
        *,
        order_id: str,
        parcel_id: str,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.create` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DeliveryClient(self.transport).create_parcel(
            order_id=order_id,
            parcel_id=parcel_id,
            idempotency_key=idempotency_key,
        )

    def update_change_parcels(
        self, *, parcel_ids: Sequence[str], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.update_change_parcels` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DeliveryClient(self.transport).update_change_parcels(
            parcel_ids=list(parcel_ids),
            idempotency_key=idempotency_key,
        )

    def create_change_parcel_result(
        self, *, parcel_id: str, result: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.create_change_parcel_result` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DeliveryClient(self.transport).change_parcel_result(
            parcel_id=parcel_id,
            result=result,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class SandboxDelivery(DomainObject):
    """Доменный объект sandbox API доставки."""

    user_id: int | str | None = None

    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.create_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).create_announcement(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )

    def track_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.track_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).track_announcement(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )

    def update_custom_area_schedule(
        self, *, items: Sequence[CustomAreaScheduleEntry], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.update_custom_area_schedule` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).update_custom_area_schedule(
            items=list(items),
            idempotency_key=idempotency_key,
        )

    def cancel_parcel(
        self, *, parcel_id: str, actor: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.cancel_parcel` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).cancel_parcel(
            parcel_id=parcel_id,
            actor=actor,
            idempotency_key=idempotency_key,
        )

    def check_confirmation_code(
        self, *, parcel_id: str, confirm_code: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.check_confirmation_code` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).check_confirmation_code(
            parcel_id=parcel_id,
            confirm_code=confirm_code,
            idempotency_key=idempotency_key,
        )

    def set_order_properties(
        self,
        *,
        order_id: str,
        properties: OrderDeliveryProperties,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.set_order_properties` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).set_order_properties(
            order_id=order_id,
            properties=properties,
            idempotency_key=idempotency_key,
        )

    def set_order_real_address(
        self, *, order_id: str, address: RealAddress, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.set_order_real_address` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).set_order_real_address(
            order_id=order_id,
            address=address,
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
        """Выполняет публичную операцию `SandboxDelivery.tracking` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).tracking(
            order_id=order_id,
            avito_status=avito_status,
            avito_event_type=avito_event_type,
            provider_event_code=provider_event_code,
            date=date,
            location=location,
            comment=comment,
            options=options,
            idempotency_key=idempotency_key,
        )

    def prohibit_order_acceptance(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.prohibit_order_acceptance` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).prohibit_order_acceptance(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )

    def list_sorting_center(self) -> DeliverySortingCentersResult:
        """Выполняет публичную операцию `SandboxDelivery.list_sorting_center` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).list_sorting_center()

    def add_sorting_center(
        self, *, items: Sequence[SortingCenterUpload], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_sorting_center` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).add_sorting_center(
            items=list(items),
            idempotency_key=idempotency_key,
        )

    def add_areas(
        self,
        *,
        tariff_id: str,
        areas: Sequence[SandboxArea],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_areas` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).add_areas(
            tariff_id=tariff_id,
            areas=list(areas),
            idempotency_key=idempotency_key,
        )

    def add_tags_to_sorting_center(
        self,
        *,
        tariff_id: str,
        items: Sequence[TaggedSortingCenter],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_tags_to_sorting_center` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).add_tags_to_sorting_center(
            tariff_id=tariff_id,
            items=list(items),
            idempotency_key=idempotency_key,
        )

    def add_terminals(
        self,
        *,
        tariff_id: str,
        items: Sequence[TerminalUpload],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_terminals` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).add_terminals(
            tariff_id=tariff_id,
            items=list(items),
            idempotency_key=idempotency_key,
        )

    def update_terms(
        self,
        *,
        tariff_id: str,
        items: Sequence[DeliveryTermsZone],
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.update_terms` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).update_terms(
            tariff_id=tariff_id,
            items=list(items),
            idempotency_key=idempotency_key,
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
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_tariff` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).add_tariff(
            name=name,
            delivery_provider_tariff_id=delivery_provider_tariff_id,
            directions=list(directions),
            tariff_zones=list(tariff_zones),
            terms_zones=list(terms_zones),
            tariff_type=tariff_type,
            idempotency_key=idempotency_key,
        )

    def create_parcel(
        self,
        *,
        order_id: str,
        parcel_id: str,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.create_parcel` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).create_parcel(
            order_id=order_id,
            parcel_id=parcel_id,
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
        """Выполняет публичную операцию `SandboxDelivery.cancel_sandbox_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).cancel_sandbox_announcement(
            announcement_id=announcement_id,
            date=date,
            options=options,
            idempotency_key=idempotency_key,
        )

    def cancel_sandbox_parcel(
        self,
        *,
        parcel_id: str,
        options: CancelSandboxParcelOptions | None = None,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.cancel_sandbox_parcel` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).cancel_sandbox_parcel(
            parcel_id=parcel_id,
            options=options,
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
        """Выполняет публичную операцию `SandboxDelivery.change_sandbox_parcel` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).change_sandbox_parcel(
            type=type,
            parcel_id=parcel_id,
            application=application,
            options=options,
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
        packages: Sequence[SandboxAnnouncementPackage],
        options: SandboxCreateAnnouncementOptions,
        idempotency_key: str | None = None,
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.create_sandbox_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).create_sandbox_announcement(
            announcement_id=announcement_id,
            barcode=barcode,
            sender=sender,
            receiver=receiver,
            announcement_type=announcement_type,
            date=date,
            packages=list(packages),
            options=options,
            idempotency_key=idempotency_key,
        )

    def get_sandbox_announcement_event(
        self, *, announcement_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_announcement_event` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).get_sandbox_announcement_event(
            announcement_id=announcement_id,
            idempotency_key=idempotency_key,
        )

    def get_sandbox_change_parcel_info(
        self, *, application_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_change_parcel_info` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).get_sandbox_change_parcel_info(
            application_id=application_id,
            idempotency_key=idempotency_key,
        )

    def get_sandbox_parcel_info(
        self, *, parcel_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_parcel_info` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).get_sandbox_parcel_info(
            parcel_id=parcel_id,
            idempotency_key=idempotency_key,
        )

    def get_sandbox_registered_parcel_id(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_registered_parcel_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SandboxDeliveryClient(self.transport).get_sandbox_registered_parcel_id(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class DeliveryTask(DomainObject):
    """Доменный объект задачи доставки."""

    task_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, task_id: str | None = None) -> DeliveryTaskInfo:
        """Выполняет публичную операцию `DeliveryTask.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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
        """Выполняет публичную операцию `Stock.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return StockManagementClient(self.transport).get_info(item_ids=list(item_ids))

    def update(
        self,
        *,
        stocks: Sequence[StockUpdateEntry],
        idempotency_key: str | None = None,
    ) -> StockUpdateResult:
        """Выполняет публичную операцию `Stock.update` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return StockManagementClient(self.transport).update_stocks(
            stocks=list(stocks),
            idempotency_key=idempotency_key,
        )


__all__ = (
    "DeliveryOrder",
    "DeliveryTask",
    "Order",
    "OrderLabel",
    "SandboxDelivery",
    "Stock",
)
