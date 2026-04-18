"""Типизированные модели раздела autoteka."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class JsonRequest:
    """Типизированная обертка над JSON payload запроса."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class CatalogFieldValue:
    """Значение параметра автокаталога."""

    value_id: str | None
    label: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CatalogField:
    """Параметр автокаталога."""

    field_id: str | None
    label: str | None
    data_type: str | None
    values: list[CatalogFieldValue]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CatalogResolveResult:
    """Результат актуализации параметров автокаталога."""

    items: list[CatalogField]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaLeadsResult:
    """Список событий сервиса Сигнал."""

    items: list[AutotekaLeadEvent]
    last_id: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringInvalidVehicle:
    """Невалидный идентификатор авто в запросах мониторинга."""

    vehicle_id: str | None
    description: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringBucketResult:
    """Результат изменения списка мониторинга."""

    success: bool
    invalid_vehicles: list[MonitoringInvalidVehicle]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MonitoringEventsResult:
    """Список событий мониторинга."""

    items: list[MonitoringEvent]
    has_next: bool | None = None
    next_cursor: str | None = None
    next_link: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaPackageInfo:
    """Информация о текущем пакете отчетов Автотеки."""

    reports_total: int | None
    reports_remaining: int | None
    created_at: str | None
    expires_at: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaPreviewInfo:
    """Информация о превью автомобиля."""

    preview_id: str | None
    status: str | None
    vehicle_id: str | None
    reg_number: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaReportInfo:
    """Информация об отчете Автотеки."""

    report_id: str | None
    status: str | None
    vehicle_id: str | None
    created_at: str | None
    web_link: str | None
    pdf_link: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaReportsResult:
    """Список отчетов Автотеки."""

    items: list[AutotekaReportInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaScoringInfo:
    """Информация о скоринге рисков."""

    scoring_id: str | None
    is_completed: bool | None
    created_at: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaSpecificationInfo:
    """Информация о запросе спецификации автомобиля."""

    specification_id: str | None
    status: str | None
    vehicle_id: str | None
    plate_number: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutotekaTeaserInfo:
    """Информация о тизере Автотеки."""

    teaser_id: str | None
    status: str | None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
    raw_payload: Mapping[str, object] = field(default_factory=dict)
