"""Доменные объекты пакета realty."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.realty.models import (
    RealtyActionResult,
    RealtyAnalyticsInfo,
    RealtyBaseParamsUpdateRequest,
    RealtyBookingsQuery,
    RealtyBookingsResult,
    RealtyBookingsUpdateRequest,
    RealtyInterval,
    RealtyIntervalsRequest,
    RealtyMarketPriceInfo,
    RealtyPricePeriod,
    RealtyPricesUpdateRequest,
)
from avito.realty.operations import (
    GET_INTERVALS,
    GET_MARKET_PRICE_CORRESPONDENCE,
    GET_REPORT_FOR_CLASSIFIED,
    LIST_REALTY_BOOKINGS,
    UPDATE_BASE_PARAMS,
    UPDATE_BOOKINGS_INFO,
    UPDATE_REALTY_PRICES,
)


@dataclass(slots=True, frozen=True)
class RealtyListing(DomainObject):
    """Доменный объект объявления краткосрочной аренды."""

    __swagger_domain__ = "realty"
    __sdk_factory__ = "realty_listing"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/realty/v1/items/intervals",
        spec="Краткосрочнаяаренда.json",
        operation_id="putIntervals",
        method_args={"intervals": "body.intervals", "item_id": "body.item_id"},
    )
    def get_intervals(
        self,
        *,
        intervals: list[RealtyInterval],
        item_id: int | None = None,
    ) -> RealtyActionResult:
        """Выполняет публичную операцию `RealtyListing.get_intervals` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyActionResult,
            self._execute(
                GET_INTERVALS,
                request=RealtyIntervalsRequest(
                    item_id=item_id or int(self._require_item_id()),
                    intervals=intervals,
                ),
            ),
        )

    @swagger_operation(
        "POST",
        "/realty/v1/items/{item_id}/base",
        spec="Краткосрочнаяаренда.json",
        operation_id="postBaseParams",
        method_args={"min_stay_days": "body.minimal_duration"},
    )
    def update_base_params(
        self, *, min_stay_days: int, item_id: int | str | None = None
    ) -> RealtyActionResult:
        """Выполняет публичную операцию `RealtyListing.update_base_params` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyActionResult,
            self._execute(
                UPDATE_BASE_PARAMS,
                path_params={"item_id": item_id or self._require_item_id()},
                request=RealtyBaseParamsUpdateRequest(min_stay_days=min_stay_days),
            ),
        )

    def _require_item_id(self) -> str:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return str(self.item_id)


@dataclass(slots=True, frozen=True)
class RealtyBooking(DomainObject):
    """Доменный объект бронирований недвижимости."""

    __swagger_domain__ = "realty"
    __sdk_factory__ = "realty_booking"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/core/v1/accounts/{user_id}/items/{item_id}/bookings",
        spec="Краткосрочнаяаренда.json",
        operation_id="putBookingsInfo",
        method_args={"blocked_dates": "body.bookings"},
    )
    def update_bookings_info(
        self,
        *,
        blocked_dates: list[str],
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        """Выполняет публичную операцию `RealtyBooking.update_bookings_info` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyActionResult,
            self._execute(
                UPDATE_BOOKINGS_INFO,
                path_params={
                    "user_id": user_id or self._require_user_id(),
                    "item_id": item_id or self._require_item_id(),
                },
                request=RealtyBookingsUpdateRequest(blocked_dates=blocked_dates),
            ),
        )

    @swagger_operation(
        "GET",
        "/realty/v1/accounts/{user_id}/items/{item_id}/bookings",
        spec="Краткосрочнаяаренда.json",
        operation_id="getRealtyBookings",
        method_args={"date_start": "query.date_start", "date_end": "query.date_end"},
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
        """Выполняет публичную операцию `RealtyBooking.list_realty_bookings` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyBookingsResult,
            self._execute(
                LIST_REALTY_BOOKINGS,
                path_params={
                    "user_id": user_id or self._require_user_id(),
                    "item_id": item_id or self._require_item_id(),
                },
                query=RealtyBookingsQuery(
                    date_start=date_start,
                    date_end=date_end,
                    with_unpaid=with_unpaid,
                ),
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

    __swagger_domain__ = "realty"
    __sdk_factory__ = "realty_pricing"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/realty/v1/accounts/{user_id}/items/{item_id}/prices",
        spec="Краткосрочнаяаренда.json",
        operation_id="postRealtyPrices",
        method_args={"periods": "body.prices"},
    )
    def update_realty_prices(
        self,
        *,
        periods: list[RealtyPricePeriod],
        user_id: int | str | None = None,
        item_id: int | str | None = None,
    ) -> RealtyActionResult:
        """Выполняет публичную операцию `RealtyPricing.update_realty_prices` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyActionResult,
            self._execute(
                UPDATE_REALTY_PRICES,
                path_params={
                    "user_id": user_id or self._require_user_id(),
                    "item_id": item_id or self._require_item_id(),
                },
                request=RealtyPricesUpdateRequest(periods=periods),
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
class RealtyAnalyticsReport(DomainObject):
    """Доменный объект аналитики по недвижимости."""

    __swagger_domain__ = "realty"
    __sdk_factory__ = "realty_analytics_report"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/realty/v1/marketPriceCorrespondence/{itemId}/{price}",
        spec="Аналитикапонедвижимости.json",
        operation_id="market_price_correspondence_v1",
        method_args={"price": "path.price"},
    )
    def get_market_price_correspondence(
        self,
        *,
        item_id: int | str | None = None,
        price: int | str,
    ) -> RealtyMarketPriceInfo:
        """Выполняет публичную операцию `RealtyAnalyticsReport.get_market_price_correspondence` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyMarketPriceInfo,
            self._execute(
                GET_MARKET_PRICE_CORRESPONDENCE,
                path_params={
                    "itemId": item_id or self._require_item_id(),
                    "price": price,
                },
            ),
        )

    @swagger_operation(
        "POST",
        "/realty/v1/report/create/{itemId}",
        spec="Аналитикапонедвижимости.json",
        operation_id="CreateReportForClassified",
    )
    def get_report_for_classified(self, *, item_id: int | str | None = None) -> RealtyAnalyticsInfo:
        """Выполняет публичную операцию `RealtyAnalyticsReport.get_report_for_classified` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return cast(
            RealtyAnalyticsInfo,
            self._execute(
                GET_REPORT_FOR_CLASSIFIED,
                path_params={"itemId": item_id or self._require_item_id()},
            ),
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
