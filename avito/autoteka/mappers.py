"""Мапперы JSON -> dataclass для пакета autoteka."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.autoteka.models import (
    AutotekaLeadEvent,
    AutotekaLeadsResult,
    AutotekaPackageInfo,
    AutotekaPreviewInfo,
    AutotekaReportInfo,
    AutotekaReportsResult,
    AutotekaScoringInfo,
    AutotekaSpecificationInfo,
    AutotekaTeaserInfo,
    AutotekaValuationInfo,
    CatalogField,
    CatalogFieldValue,
    CatalogResolveResult,
    MonitoringBucketResult,
    MonitoringEvent,
    MonitoringEventsResult,
    MonitoringInvalidVehicle,
)
from avito.core.exceptions import ResponseMappingError

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_catalogs_resolve(payload: object) -> CatalogResolveResult:
    """Преобразует ответ автокаталога."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    return CatalogResolveResult(
        items=[
            CatalogField(
                field_id=_str(item, "id", "fieldId"),
                label=_str(item, "label"),
                data_type=_str(item, "dataType", "type"),
                values=[
                    CatalogFieldValue(
                        value_id=_str(value, "valueId", "id"),
                        label=_str(value, "label", "value"),
                        raw_payload=value,
                    )
                    for value in _list(item, "values", "items")
                ],
                raw_payload=item,
            )
            for item in _list(result, "fields", "items")
        ],
        raw_payload=data,
    )


def map_leads(payload: object) -> AutotekaLeadsResult:
    """Преобразует события сервиса Сигнал."""

    data = _expect_mapping(payload)
    pagination = _mapping(data, "pagination")
    items = []
    for item in _list(data, "result", "items"):
        event_payload = _mapping(item, "payload")
        items.append(
            AutotekaLeadEvent(
                event_id=_str(item, "id"),
                subscription_id=_str(item, "subscriptionId"),
                vehicle_id=_str(event_payload, "vin", "vehicleId"),
                item_id=_int(event_payload, "itemId"),
                brand=_str(event_payload, "brand"),
                model=_str(event_payload, "model"),
                price=_int(event_payload, "price"),
                created_at=_str(event_payload, "itemCreatedAt"),
                url=_str(event_payload, "url"),
                raw_payload=item,
            )
        )
    return AutotekaLeadsResult(items=items, last_id=_int(pagination, "lastId"), raw_payload=data)


def map_monitoring_bucket(payload: object) -> MonitoringBucketResult:
    """Преобразует результат изменения корзины мониторинга."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    return MonitoringBucketResult(
        success=bool(result.get("isOk", False)),
        invalid_vehicles=[
            MonitoringInvalidVehicle(
                vehicle_id=_str(item, "vehicleID", "vehicleId"),
                description=_str(item, "description"),
                raw_payload=item,
            )
            for item in _list(result, "invalidVehicles", "items")
        ],
        raw_payload=data,
    )


def map_monitoring_events(payload: object) -> MonitoringEventsResult:
    """Преобразует события мониторинга."""

    data = _expect_mapping(payload)
    pagination = _mapping(data, "pagination")
    return MonitoringEventsResult(
        items=[
            MonitoringEvent(
                vehicle_id=_str(item, "vin", "vehicleId"),
                brand=_str(item, "brand"),
                model=_str(item, "model"),
                year=_int(item, "year"),
                operation_code=_int(item, "operationCode"),
                operation_date_from=_str(item, "operationDateFrom", "operationDate"),
                operation_date_to=_str(item, "operationDateTo"),
                owner_code=_int(item, "ownerCode"),
                actual_at=_int(item, "actualAt"),
                raw_payload=item,
            )
            for item in _list(data, "data", "items")
        ],
        has_next=_bool(pagination, "hasNext"),
        next_cursor=_str(pagination, "nextCursor"),
        next_link=_str(pagination, "nextLink"),
        raw_payload=data,
    )


def map_package(payload: object) -> AutotekaPackageInfo:
    """Преобразует информацию о пакете отчетов."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    package = _mapping(result, "package")
    return AutotekaPackageInfo(
        reports_total=_int(package, "reportsCnt"),
        reports_remaining=_int(package, "reportsCntRemain"),
        created_at=_str(package, "createdTime"),
        expires_at=_str(package, "expireTime"),
        raw_payload=data,
    )


def _map_preview_source(source: Payload) -> AutotekaPreviewInfo:
    return AutotekaPreviewInfo(
        preview_id=_str(source, "previewId"),
        status=_str(source, "status"),
        vehicle_id=_str(source, "vin", "vehicleId"),
        reg_number=_str(source, "regNumber", "plateNumber"),
        raw_payload=source,
    )


def map_preview(payload: object) -> AutotekaPreviewInfo:
    """Преобразует превью автомобиля."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    preview = _mapping(result, "preview")
    source = preview or result or data
    return _map_preview_source(source)


def _map_report_source(source: Payload) -> AutotekaReportInfo:
    data = _mapping(source, "data")
    return AutotekaReportInfo(
        report_id=_str(source, "reportId"),
        status=_str(source, "status"),
        vehicle_id=_str(data, "vin", "vehicleId") or _str(source, "vin"),
        created_at=_str(source, "createdAt") or _str(data, "createdAt"),
        web_link=_str(source, "webLink"),
        pdf_link=_str(source, "pdfLink"),
        raw_payload=source,
    )


def map_report(payload: object) -> AutotekaReportInfo:
    """Преобразует один отчет Автотеки."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    report = _mapping(result, "report")
    source = report or result or data
    return _map_report_source(source)


def map_reports(payload: object) -> AutotekaReportsResult:
    """Преобразует список отчетов."""

    data = _expect_mapping(payload)
    return AutotekaReportsResult(
        items=[_map_report_source(item) for item in _list(data, "result", "items")],
        raw_payload=data,
    )


def map_scoring(payload: object) -> AutotekaScoringInfo:
    """Преобразует ответ скоринга."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    scoring = _mapping(result, "scoring", "risksAssessment")
    source = scoring or result or data
    return AutotekaScoringInfo(
        scoring_id=_str(source, "scoringId"),
        is_completed=_bool(source, "isCompleted"),
        created_at=_int(source, "createdAt"),
        raw_payload=source,
    )


def map_specification(payload: object) -> AutotekaSpecificationInfo:
    """Преобразует ответ спецификации."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    specification = _mapping(result, "specification")
    source = specification or result or data
    return AutotekaSpecificationInfo(
        specification_id=_str(source, "specificationId"),
        status=_str(source, "status"),
        vehicle_id=_str(source, "vehicleId"),
        plate_number=_str(source, "plateNumber"),
        raw_payload=source,
    )


def map_teaser(payload: object) -> AutotekaTeaserInfo:
    """Преобразует ответ тизера."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    teaser_wrapper = _mapping(result, "teaser")
    teaser_data = _mapping(teaser_wrapper, "data") or _mapping(data, "data")
    source = teaser_wrapper or result or data
    return AutotekaTeaserInfo(
        teaser_id=_str(source, "teaserId"),
        status=_str(source, "status"),
        brand=_str(teaser_data, "brand") if teaser_data else _str(source, "brand"),
        model=_str(teaser_data, "model") if teaser_data else _str(source, "model"),
        year=_int(teaser_data, "year") if teaser_data else _int(source, "year"),
        raw_payload=data,
    )


def map_valuation(payload: object) -> AutotekaValuationInfo:
    """Преобразует ответ оценки автомобиля."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    valuation = _mapping(result, "valuation")
    source = result or data
    return AutotekaValuationInfo(
        status=_str(source, "status"),
        vehicle_id=_str(source, "vehicleId"),
        brand=_str(source, "brand"),
        model=_str(source, "model"),
        year=_int(source, "year"),
        owners_count=_str(source, "ownersCount"),
        mileage=_int(source, "mileage"),
        avg_price_with_condition=_int(valuation, "avgPriceWithCondition"),
        avg_market_price=_int(valuation, "avgMarketPrice"),
        raw_payload=data,
    )
