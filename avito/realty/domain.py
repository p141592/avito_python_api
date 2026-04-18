"""Доменные объекты пакета realty."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import Transport
from avito.realty.client import RealtyAnalyticsClient, ShortTermRentClient
from avito.realty.models import (
    JsonRequest,
    RealtyActionResult,
    RealtyAnalyticsInfo,
    RealtyBookingsResult,
    RealtyMarketPriceInfo,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела realty."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class RealtyListing(DomainObject):
    """Доменный объект объявления краткосрочной аренды."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_intervals(self, *, payload: Mapping[str, object]) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).get_intervals(JsonRequest(payload))

    def update_base_params(
        self, *, payload: Mapping[str, object], item_id: int | str | None = None
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_base_params(
            item_id=item_id or self._require_item_id(),
            request=JsonRequest(payload),
        )

    def _require_item_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class RealtyBooking(DomainObject):
    """Доменный объект бронирований недвижимости."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def update_bookings_info(
        self,
        *,
        payload: Mapping[str, object],
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_bookings_info(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
            request=JsonRequest(payload),
        )

    def list_realty_bookings(
        self,
        *,
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyBookingsResult:
        return ShortTermRentClient(self.transport).list_realty_bookings(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
        )

    def _require_item_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id`.")
        return str(self.resource_id)

    def _require_user_id(self) -> str:
        if self.user_id is None:
            raise ValueError("Для операции требуется `user_id`.")
        return str(self.user_id)


@dataclass(slots=True, frozen=True)
class RealtyPricing(DomainObject):
    """Доменный объект цен краткосрочной аренды."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def update_realty_prices(
        self,
        *,
        payload: Mapping[str, object],
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_realty_prices(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
            request=JsonRequest(payload),
        )

    def _require_item_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id`.")
        return str(self.resource_id)

    def _require_user_id(self) -> str:
        if self.user_id is None:
            raise ValueError("Для операции требуется `user_id`.")
        return str(self.user_id)


@dataclass(slots=True, frozen=True)
class RealtyAnalyticsReport(DomainObject):
    """Доменный объект аналитики по недвижимости."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_market_price_correspondence_v1(
        self,
        *,
        item_id: int | str | None = None,
        price: int | str,
    ) -> RealtyMarketPriceInfo:
        return RealtyAnalyticsClient(self.transport).get_market_price_correspondence_v1(
            item_id=item_id or self._require_item_id(),
            price=price,
        )

    def get_report_for_classified(self, *, item_id: int | str | None = None) -> RealtyAnalyticsInfo:
        return RealtyAnalyticsClient(self.transport).get_report_for_classified(
            item_id=item_id or self._require_item_id()
        )

    def _require_item_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id`.")
        return str(self.resource_id)


__all__ = (
    "DomainObject",
    "RealtyAnalyticsReport",
    "RealtyBooking",
    "RealtyListing",
    "RealtyPricing",
)
