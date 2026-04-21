"""Типизированные модели раздела realty."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class RealtyActionResult(SerializableModel):
    """Результат mutation-операции по недвижимости."""

    success: bool
    status: str | None = None


@dataclass(slots=True, frozen=True)
class RealtyBookingsUpdateRequest:
    """Запрос обновления занятости по объекту."""

    blocked_dates: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса бронирований."""

        return {"blockedDates": list(self.blocked_dates)}


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
class RealtyPricePeriod:
    """Период с ценой в запросе обновления цен."""

    date_from: str
    price: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует период с ценой."""

        return {"dateFrom": self.date_from, "price": self.price}


@dataclass(slots=True, frozen=True)
class RealtyPricesUpdateRequest:
    """Запрос обновления цен по объекту."""

    periods: list[RealtyPricePeriod]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса цен."""

        return {"periods": [period.to_payload() for period in self.periods]}


@dataclass(slots=True, frozen=True)
class RealtyInterval:
    """Интервал доступности объекта."""

    date: str
    available: bool

    def to_payload(self) -> dict[str, object]:
        """Сериализует интервал доступности."""

        return {"date": self.date, "available": self.available}


@dataclass(slots=True, frozen=True)
class RealtyIntervalsRequest:
    """Запрос заполнения интервалов доступности."""

    item_id: int
    intervals: list[RealtyInterval]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса интервалов."""

        return {
            "itemId": self.item_id,
            "intervals": [interval.to_payload() for interval in self.intervals],
        }


@dataclass(slots=True, frozen=True)
class RealtyBaseParamsUpdateRequest:
    """Запрос обновления базовых параметров объекта."""

    min_stay_days: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса базовых параметров."""

        return {"minStayDays": self.min_stay_days}


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


