"""Типизированные модели раздела realty."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import SerializableModel, enable_module_serialization


@dataclass(slots=True, frozen=True)
class RealtyRequest:
    """Унифицированный typed request для Realty API."""

    payload: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class RealtyActionResult(SerializableModel):
    """Результат mutation-операции по недвижимости."""

    success: bool
    status: str | None = None


@dataclass(slots=True, frozen=True)
class RealtyBookingSafeDeposit(SerializableModel):
    """Информация о предоплате по бронированию."""

    owner_amount: int | None
    tax: int | None
    total_amount: int | None


@dataclass(slots=True, frozen=True)
class RealtyBookingContact(SerializableModel):
    """Контактные данные гостя."""

    name: str | None
    email: str | None
    phone: str | None


@dataclass(slots=True, frozen=True)
class RealtyBookingInfo(SerializableModel):
    """Информация о бронировании объекта недвижимости."""

    booking_id: int | None
    base_price: int | None
    check_in: str | None
    check_out: str | None
    contact: RealtyBookingContact | None
    guest_count: int | None
    nights: int | None
    safe_deposit: RealtyBookingSafeDeposit | None
    status: str | None


@dataclass(slots=True, frozen=True)
class RealtyBookingsResult(SerializableModel):
    """Список бронирований по объявлению."""

    items: list[RealtyBookingInfo]


@dataclass(slots=True, frozen=True)
class RealtyBookingsQuery:
    """Query-параметры запроса бронирований."""

    date_start: str
    date_end: str
    with_unpaid: bool | None = None

    def to_params(self) -> dict[str, str]:
        """Сериализует query-параметры запроса бронирований."""

        params = {"date_start": self.date_start, "date_end": self.date_end}
        if self.with_unpaid is not None:
            params["with_unpaid"] = "true" if self.with_unpaid else "false"
        return params


@dataclass(slots=True, frozen=True)
class RealtyMarketPriceInfo(SerializableModel):
    """Соответствие цены рыночной стоимости."""

    correspondence: str | None
    error_message: str | None = None


@dataclass(slots=True, frozen=True)
class RealtyAnalyticsInfo(SerializableModel):
    """Информация об аналитическом отчете по недвижимости."""

    success: bool
    report_link: str | None = None
    error_message: str | None = None


enable_module_serialization(globals())
