"""Внутренние section clients для пакета realty."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.realty.mappers import map_action, map_analytics_report, map_bookings, map_market_price
from avito.realty.models import (
    RealtyActionResult,
    RealtyAnalyticsInfo,
    RealtyBaseParamsUpdateRequest,
    RealtyBookingsUpdateRequest,
    RealtyBookingsQuery,
    RealtyBookingsResult,
    RealtyIntervalsRequest,
    RealtyMarketPriceInfo,
    RealtyPricesUpdateRequest,
)


@dataclass(slots=True)
class ShortTermRentClient:
    """Выполняет HTTP-операции краткосрочной аренды."""

    transport: Transport

    def update_bookings_info(
        self, *, user_id: int | str, item_id: int | str, request: RealtyBookingsUpdateRequest
    ) -> RealtyActionResult:
        payload = self.transport.request_json(
            "POST",
            f"/core/v1/accounts/{user_id}/items/{item_id}/bookings",
            context=RequestContext("realty.bookings.update", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action(payload)

    def list_realty_bookings(
        self, *, user_id: int | str, item_id: int | str, query: RealtyBookingsQuery
    ) -> RealtyBookingsResult:
        payload = self.transport.request_json(
            "GET",
            f"/realty/v1/accounts/{user_id}/items/{item_id}/bookings",
            context=RequestContext("realty.bookings.list"),
            params=query.to_params(),
        )
        return map_bookings(payload)

    def update_realty_prices(
        self, *, user_id: int | str, item_id: int | str, request: RealtyPricesUpdateRequest
    ) -> RealtyActionResult:
        payload = self.transport.request_json(
            "POST",
            f"/realty/v1/accounts/{user_id}/items/{item_id}/prices",
            context=RequestContext("realty.prices.update", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action(payload)

    def get_intervals(self, request: RealtyIntervalsRequest) -> RealtyActionResult:
        payload = self.transport.request_json(
            "POST",
            "/realty/v1/items/intervals",
            context=RequestContext("realty.intervals.fill", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action(payload)

    def update_base_params(
        self, *, item_id: int | str, request: RealtyBaseParamsUpdateRequest
    ) -> RealtyActionResult:
        payload = self.transport.request_json(
            "POST",
            f"/realty/v1/items/{item_id}/base",
            context=RequestContext("realty.base_params.update", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action(payload)


@dataclass(slots=True)
class RealtyAnalyticsClient:
    """Выполняет HTTP-операции аналитики недвижимости."""

    transport: Transport

    def get_market_price_correspondence_v1(
        self, *, item_id: int | str, price: int | str
    ) -> RealtyMarketPriceInfo:
        payload = self.transport.request_json(
            "GET",
            f"/realty/v1/marketPriceCorrespondence/{item_id}/{price}",
            context=RequestContext("realty.analytics.market_price"),
        )
        return map_market_price(payload)

    def get_report_for_classified(self, *, item_id: int | str) -> RealtyAnalyticsInfo:
        payload = self.transport.request_json(
            "POST",
            f"/realty/v1/report/create/{item_id}",
            context=RequestContext("realty.analytics.report", allow_retry=True),
        )
        return map_analytics_report(payload)
