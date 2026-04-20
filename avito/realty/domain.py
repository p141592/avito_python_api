"""Доменные объекты пакета realty."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.realty.client import RealtyAnalyticsClient, ShortTermRentClient
from avito.realty.models import (
    RealtyActionResult,
    RealtyAnalyticsInfo,
    RealtyBaseParamsUpdateRequest,
    RealtyBookingsQuery,
    RealtyBookingsResult,
    RealtyBookingsUpdateRequest,
    RealtyIntervalsRequest,
    RealtyMarketPriceInfo,
    RealtyPricesUpdateRequest,
)


@dataclass(slots=True, frozen=True)
class RealtyListing(DomainObject):
    """Доменный объект объявления краткосрочной аренды."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_intervals(self, *, request: RealtyIntervalsRequest) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).get_intervals(request)

    def update_base_params(
        self, *, request: RealtyBaseParamsUpdateRequest, item_id: int | str | None = None
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_base_params(
            item_id=item_id or self._require_item_id(),
            request=request,
        )

    def _require_item_id(self) -> str:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return str(self.item_id)


@dataclass(slots=True, frozen=True)
class RealtyBooking(DomainObject):
    """Доменный объект бронирований недвижимости."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def update_bookings_info(
        self,
        *,
        request: RealtyBookingsUpdateRequest,
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_bookings_info(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
            request=request,
        )

    def list_realty_bookings(
        self,
        *,
        date_start: str,
        date_end: str,
        with_unpaid: bool | None = None,
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyBookingsResult:
        return ShortTermRentClient(self.transport).list_realty_bookings(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
            query=RealtyBookingsQuery(
                date_start=date_start,
                date_end=date_end,
                with_unpaid=with_unpaid,
            ),
        )

    def _require_item_id(self) -> str:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return str(self.item_id)

    def _require_user_id(self) -> str:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return str(self.user_id)


@dataclass(slots=True, frozen=True)
class RealtyPricing(DomainObject):
    """Доменный объект цен краткосрочной аренды."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def update_realty_prices(
        self,
        *,
        request: RealtyPricesUpdateRequest,
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        return ShortTermRentClient(self.transport).update_realty_prices(
            user_id=user_id or self._require_user_id(),
            item_id=item_id or self._require_item_id(),
            request=request,
        )

    def _require_item_id(self) -> str:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return str(self.item_id)

    def _require_user_id(self) -> str:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return str(self.user_id)


@dataclass(slots=True, frozen=True)
class RealtyAnalyticsReport(DomainObject):
    """Доменный объект аналитики по недвижимости."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_market_price_correspondence(
        self,
        *,
        item_id: int | str | None = None,
        price: int | str,
    ) -> RealtyMarketPriceInfo:
        return RealtyAnalyticsClient(self.transport).get_market_price_correspondence(
            item_id=item_id or self._require_item_id(),
            price=price,
        )

    def get_report_for_classified(self, *, item_id: int | str | None = None) -> RealtyAnalyticsInfo:
        return RealtyAnalyticsClient(self.transport).get_report_for_classified(
            item_id=item_id or self._require_item_id()
        )

    def _require_item_id(self) -> str:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return str(self.item_id)


__all__ = (
    "RealtyAnalyticsReport",
    "RealtyBooking",
    "RealtyListing",
    "RealtyPricing",
)
