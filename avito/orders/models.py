"""Типизированные модели раздела orders."""

from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from typing import Any

from avito.core import BinaryResponse
from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class DeliveryDateInterval:
    """Интервалы доставки/забора для конкретной даты."""

    date: str
    intervals: list[str]

    def to_payload(self) -> dict[str, object]:
        return {"date": self.date, "intervals": list(self.intervals)}


@dataclass(slots=True, frozen=True)
class CustomAreaScheduleEntry:
    """Кастомное расписание для списка областей доставки."""

    provider_area_numbers: list[str]
    services: list[str]
    custom_schedule: list[DeliveryDateInterval]
    use_all_areas: bool | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "providerAreaNumber": list(self.provider_area_numbers),
            "services": list(self.services),
            "customSchedule": [entry.to_payload() for entry in self.custom_schedule],
        }
        if self.use_all_areas is not None:
            payload["useAllAreas"] = self.use_all_areas
        return payload


@dataclass(slots=True, frozen=True)
class CustomAreaScheduleRequest:
    """Запрос установки кастомного расписания областей."""

    items: list[CustomAreaScheduleEntry]

    def to_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.items]


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
class CancelParcelRequest:
    """Запрос отмены sandbox-посылки."""

    parcel_id: str
    actor: str

    def to_payload(self) -> dict[str, object]:
        return {"parcelID": self.parcel_id, "actor": self.actor}


@dataclass(slots=True, frozen=True)
class SandboxConfirmationCodeRequest:
    """Запрос проверки кода подтверждения sandbox-заказа."""

    parcel_id: str
    confirm_code: str

    def to_payload(self) -> dict[str, object]:
        return {"parcelID": self.parcel_id, "confirmCode": self.confirm_code}


@dataclass(slots=True, frozen=True)
class DeliveryTerms:
    """Параметры условий доставки заказа."""

    cost: int | None = None
    direct_control_date: str | None = None
    receiver_terminal_code: str | None = None
    return_control_date: str | None = None
    sender_receive_terminal_code: str | None = None
    tough_wrap: bool | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.cost is not None:
            payload["cost"] = self.cost
        if self.direct_control_date is not None:
            payload["directControlDate"] = self.direct_control_date
        if self.receiver_terminal_code is not None:
            payload["receiverTerminalCode"] = self.receiver_terminal_code
        if self.return_control_date is not None:
            payload["returnControlDate"] = self.return_control_date
        if self.sender_receive_terminal_code is not None:
            payload["senderReceiveTerminalCode"] = self.sender_receive_terminal_code
        if self.tough_wrap is not None:
            payload["toughWrap"] = self.tough_wrap
        return payload


@dataclass(slots=True, frozen=True)
class OrderDeliveryProperties:
    """Набор параметров доставки sandbox-заказа."""

    delivery: DeliveryTerms | None = None
    dimensions: list[int] | None = None
    weight: int | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.delivery is not None:
            payload["delivery"] = self.delivery.to_payload()
        if self.dimensions is not None:
            payload["dimensions"] = list(self.dimensions)
        if self.weight is not None:
            payload["weight"] = self.weight
        return payload


@dataclass(slots=True, frozen=True)
class SetOrderPropertiesRequest:
    """Запрос установки параметров доставки sandbox-заказа."""

    order_id: str
    properties: OrderDeliveryProperties

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "properties": self.properties.to_payload()}


@dataclass(slots=True, frozen=True)
class RealAddress:
    """Фактический адрес приема или возврата."""

    address_type: str
    terminal_number: str

    def to_payload(self) -> dict[str, object]:
        return {
            "addressType": self.address_type,
            "terminalNumber": self.terminal_number,
        }


@dataclass(slots=True, frozen=True)
class SetOrderRealAddressRequest:
    """Запрос передачи фактического адреса sandbox-заказа."""

    order_id: str
    address: RealAddress

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id, "address": self.address.to_payload()}


@dataclass(slots=True, frozen=True)
class DeliveryTrackingOptions:
    """Дополнительные поля tracking-события."""

    barcode: str | None = None
    return_barcode: str | None = None
    return_dispatch_number: str | None = None
    return_tracking_number: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.barcode is not None:
            payload["barcode"] = self.barcode
        if self.return_barcode is not None:
            payload["returnBarcode"] = self.return_barcode
        if self.return_dispatch_number is not None:
            payload["returnDispatchNumber"] = self.return_dispatch_number
        if self.return_tracking_number is not None:
            payload["returnTrackingNumber"] = self.return_tracking_number
        return payload


@dataclass(slots=True, frozen=True)
class DeliveryTrackingRequest:
    """Запрос передачи tracking-события sandbox-заказа."""

    order_id: str
    avito_status: str
    avito_event_type: str
    provider_event_code: str
    date: str
    location: str
    comment: str | None = None
    options: DeliveryTrackingOptions | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "orderId": self.order_id,
            "avitoStatus": self.avito_status,
            "avitoEventType": self.avito_event_type,
            "providerEventCode": self.provider_event_code,
            "date": self.date,
            "location": self.location,
        }
        if self.comment is not None:
            payload["comment"] = self.comment
        if self.options is not None:
            payload["options"] = self.options.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class ProhibitOrderAcceptanceRequest:
    """Запрос запрета приема sandbox-посылки."""

    order_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderId": self.order_id}


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
class DeliveryAddress:
    """Адрес сортировочного центра или терминала."""

    country: str
    region: str
    locality: str
    fias: str
    zip_code: str
    lat: float
    lng: float
    address_row: str | None = None
    building: str | None = None
    floor: int | None = None
    house: str | None = None
    housing: str | None = None
    locality_type: str | None = None
    porch: str | None = None
    room: str | None = None
    street: str | None = None
    sub_region: str | None = None
    sub_region_type: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "country": self.country,
            "region": self.region,
            "locality": self.locality,
            "fias": self.fias,
            "zipCode": self.zip_code,
            "lat": self.lat,
            "lng": self.lng,
        }
        if self.address_row is not None:
            payload["addressRow"] = self.address_row
        if self.building is not None:
            payload["building"] = self.building
        if self.floor is not None:
            payload["floor"] = self.floor
        if self.house is not None:
            payload["house"] = self.house
        if self.housing is not None:
            payload["housing"] = self.housing
        if self.locality_type is not None:
            payload["localityType"] = self.locality_type
        if self.porch is not None:
            payload["porch"] = self.porch
        if self.room is not None:
            payload["room"] = self.room
        if self.street is not None:
            payload["street"] = self.street
        if self.sub_region is not None:
            payload["subRegion"] = self.sub_region
        if self.sub_region_type is not None:
            payload["subRegionType"] = self.sub_region_type
        return payload


@dataclass(slots=True, frozen=True)
class DeliveryRestriction:
    """Ограничения терминала или сортировочного центра."""

    max_weight: int
    max_dimensions: list[int]
    max_declared_cost: int
    dimensional_factor: int | None = None
    max_dimensional_weight: int | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "maxWeight": self.max_weight,
            "maxDimensions": list(self.max_dimensions),
            "maxDeclaredCost": self.max_declared_cost,
        }
        if self.dimensional_factor is not None:
            payload["dimensionalFactor"] = self.dimensional_factor
        if self.max_dimensional_weight is not None:
            payload["maxDimensionalWeight"] = self.max_dimensional_weight
        return payload


@dataclass(slots=True, frozen=True)
class WeeklySchedule:
    """Недельное расписание работы."""

    mon: list[str]
    tue: list[str]
    wed: list[str]
    thu: list[str]
    fri: list[str]
    sat: list[str]
    sun: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "mon": list(self.mon),
            "tue": list(self.tue),
            "wed": list(self.wed),
            "thu": list(self.thu),
            "fri": list(self.fri),
            "sat": list(self.sat),
            "sun": list(self.sun),
        }


@dataclass(slots=True, frozen=True)
class SortingCenterUpload:
    """Сортировочный центр для загрузки в sandbox delivery API."""

    delivery_provider_id: str
    name: str
    address: DeliveryAddress
    phones: list[str]
    itinerary: str
    photos: list[str]
    schedule: WeeklySchedule
    restriction: DeliveryRestriction
    direction_tag: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "deliveryProviderId": self.delivery_provider_id,
            "name": self.name,
            "address": self.address.to_payload(),
            "phones": list(self.phones),
            "itinerary": self.itinerary,
            "photos": list(self.photos),
            "schedule": self.schedule.to_payload(),
            "restriction": self.restriction.to_payload(),
        }
        if self.direction_tag is not None:
            payload["directionTag"] = self.direction_tag
        return payload


@dataclass(slots=True, frozen=True)
class AddSortingCentersRequest:
    """Запрос загрузки сортировочных центров."""

    items: list[SortingCenterUpload]

    def to_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.items]


@dataclass(slots=True, frozen=True)
class TaggedSortingCenter:
    """Тэг для сортировочного центра."""

    delivery_provider_id: str
    direction_tag: str

    def to_payload(self) -> dict[str, object]:
        return {
            "deliveryProviderId": self.delivery_provider_id,
            "directionTag": self.direction_tag,
        }


@dataclass(slots=True, frozen=True)
class TaggedSortingCentersRequest:
    """Запрос установки тэгов сортировочным центрам."""

    items: list[TaggedSortingCenter]

    def to_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.items]


@dataclass(slots=True, frozen=True)
class TerminalUpload:
    """Терминал для загрузки в sandbox delivery API."""

    delivery_provider_id: str
    name: str
    address: DeliveryAddress
    phones: list[str]
    itinerary: str
    photos: list[str]
    direction_tag: str
    services: list[str]
    schedule: WeeklySchedule
    restriction: DeliveryRestriction
    display_name: str | None = None
    options: list[str] | None = None
    terminal_type: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "deliveryProviderId": self.delivery_provider_id,
            "name": self.name,
            "address": self.address.to_payload(),
            "phones": list(self.phones),
            "itinerary": self.itinerary,
            "photos": list(self.photos),
            "directionTag": self.direction_tag,
            "services": list(self.services),
            "schedule": self.schedule.to_payload(),
            "restriction": self.restriction.to_payload(),
        }
        if self.display_name is not None:
            payload["displayName"] = self.display_name
        if self.options is not None:
            payload["options"] = list(self.options)
        if self.terminal_type is not None:
            payload["type"] = self.terminal_type
        return payload


@dataclass(slots=True, frozen=True)
class AddTerminalsRequest:
    """Запрос загрузки терминалов."""

    items: list[TerminalUpload]

    def to_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.items]


@dataclass(slots=True, frozen=True)
class DeliveryTermsZone:
    """Зона сроков доставки."""

    delivery_provider_zone_id: str | None = None
    min_term: int | None = None
    max_term: int | None = None
    name: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.delivery_provider_zone_id is not None:
            payload["deliveryProviderZoneId"] = self.delivery_provider_zone_id
        if self.min_term is not None:
            payload["minTerm"] = self.min_term
        if self.max_term is not None:
            payload["maxTerm"] = self.max_term
        if self.name is not None:
            payload["name"] = self.name
        return payload


@dataclass(slots=True, frozen=True)
class UpdateTermsRequest:
    """Запрос обновления сроков по тарифу."""

    items: list[DeliveryTermsZone]

    def to_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.items]


@dataclass(slots=True, frozen=True)
class DeliveryDirectionZone:
    """Условия доставки внутри направления тарифа."""

    tariff_zone_id: str | None = None
    terms_zone_id: str | None = None
    type: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.tariff_zone_id is not None:
            payload["tariffZoneId"] = self.tariff_zone_id
        if self.terms_zone_id is not None:
            payload["termsZoneId"] = self.terms_zone_id
        if self.type is not None:
            payload["type"] = self.type
        return payload


@dataclass(slots=True, frozen=True)
class DeliveryDirection:
    """Направление доставки в тарифе."""

    provider_direction_id: str
    tag_from: str
    tag_to: str
    zones: list[DeliveryDirectionZone]

    def to_payload(self) -> dict[str, object]:
        return {
            "providerDirectionId": self.provider_direction_id,
            "tagFrom": self.tag_from,
            "tagTo": self.tag_to,
            "zones": [zone.to_payload() for zone in self.zones],
        }


@dataclass(slots=True, frozen=True)
class DeliveryTariffValue:
    """Значение внутри модели расчета тарифной зоны."""

    cost: int | None = None
    max_weight: int | None = None
    dimensional_factor: int | None = None
    max_declared_cost: int | None = None
    percent: float | None = None
    min_cost: int | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.cost is not None:
            payload["cost"] = self.cost
        if self.max_weight is not None:
            payload["maxWeight"] = self.max_weight
        if self.dimensional_factor is not None:
            payload["dimensionalFactor"] = self.dimensional_factor
        if self.max_declared_cost is not None:
            payload["maxDeclaredCost"] = self.max_declared_cost
        if self.percent is not None:
            payload["percent"] = self.percent
        if self.min_cost is not None:
            payload["minCost"] = self.min_cost
        return payload


@dataclass(slots=True, frozen=True)
class DeliveryTariffItem:
    """Модель расчета стоимости услуги в тарифной зоне."""

    calculation_mechanic: str
    chargeable_parameter: str
    service_name: str
    values: list[DeliveryTariffValue]

    def to_payload(self) -> dict[str, object]:
        return {
            "calculationMechanic": self.calculation_mechanic,
            "chargeableParameter": self.chargeable_parameter,
            "serviceName": self.service_name,
            "values": [value.to_payload() for value in self.values],
        }


@dataclass(slots=True, frozen=True)
class DeliveryTariffZone:
    """Тарифная зона доставки."""

    name: str
    delivery_provider_zone_id: str
    items: list[DeliveryTariffItem]

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "deliveryProviderZoneId": self.delivery_provider_zone_id,
            "items": [item.to_payload() for item in self.items],
        }


@dataclass(slots=True, frozen=True)
class AddTariffV2Request:
    """Запрос загрузки тарифа sandbox delivery API."""

    name: str
    delivery_provider_tariff_id: str
    directions: list[DeliveryDirection]
    tariff_zones: list[DeliveryTariffZone]
    terms_zones: list[DeliveryTermsZone]
    tariff_type: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "deliveryProviderTariffId": self.delivery_provider_tariff_id,
            "directions": [direction.to_payload() for direction in self.directions],
            "tariffZones": [zone.to_payload() for zone in self.tariff_zones],
            "termsZones": [zone.to_payload() for zone in self.terms_zones],
        }
        if self.tariff_type is not None:
            payload["tariffType"] = self.tariff_type
        return payload


@dataclass(slots=True, frozen=True)
class SandboxCancelAnnouncementOptions:
    """Опции отмены тестового анонса."""

    url_to_cancel_announcement: str

    def to_payload(self) -> dict[str, object]:
        return {"urlToCancelAnnouncement": self.url_to_cancel_announcement}


@dataclass(slots=True, frozen=True)
class SandboxCancelAnnouncementRequest:
    """Запрос отмены тестового анонса."""

    announcement_id: str
    date: str
    options: SandboxCancelAnnouncementOptions

    def to_payload(self) -> dict[str, object]:
        return {
            "announcementID": self.announcement_id,
            "date": self.date,
            "options": self.options.to_payload(),
        }


@dataclass(slots=True, frozen=True)
class CancelSandboxParcelOptions:
    """Опции отмены тестовой посылки."""

    cancelation_url: str

    def to_payload(self) -> dict[str, object]:
        return {"cancelationUrl": self.cancelation_url}


@dataclass(slots=True, frozen=True)
class CancelSandboxParcelRequest:
    """Запрос отмены тестовой посылки."""

    parcel_id: str
    options: CancelSandboxParcelOptions | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"parcelID": self.parcel_id}
        if self.options is not None:
            payload["options"] = self.options.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class ChangeParcelApplication:
    """Изменяемые данные по посылке."""

    kind: str | None = None
    name: str | None = None
    phones: list[str] | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.kind is not None:
            payload["kind"] = self.kind
        if self.name is not None:
            payload["name"] = self.name
        if self.phones is not None:
            payload["phones"] = list(self.phones)
        return payload


@dataclass(slots=True, frozen=True)
class ChangeParcelOptions:
    """Опции создания заявки на изменение посылки."""

    change_parcel_url: str

    def to_payload(self) -> dict[str, object]:
        return {"changeParcelUrl": self.change_parcel_url}


@dataclass(slots=True, frozen=True)
class ChangeParcelRequest:
    """Запрос создания заявки на изменение тестовой посылки."""

    type: str
    parcel_id: str
    application: ChangeParcelApplication | None = None
    options: ChangeParcelOptions | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"type": self.type, "parcelID": self.parcel_id}
        if self.application is not None:
            payload["application"] = self.application.to_payload()
        if self.options is not None:
            payload["options"] = self.options.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class SandboxCreateAnnouncementOptions:
    """Опции создания тестового анонса."""

    url_to_send_announcement: str

    def to_payload(self) -> dict[str, object]:
        return {"urlToSendAnnouncement": self.url_to_send_announcement}


@dataclass(slots=True, frozen=True)
class SandboxDeliveryPoint:
    """Точка отправки или приема в тестовом анонсе."""

    provider: str
    point_id: str | None = None
    accuracy: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"provider": self.provider}
        if self.point_id is not None:
            payload["id"] = self.point_id
        if self.accuracy is not None:
            payload["accuracy"] = self.accuracy
        return payload


@dataclass(slots=True, frozen=True)
class SandboxAnnouncementDelivery:
    """Логистическая точка участника тестового анонса."""

    type: str
    terminal: SandboxDeliveryPoint | None = None
    sorting_center: SandboxDeliveryPoint | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"type": self.type}
        if self.terminal is not None:
            payload["terminal"] = self.terminal.to_payload()
        if self.sorting_center is not None:
            payload["sortingCenter"] = self.sorting_center.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class SandboxAnnouncementParticipant:
    """Участник тестового анонса."""

    type: str
    phones: list[str]
    email: str
    name: str
    delivery: SandboxAnnouncementDelivery

    def to_payload(self) -> dict[str, object]:
        return {
            "type": self.type,
            "phones": list(self.phones),
            "email": self.email,
            "name": self.name,
            "delivery": self.delivery.to_payload(),
        }


@dataclass(slots=True, frozen=True)
class SandboxAnnouncementPackage:
    """Грузоместо в тестовом анонсе."""

    package_id: str
    parcel_ids: list[str]
    seal_id: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "id": self.package_id,
            "parcelIDs": list(self.parcel_ids),
        }
        if self.seal_id is not None:
            payload["sealID"] = self.seal_id
        return payload


@dataclass(slots=True, frozen=True)
class SandboxCreateAnnouncementRequest:
    """Запрос создания тестового анонса."""

    announcement_id: str
    barcode: str
    sender: SandboxAnnouncementParticipant
    receiver: SandboxAnnouncementParticipant
    announcement_type: str
    date: str
    packages: list[SandboxAnnouncementPackage]
    options: SandboxCreateAnnouncementOptions

    def to_payload(self) -> dict[str, object]:
        return {
            "announcementID": self.announcement_id,
            "barcode": self.barcode,
            "sender": self.sender.to_payload(),
            "receiver": self.receiver.to_payload(),
            "announcementType": self.announcement_type,
            "date": self.date,
            "packages": [package.to_payload() for package in self.packages],
            "options": self.options.to_payload(),
        }


@dataclass(slots=True, frozen=True)
class SandboxGetAnnouncementEventRequest:
    """Запрос последнего события тестового анонса."""

    announcement_id: str

    def to_payload(self) -> dict[str, object]:
        return {"announcementID": self.announcement_id}


@dataclass(slots=True, frozen=True)
class GetChangeParcelInfoRequest:
    """Запрос информации о заявке на изменение посылки."""

    application_id: str

    def to_payload(self) -> dict[str, object]:
        return {"applicationID": self.application_id}


@dataclass(slots=True, frozen=True)
class GetSandboxParcelInfoRequest:
    """Запрос информации о тестовой посылке."""

    parcel_id: str

    def to_payload(self) -> dict[str, object]:
        return {"parcelID": self.parcel_id}


@dataclass(slots=True, frozen=True)
class GetRegisteredParcelIdRequest:
    """Запрос ID зарегистрированной тестовой посылки."""

    order_id: str

    def to_payload(self) -> dict[str, object]:
        return {"orderID": self.order_id}


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
class OrderSummary(SerializableModel):
    """Краткая информация о заказе."""

    order_id: str | None
    status: str | None
    created_at: str | None
    buyer_name: str | None
    total_price: int | None


@dataclass(slots=True, frozen=True)
class OrdersResult(SerializableModel):
    """Список заказов."""

    items: list[OrderSummary]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class OrderActionResult(SerializableModel):
    """Результат операции над заказом."""

    success: bool
    order_id: str | None = None
    status: str | None = None
    message: str | None = None


@dataclass(slots=True, frozen=True)
class CourierRange(SerializableModel):
    """Доступный интервал курьерской доставки."""

    interval_id: str | None
    date: str | None
    start_at: str | None
    end_at: str | None


@dataclass(slots=True, frozen=True)
class CourierRangesResult(SerializableModel):
    """Список доступных интервалов курьерской доставки."""

    items: list[CourierRange]
    address: str | None = None


@dataclass(slots=True, frozen=True)
class LabelTaskResult(SerializableModel):
    """Результат генерации этикеток."""

    task_id: str | None
    status: str | None = None


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
class DeliveryEntityResult(SerializableModel):
    """Результат операции delivery API."""

    success: bool
    task_id: str | None = None
    order_id: str | None = None
    parcel_id: str | None = None
    status: str | None = None
    message: str | None = None


@dataclass(slots=True, frozen=True)
class DeliverySortingCenter(SerializableModel):
    """Сортировочный центр доставки."""

    sorting_center_id: str | None
    name: str | None
    city: str | None


@dataclass(slots=True, frozen=True)
class DeliverySortingCentersResult(SerializableModel):
    """Список сортировочных центров доставки."""

    items: list[DeliverySortingCenter]


@dataclass(slots=True, frozen=True)
class DeliveryTaskInfo(SerializableModel):
    """Информация о задаче доставки."""

    task_id: str | None
    status: str | None
    error: str | None


@dataclass(slots=True, frozen=True)
class StockInfo(SerializableModel):
    """Информация по остаткам объявления."""

    item_id: int | None
    quantity: int | None
    is_multiple: bool | None
    is_unlimited: bool | None
    is_out_of_stock: bool | None


@dataclass(slots=True, frozen=True)
class StockInfoResult(SerializableModel):
    """Список текущих остатков."""

    items: list[StockInfo]


@dataclass(slots=True, frozen=True)
class StockUpdateItem(SerializableModel):
    """Результат обновления остатков объявления."""

    item_id: int | None
    external_id: str | None
    success: bool
    errors: list[str]


@dataclass(slots=True, frozen=True)
class StockUpdateResult(SerializableModel):
    """Результат изменения остатков."""

    items: list[StockUpdateItem]
