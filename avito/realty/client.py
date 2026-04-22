"""Внутренние section clients для пакета realty."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.realty.mappers import map_action, map_analytics_report, map_bookings, map_market_price
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


@dataclass(slots=True, frozen=True)
class ShortTermRentClient:
    """Выполняет HTTP-операции краткосрочной аренды."""

    transport: Transport

    def update_bookings_info(
        self,
        *,
        user_id: int | str,
        item_id: int | str,
        blocked_dates: list[str],
        idempotency_key: str | None = None,
    ) -> RealtyActionResult:
        return self.transport.request_public_model(
            "POST",
            f"/core/v1/accounts/{user_id}/items/{item_id}/bookings",
            context=RequestContext("realty.bookings.update", allow_retry=idempotency_key is not None),
            mapper=map_action,
            json_body=RealtyBookingsUpdateRequest(blocked_dates=blocked_dates).to_payload(),
            idempotency_key=idempotency_key,
        )

    def list_realty_bookings(
        self, *, user_id: int | str, item_id: int | str, query: RealtyBookingsQuery
    ) -> RealtyBookingsResult:
        return self.transport.request_public_model(
            "GET",
            f"/realty/v1/accounts/{user_id}/items/{item_id}/bookings",
            context=RequestContext("realty.bookings.list"),
            mapper=map_bookings,
            params=query.to_params(),
        )

    def update_realty_prices(
        self,
        *,
        user_id: int | str,
        item_id: int | str,
        periods: list[RealtyPricePeriod],
        idempotency_key: str | None = None,
    ) -> RealtyActionResult:
        return self.transport.request_public_model(
            "POST",
            f"/realty/v1/accounts/{user_id}/items/{item_id}/prices",
            context=RequestContext("realty.prices.update", allow_retry=idempotency_key is not None),
            mapper=map_action,
            json_body=RealtyPricesUpdateRequest(periods=periods).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_intervals(
        self,
        *,
        item_id: int,
        intervals: list[RealtyInterval],
        idempotency_key: str | None = None,
    ) -> RealtyActionResult:
        return self.transport.request_public_model(
            "POST",
            "/realty/v1/items/intervals",
            context=RequestContext("realty.intervals.fill", allow_retry=idempotency_key is not None),
            mapper=map_action,
            json_body=RealtyIntervalsRequest(item_id=item_id, intervals=intervals).to_payload(),
            idempotency_key=idempotency_key,
        )

    def update_base_params(
        self,
        *,
        item_id: int | str,
        min_stay_days: int,
        idempotency_key: str | None = None,
    ) -> RealtyActionResult:
        return self.transport.request_public_model(
            "POST",
            f"/realty/v1/items/{item_id}/base",
            context=RequestContext(
                "realty.base_params.update",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_action,
            json_body=RealtyBaseParamsUpdateRequest(min_stay_days=min_stay_days).to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class RealtyAnalyticsClient:
    """Выполняет HTTP-операции аналитики недвижимости."""

    transport: Transport

    def get_market_price_correspondence(
        self, *, item_id: int | str, price: int | str
    ) -> RealtyMarketPriceInfo:
        return self.transport.request_public_model(
            "GET",
            f"/realty/v1/marketPriceCorrespondence/{item_id}/{price}",
            context=RequestContext("realty.analytics.market_price"),
            mapper=map_market_price,
        )

    def get_report_for_classified(
        self,
        *,
        item_id: int | str,
        idempotency_key: str | None = None,
    ) -> RealtyAnalyticsInfo:
        return self.transport.request_public_model(
            "POST",
            f"/realty/v1/report/create/{item_id}",
            context=RequestContext("realty.analytics.report", allow_retry=idempotency_key is not None),
            mapper=map_analytics_report,
            idempotency_key=idempotency_key,
        )
