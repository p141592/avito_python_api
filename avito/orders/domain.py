"""Доменные объекты пакета orders."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from avito.core import BinaryResponse, ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
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
    TrackingAvitoEventType,
    TrackingAvitoStatus,
    UpdateTermsRequest,
)
from avito.orders.operations import (
    ACCEPT_RETURN_ORDER,
    APPLY_TRANSITION,
    CHECK_CONFIRMATION_CODE,
    CREATE_LABELS,
    CREATE_LABELS_EXTENDED,
    DELIVERY_CANCEL_ANNOUNCEMENT,
    DELIVERY_CHANGE_PARCEL_RESULT,
    DELIVERY_CREATE_ANNOUNCEMENT,
    DELIVERY_CREATE_PARCEL,
    DELIVERY_UPDATE_CHANGE_PARCELS,
    DOWNLOAD_LABEL,
    GET_COURIER_DELIVERY_RANGE,
    GET_DELIVERY_TASK,
    GET_STOCK_INFO,
    LIST_ORDERS,
    SANDBOX_ADD_AREAS,
    SANDBOX_ADD_SORTING_CENTER,
    SANDBOX_ADD_TAGS_TO_SORTING_CENTER,
    SANDBOX_ADD_TARIFF,
    SANDBOX_ADD_TERMINALS,
    SANDBOX_CANCEL_PARCEL,
    SANDBOX_CANCEL_SANDBOX_ANNOUNCEMENT,
    SANDBOX_CANCEL_SANDBOX_PARCEL,
    SANDBOX_CHANGE_SANDBOX_PARCEL,
    SANDBOX_CHECK_CONFIRMATION_CODE,
    SANDBOX_CREATE_ANNOUNCEMENT,
    SANDBOX_CREATE_PARCEL,
    SANDBOX_CREATE_SANDBOX_ANNOUNCEMENT,
    SANDBOX_GET_ANNOUNCEMENT_EVENT,
    SANDBOX_GET_CHANGE_PARCEL_INFO,
    SANDBOX_GET_PARCEL_INFO,
    SANDBOX_GET_REGISTERED_PARCEL_ID,
    SANDBOX_LIST_SORTING_CENTER,
    SANDBOX_PROHIBIT_ORDER_ACCEPTANCE,
    SANDBOX_SET_ORDER_PROPERTIES,
    SANDBOX_SET_ORDER_REAL_ADDRESS,
    SANDBOX_TRACK_ANNOUNCEMENT,
    SANDBOX_TRACKING,
    SANDBOX_UPDATE_CUSTOM_AREA_SCHEDULE,
    SANDBOX_UPDATE_TERMS,
    SET_CNC_DETAILS,
    SET_COURIER_DELIVERY_RANGE,
    SET_TRACKING_NUMBER,
    UPDATE_MARKINGS,
    UPDATE_STOCKS,
)


@dataclass(slots=True, frozen=True)
class Order(DomainObject):
    """Доменный объект заказа."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "order"

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/order-management/1/orders",
        spec="Управлениезаказами.json",
        operation_id="getOrders",
    )
    def list(self) -> OrdersResult:
        """Выполняет публичную операцию `Order.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(LIST_ORDERS)  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/markings",
        spec="Управлениезаказами.json",
        operation_id="markings",
        method_args={"order_id": "body.markings", "codes": "body.markings"},
    )
    def update_markings(
        self, *, order_id: str, codes: Sequence[str], idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.update_markings` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            UPDATE_MARKINGS,
            request=OrderMarkingsRequest(order_id=order_id, codes=list(codes)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/acceptReturnOrder",
        spec="Управлениезаказами.json",
        operation_id="acceptReturnOrder",
        method_args={"order_id": "body.order_id", "postal_office_id": "body.terminal_number"},
    )
    def accept_return_order(
        self, *, order_id: str, postal_office_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.accept_return_order` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            ACCEPT_RETURN_ORDER,
            request=OrderAcceptReturnRequest(
                order_id=order_id,
                postal_office_id=postal_office_id,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/applyTransition",
        spec="Управлениезаказами.json",
        operation_id="applyTransition",
        method_args={"order_id": "body.order_id", "transition": "body.transition"},
    )
    def apply(
        self, *, order_id: str, transition: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.apply` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            APPLY_TRANSITION,
            request=OrderApplyTransitionRequest(order_id=order_id, transition=transition),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/checkConfirmationCode",
        spec="Управлениезаказами.json",
        operation_id="checkConfirmationCode",
        method_args={"order_id": "body.parcel_id", "code": "body.confirm_code"},
    )
    def check_confirmation_code(
        self, *, order_id: str, code: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.check_confirmation_code` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CHECK_CONFIRMATION_CODE,
            request=OrderConfirmationCodeRequest(order_id=order_id, code=code),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/cncSetDetails",
        spec="Управлениезаказами.json",
        operation_id="cncSetDetails",
        method_args={"order_id": "body.id", "pickup_point_id": "body.marketplace_id"},
    )
    def set_cnc_details(
        self, *, order_id: str, pickup_point_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.set_cnc_details` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SET_CNC_DETAILS,
            request=OrderCncDetailsRequest(order_id=order_id, pickup_point_id=pickup_point_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/order-management/1/order/getCourierDeliveryRange",
        spec="Управлениезаказами.json",
        operation_id="getCourierDeliveryRange",
    )
    def get_courier_delivery_range(self) -> CourierRangesResult:
        """Выполняет публичную операцию `Order.get_courier_delivery_range` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_COURIER_DELIVERY_RANGE,
            query={"orderId": "order-1"},
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/setCourierDeliveryRange",
        spec="Управлениезаказами.json",
        operation_id="setCourierDeliveryRange",
        method_args={"order_id": "body.order_id", "interval_id": "body.interval_type"},
    )
    def set_courier_delivery_range(
        self, *, order_id: str, interval_id: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.set_courier_delivery_range` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SET_COURIER_DELIVERY_RANGE,
            request=OrderCourierRangeRequest(order_id=order_id, interval_id=interval_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/order/setTrackingNumber",
        spec="Управлениезаказами.json",
        operation_id="setOrderTrackingNumber",
        method_args={"order_id": "body.order_id", "tracking_number": "body.tracking_number"},
    )
    def update_tracking_number(
        self, *, order_id: str, tracking_number: str, idempotency_key: str | None = None
    ) -> OrderActionResult:
        """Выполняет публичную операцию `Order.update_tracking_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SET_TRACKING_NUMBER,
            request=OrderTrackingNumberRequest(
                order_id=order_id,
                tracking_number=tracking_number,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]


@dataclass(slots=True, frozen=True)
class OrderLabel(DomainObject):
    """Доменный объект генерации и загрузки этикеток."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "order_label"
    __sdk_factory_args__ = {"task_id": "path.task_id"}

    task_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/order-management/1/orders/labels",
        spec="Управлениезаказами.json",
        operation_id="generateLabels",
        method_args={"order_ids": "body.order_ids"},
    )
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

        if extended:
            return self.create_extended(order_ids=order_ids, idempotency_key=idempotency_key)
        return self._execute(
            CREATE_LABELS,
            request=OrderLabelsRequest(order_ids=list(order_ids)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/order-management/1/orders/labels/extended",
        spec="Управлениезаказами.json",
        operation_id="generateLabelsExtended",
        method_args={"order_ids": "body.order_ids"},
    )
    def create_extended(
        self,
        *,
        order_ids: Sequence[str],
        idempotency_key: str | None = None,
    ) -> LabelTaskResult:
        """Запускает генерацию расширенных этикеток и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_LABELS_EXTENDED,
            request=OrderLabelsRequest(order_ids=list(order_ids)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/order-management/1/orders/labels/{taskID}/download",
        spec="Управлениезаказами.json",
        operation_id="downloadLabel",
    )
    def download(self, *, task_id: str | None = None) -> LabelPdfResult:
        """Выполняет публичную операцию `OrderLabel.download` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_task_id = task_id or self._require_task_id()
        binary = self._execute(
            DOWNLOAD_LABEL,
            path_params={"taskID": resolved_task_id},
        )
        return LabelPdfResult(binary=cast(BinaryResponse, binary))

    def _require_task_id(self) -> str:
        if self.task_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.task_id)


@dataclass(slots=True, frozen=True)
class DeliveryOrder(DomainObject):
    """Доменный объект production API доставки."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "delivery_order"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/createAnnouncement",
        spec="Доставка.json",
        operation_id="CreateAnnouncement3PL",
        method_args={"order_id": "body.announcement_id"},
    )
    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.create_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELIVERY_CREATE_ANNOUNCEMENT,
            request=DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/cancelAnnouncement",
        spec="Доставка.json",
        operation_id="CancelAnnouncement3PL",
        method_args={"order_id": "body.announcement_id"},
    )
    def delete(self, *, order_id: str, idempotency_key: str | None = None) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.delete` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELIVERY_CANCEL_ANNOUNCEMENT,
            request=DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/createParcel",
        spec="Доставка.json",
        operation_id="createParcel",
        method_args={"order_id": "body.order_id", "parcel_id": "body.parcel_id"},
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

        return self._execute(
            DELIVERY_CREATE_PARCEL,
            request=DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/sandbox/changeParcels",
        spec="Доставка.json",
        operation_id="ChangeParcels",
        method_args={"parcel_ids": "body.applications"},
    )
    def update_change_parcels(
        self, *, parcel_ids: Sequence[str], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.update_change_parcels` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELIVERY_UPDATE_CHANGE_PARCELS,
            request=DeliveryParcelIdsRequest(parcel_ids=list(parcel_ids)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery/order/changeParcelResult",
        spec="Доставка.json",
        operation_id="ChangeParcelResult",
        method_args={"parcel_id": "body.id", "result": "body.status"},
    )
    def create_change_parcel_result(
        self, *, parcel_id: str, result: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `DeliveryOrder.create_change_parcel_result` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELIVERY_CHANGE_PARCEL_RESULT,
            request=DeliveryParcelResultRequest(parcel_id=parcel_id, result=result),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]


@dataclass(slots=True, frozen=True)
class SandboxDelivery(DomainObject):
    """Доменный объект sandbox API доставки."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "sandbox_delivery"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/delivery-sandbox/announcements/create",
        spec="Доставка.json",
        operation_id="CreateAnnouncement",
        method_args={"order_id": "body.announcement_id"},
    )
    def create_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.create_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_CREATE_ANNOUNCEMENT,
            request=DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/announcements/track",
        spec="Доставка.json",
        operation_id="TrackAnnouncement",
        method_args={"order_id": "body.announcement_id"},
    )
    def track_announcement(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.track_announcement` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_TRACK_ANNOUNCEMENT,
            request=DeliveryAnnouncementRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/areas/custom-schedule",
        spec="Доставка.json",
        operation_id="customAreaSchedule",
        method_args={"items": "body"},
    )
    def update_custom_area_schedule(
        self, *, items: Sequence[CustomAreaScheduleEntry], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.update_custom_area_schedule` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_UPDATE_CUSTOM_AREA_SCHEDULE,
            request=CustomAreaScheduleRequest(items=list(items)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/cancelParcel",
        spec="Доставка.json",
        operation_id="cancelParcel",
        method_args={"parcel_id": "body.parcel_id", "actor": "body.actor"},
    )
    def cancel_parcel(
        self, *, parcel_id: str, actor: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.cancel_parcel` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_CANCEL_PARCEL,
            request=CancelParcelRequest(parcel_id=parcel_id, actor=actor),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/order/checkConfirmationCode",
        spec="Доставка.json",
        operation_id="checkConfirmationCode",
        method_args={"parcel_id": "body.parcel_id", "confirm_code": "body.confirm_code"},
    )
    def check_confirmation_code(
        self, *, parcel_id: str, confirm_code: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.check_confirmation_code` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_CHECK_CONFIRMATION_CODE,
            request=SandboxConfirmationCodeRequest(
                parcel_id=parcel_id,
                confirm_code=confirm_code,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/order/properties",
        spec="Доставка.json",
        operation_id="setOrderProperties",
        method_args={"order_id": "body.order_id", "properties": "body.properties"},
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

        return self._execute(
            SANDBOX_SET_ORDER_PROPERTIES,
            request=SetOrderPropertiesRequest(order_id=order_id, properties=properties),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/order/realAddress",
        spec="Доставка.json",
        operation_id="setOrderRealAddress",
        method_args={"order_id": "body.order_id", "address": "body.address"},
    )
    def set_order_real_address(
        self, *, order_id: str, address: RealAddress, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.set_order_real_address` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_SET_ORDER_REAL_ADDRESS,
            request=SetOrderRealAddressRequest(order_id=order_id, address=address),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/order/tracking",
        spec="Доставка.json",
        operation_id="tracking",
        method_args={
            "order_id": "body.order_id",
            "avito_status": "body.avito_status",
            "avito_event_type": "body.avito_event_type",
            "provider_event_code": "body.provider_event_code",
            "date": "body.date",
            "location": "body.location",
        },
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

        return self._execute(
            SANDBOX_TRACKING,
            request=DeliveryTrackingRequest(
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
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/prohibitOrderAcceptance",
        spec="Доставка.json",
        operation_id="prohibitOrderAcceptance",
        method_args={"order_id": "body.order_id"},
    )
    def prohibit_order_acceptance(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.prohibit_order_acceptance` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_PROHIBIT_ORDER_ACCEPTANCE,
            request=ProhibitOrderAcceptanceRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/delivery-sandbox/sorting-center",
        spec="Доставка.json",
        operation_id="GetSortingCenter",
    )
    def list_sorting_center(self) -> DeliverySortingCentersResult:
        """Выполняет публичную операцию `SandboxDelivery.list_sorting_center` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_LIST_SORTING_CENTER,
            query={"deliveryProviders": "pochta"},
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffs/sorting-center",
        spec="Доставка.json",
        operation_id="AddSortingCenter",
        method_args={"items": "body"},
    )
    def add_sorting_center(
        self, *, items: Sequence[SortingCenterUpload], idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.add_sorting_center` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_ADD_SORTING_CENTER,
            request=AddSortingCentersRequest(items=list(items)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffs/{tariff_id}/areas",
        spec="Доставка.json",
        operation_id="AddAreasSandbox",
        method_args={"tariff_id": "path.tariff_id", "areas": "body"},
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

        return self._execute(
            SANDBOX_ADD_AREAS,
            path_params={"tariff_id": tariff_id},
            request=SandboxAreasRequest(areas=list(areas)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers",
        spec="Доставка.json",
        operation_id="AddTagsToSortingCenter",
        method_args={"tariff_id": "path.tariff_id", "items": "body"},
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

        return self._execute(
            SANDBOX_ADD_TAGS_TO_SORTING_CENTER,
            path_params={"tariff_id": tariff_id},
            request=TaggedSortingCentersRequest(items=list(items)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffs/{tariff_id}/terminals",
        spec="Доставка.json",
        operation_id="AddTerminalsSandbox",
        method_args={"tariff_id": "path.tariff_id", "items": "body"},
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

        return self._execute(
            SANDBOX_ADD_TERMINALS,
            path_params={"tariff_id": tariff_id},
            request=AddTerminalsRequest(items=list(items)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffs/{tariff_id}/terms",
        spec="Доставка.json",
        operation_id="UpdateTerms",
        method_args={"tariff_id": "path.tariff_id", "items": "body"},
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

        return self._execute(
            SANDBOX_UPDATE_TERMS,
            path_params={"tariff_id": tariff_id},
            request=UpdateTermsRequest(items=list(items)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/tariffsV2",
        spec="Доставка.json",
        operation_id="AddTariffSandboxV2",
        method_args={
            "name": "body.name",
            "delivery_provider_tariff_id": "body.delivery_provider_tariff_id",
            "directions": "body.directions",
            "tariff_zones": "body.tariff_zones",
            "terms_zones": "body.terms_zones",
        },
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

        return self._execute(
            SANDBOX_ADD_TARIFF,
            request=AddTariffV2Request(
                name=name,
                delivery_provider_tariff_id=delivery_provider_tariff_id,
                directions=list(directions),
                tariff_zones=list(tariff_zones),
                terms_zones=list(terms_zones),
                tariff_type=tariff_type,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v2/createParcel",
        spec="Доставка.json",
        operation_id="CreateSandboxParcelV2",
        method_args={"order_id": "body.items", "parcel_id": "body.items"},
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

        return self._execute(
            SANDBOX_CREATE_PARCEL,
            request=DeliveryParcelRequest(order_id=order_id, parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/cancelAnnouncement",
        spec="Доставка.json",
        operation_id="v1cancelAnnouncement",
        method_args={
            "announcement_id": "body.announcement_id",
            "date": "body.date",
            "options": "body.options",
        },
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

        return self._execute(
            SANDBOX_CANCEL_SANDBOX_ANNOUNCEMENT,
            request=SandboxCancelAnnouncementRequest(
                announcement_id=announcement_id,
                date=date,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/cancelParcel",
        spec="Доставка.json",
        operation_id="v1CancelParcel",
        method_args={"parcel_id": "body.parcel_id"},
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

        return self._execute(
            SANDBOX_CANCEL_SANDBOX_PARCEL,
            request=CancelSandboxParcelRequest(parcel_id=parcel_id, options=options),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/changeParcel",
        spec="Доставка.json",
        operation_id="v1changeParcel",
        method_args={"type": "body.type", "parcel_id": "body.parcel_id"},
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

        return self._execute(
            SANDBOX_CHANGE_SANDBOX_PARCEL,
            request=ChangeParcelRequest(
                type=type,
                parcel_id=parcel_id,
                application=application,
                options=options,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/createAnnouncement",
        spec="Доставка.json",
        operation_id="v1createAnnouncement",
        method_args={
            "announcement_id": "body.announcement_id",
            "barcode": "body.barcode",
            "sender": "body.sender",
            "receiver": "body.receiver",
            "announcement_type": "body.announcement_type",
            "date": "body.date",
            "packages": "body.packages",
            "options": "body.options",
        },
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

        return self._execute(
            SANDBOX_CREATE_SANDBOX_ANNOUNCEMENT,
            request=SandboxCreateAnnouncementRequest(
                announcement_id=announcement_id,
                barcode=barcode,
                sender=sender,
                receiver=receiver,
                announcement_type=announcement_type,
                date=date,
                packages=list(packages),
                options=options,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/getAnnouncementEvent",
        spec="Доставка.json",
        operation_id="v1getAnnouncementEvent",
        method_args={"announcement_id": "body.announcement_id"},
    )
    def get_sandbox_announcement_event(
        self, *, announcement_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_announcement_event` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_GET_ANNOUNCEMENT_EVENT,
            request=SandboxGetAnnouncementEventRequest(announcement_id=announcement_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/getChangeParcelInfo",
        spec="Доставка.json",
        operation_id="v1getChangeParcelInfo",
        method_args={"application_id": "body.application_id"},
    )
    def get_sandbox_change_parcel_info(
        self, *, application_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_change_parcel_info` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_GET_CHANGE_PARCEL_INFO,
            request=GetChangeParcelInfoRequest(application_id=application_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/getParcelInfo",
        spec="Доставка.json",
        operation_id="v1getParcelInfo",
        method_args={"parcel_id": "body.parcel_id"},
    )
    def get_sandbox_parcel_info(
        self, *, parcel_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_parcel_info` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_GET_PARCEL_INFO,
            request=GetSandboxParcelInfoRequest(parcel_id=parcel_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/delivery-sandbox/v1/getRegisteredParcelID",
        spec="Доставка.json",
        operation_id="v1getRegisteredParcelID",
        method_args={"order_id": "body.order_id"},
    )
    def get_sandbox_registered_parcel_id(
        self, *, order_id: str, idempotency_key: str | None = None
    ) -> DeliveryEntityResult:
        """Выполняет публичную операцию `SandboxDelivery.get_sandbox_registered_parcel_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SANDBOX_GET_REGISTERED_PARCEL_ID,
            request=GetRegisteredParcelIdRequest(order_id=order_id),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]


@dataclass(slots=True, frozen=True)
class DeliveryTask(DomainObject):
    """Доменный объект задачи доставки."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "delivery_task"
    __sdk_factory_args__ = {"task_id": "path.task_id"}

    task_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/delivery-sandbox/tasks/{task_id}",
        spec="Доставка.json",
        operation_id="GetTask",
    )
    def get(self, *, task_id: str | None = None) -> DeliveryTaskInfo:
        """Выполняет публичную операцию `DeliveryTask.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_task_id = task_id or self._require_task_id()
        return self._execute(
            GET_DELIVERY_TASK,
            path_params={"task_id": resolved_task_id},
        )  # type: ignore[return-value]

    def _require_task_id(self) -> str:
        if self.task_id is None:
            raise ValidationError("Для операции требуется `task_id`.")
        return str(self.task_id)


@dataclass(slots=True, frozen=True)
class Stock(DomainObject):
    """Доменный объект управления остатками."""

    __swagger_domain__ = "orders"
    __sdk_factory__ = "stock"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/stock-management/1/info",
        spec="Управлениеостатками.json",
        method_args={"item_ids": "body.item_ids"},
    )
    def get(self, *, item_ids: Sequence[int]) -> StockInfoResult:
        """Выполняет публичную операцию `Stock.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_STOCK_INFO,
            request=StockInfoRequest(item_ids=list(item_ids)),
        )  # type: ignore[return-value]

    @swagger_operation(
        "PUT",
        "/stock-management/1/stocks",
        spec="Управлениеостатками.json",
        method_args={"stocks": "body.stocks"},
    )
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

        return self._execute(
            UPDATE_STOCKS,
            request=StockUpdateRequest(stocks=list(stocks)),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]


__all__ = (
    "DeliveryOrder",
    "DeliveryTask",
    "Order",
    "OrderLabel",
    "SandboxDelivery",
    "Stock",
)
