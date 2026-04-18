"""Типизированные модели раздела realty."""

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
class RealtyActionResult:
    """Результат mutation-операции по недвижимости."""

    success: bool
    status: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RealtyBookingInfo:
    """Информация о бронировании объекта недвижимости."""

    booking_id: str | None
    status: str | None
    check_in: str | None
    check_out: str | None
    guest_count: int | None
    base_price: int | None
    guest_name: str | None
    guest_email: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RealtyBookingsResult:
    """Список бронирований по объявлению."""

    items: list[RealtyBookingInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RealtyMarketPriceInfo:
    """Соответствие цены рыночной стоимости."""

    correspondence: str | None
    error_message: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RealtyAnalyticsInfo:
    """Информация об аналитическом отчете по недвижимости."""

    success: bool
    report_link: str | None = None
    error_message: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)
