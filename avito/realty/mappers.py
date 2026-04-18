"""Мапперы JSON -> dataclass для пакета realty."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.realty.models import (
    RealtyActionResult,
    RealtyAnalyticsInfo,
    RealtyBookingInfo,
    RealtyBookingsResult,
    RealtyMarketPriceInfo,
)

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


def map_action(payload: object) -> RealtyActionResult:
    """Преобразует результат mutation-операции realty."""

    data = _expect_mapping(payload)
    return RealtyActionResult(
        success=_str(data, "result") == "success" or bool(data.get("success", False)),
        status=_str(data, "result", "status"),
        raw_payload=data,
    )


def map_bookings(payload: object) -> RealtyBookingsResult:
    """Преобразует список бронирований."""

    data = _expect_mapping(payload)
    return RealtyBookingsResult(
        items=[
            RealtyBookingInfo(
                booking_id=_str(item, "avito_booking_id", "id"),
                status=_str(item, "status"),
                check_in=_str(item, "check_in"),
                check_out=_str(item, "check_out"),
                guest_count=_int(item, "guest_count"),
                base_price=_int(item, "base_price"),
                guest_name=_str(_mapping(item, "contact"), "name"),
                guest_email=_str(_mapping(item, "contact"), "email"),
                raw_payload=item,
            )
            for item in _list(data, "bookings", "items")
        ],
        raw_payload=data,
    )


def map_market_price(payload: object) -> RealtyMarketPriceInfo:
    """Преобразует соответствие цены рыночной."""

    data = _expect_mapping(payload)
    return RealtyMarketPriceInfo(
        correspondence=_str(data, "correspondence"),
        error_message=_str(_mapping(data, "error"), "message"),
        raw_payload=data,
    )


def map_analytics_report(payload: object) -> RealtyAnalyticsInfo:
    """Преобразует ответ аналитического отчета."""

    data = _expect_mapping(payload)
    success_mapping = _mapping(data, "success")
    success_data = _mapping(success_mapping, "success")
    errors = _mapping(success_mapping, "errors")
    return RealtyAnalyticsInfo(
        success=bool(success_data) or _str(_mapping(data, "result"), "result") == "success",
        report_link=_str(success_data, "reportLink"),
        error_message=_str(errors, "message"),
        raw_payload=data,
    )
