"""Типизированные модели раздела autoteka."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class CatalogResolveRequest:
    """Запрос актуализации параметров автокаталога."""

    brand_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос автокаталога."""

        return {"brandId": self.brand_id}


@dataclass(slots=True, frozen=True)
class LeadsRequest:
    """Запрос событий сервиса Сигнал."""

    limit: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос событий Сигнал."""

        return {"limit": self.limit}


@dataclass(slots=True, frozen=True)
class VinRequest:
    """Запрос по VIN."""

    vin: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует VIN-запрос."""

        return {"vin": self.vin}


@dataclass(slots=True, frozen=True)
class VehicleIdRequest:
    """Запрос по идентификатору автомобиля."""

    vehicle_id: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос по vehicle id."""

        return {"vehicleId": self.vehicle_id}


@dataclass(slots=True, frozen=True)
class ItemIdRequest:
    """Запрос по идентификатору объявления."""

    item_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос по item id."""

        return {"itemId": self.item_id}


@dataclass(slots=True, frozen=True)
class ExternalItemPreviewRequest:
    """Запрос превью по внешнему объявлению."""

    item_id: str
    site: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос внешнего объявления."""

        return {"itemId": self.item_id, "site": self.site}


@dataclass(slots=True, frozen=True)
class RegNumberRequest:
    """Запрос по государственному номеру."""

    reg_number: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос по госномеру."""

        return {"regNumber": self.reg_number}


@dataclass(slots=True, frozen=True)
class PlateNumberRequest:
    """Запрос по номерному знаку."""

    plate_number: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос по номерному знаку."""

        return {"plateNumber": self.plate_number}


@dataclass(slots=True, frozen=True)
class PreviewReportRequest:
    """Запрос отчета по preview id."""

    preview_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос отчета по preview id."""

        return {"previewId": self.preview_id}


@dataclass(slots=True, frozen=True)
class MonitoringBucketRequest:
    """Запрос изменения списка мониторинга."""

    vehicles: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос изменения списка мониторинга."""

        return {"vehicles": list(self.vehicles)}


@dataclass(slots=True, frozen=True)
class MonitoringEventsQuery:
    """Query событий мониторинга."""

    limit: int | None = None

    def to_params(self) -> dict[str, object]:
        """Сериализует query событий мониторинга."""

        params: dict[str, object] = {}
        if self.limit is not None:
            params["limit"] = self.limit
        return params


@dataclass(slots=True, frozen=True)
class TeaserCreateRequest:
    """Запрос создания тизера."""

    vehicle_id: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос создания тизера."""

        return {"vehicleId": self.vehicle_id}


@dataclass(slots=True, frozen=True)
class ValuationBySpecificationRequest:
    """Запрос оценки автомобиля по specification id."""

    specification_id: int
    mileage: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос оценки автомобиля."""

        return {"specificationId": self.specification_id, "mileage": self.mileage}


@dataclass(slots=True, frozen=True)
class CatalogFieldValue:
    """Значение параметра автокаталога."""

    value_id: str | None
    label: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CatalogField:
    """Параметр автокаталога."""

    field_id: str | None
    label: str | None
    data_type: str | None
    values: list[CatalogFieldValue]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CatalogResolveResult:
    """Результат актуализации параметров автокаталога."""

    items: list[CatalogField]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaLeadEvent:
    """Событие сервиса Сигнал."""

    event_id: str | None
    subscription_id: str | None
    vehicle_id: str | None
    item_id: int | None
    brand: str | None
    model: str | None
    price: int | None
    created_at: str | None
    url: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaLeadsResult:
    """Список событий сервиса Сигнал."""

    items: list[AutotekaLeadEvent]
    last_id: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringInvalidVehicle:
    """Невалидный идентификатор авто в запросах мониторинга."""

    vehicle_id: str | None
    description: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringBucketResult:
    """Результат изменения списка мониторинга."""

    success: bool
    invalid_vehicles: list[MonitoringInvalidVehicle]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringEvent:
    """Событие мониторинга регистрационных действий."""

    vehicle_id: str | None
    brand: str | None
    model: str | None
    year: int | None
    operation_code: int | None
    operation_date_from: str | None
    operation_date_to: str | None
    owner_code: int | None
    actual_at: int | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringEventsResult:
    """Список событий мониторинга."""

    items: list[MonitoringEvent]
    has_next: bool | None = None
    next_cursor: str | None = None
    next_link: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaPackageInfo:
    """Информация о текущем пакете отчетов Автотеки."""

    reports_total: int | None
    reports_remaining: int | None
    created_at: str | None
    expires_at: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaPreviewInfo:
    """Информация о превью автомобиля."""

    preview_id: str | None
    status: str | None
    vehicle_id: str | None
    reg_number: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaReportInfo:
    """Информация об отчете Автотеки."""

    report_id: str | None
    status: str | None
    vehicle_id: str | None
    created_at: str | None
    web_link: str | None
    pdf_link: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaReportsResult:
    """Список отчетов Автотеки."""

    items: list[AutotekaReportInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaScoringInfo:
    """Информация о скоринге рисков."""

    scoring_id: str | None
    is_completed: bool | None
    created_at: int | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaSpecificationInfo:
    """Информация о запросе спецификации автомобиля."""

    specification_id: str | None
    status: str | None
    vehicle_id: str | None
    plate_number: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaTeaserInfo:
    """Информация о тизере Автотеки."""

    teaser_id: str | None
    status: str | None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaValuationInfo:
    """Оценка стоимости автомобиля."""

    status: str | None
    vehicle_id: str | None
    brand: str | None
    model: str | None
    year: int | None
    owners_count: str | None
    mileage: int | None
    avg_price_with_condition: int | None
    avg_market_price: int | None
    _payload: Mapping[str, object] = field(default_factory=dict)


enable_module_serialization(globals())
