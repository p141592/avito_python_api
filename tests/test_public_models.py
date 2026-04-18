from __future__ import annotations

import json

import httpx

from avito.accounts import Account
from avito.accounts.models import AccountProfile
from avito.ads import Ad, AdStats
from avito.ads.models import AccountSpendings, CallStats, Listing, ListingStats, SpendingRecord
from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import (
    BbipForecastRequestItem,
    BbipPromotion,
    PromotionOrder,
    PromotionService,
)
from avito.promotion.models import PromotionForecast
from avito.promotion.models import PromotionOrder as PromotionOrderModel


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(),
        retry_policy=RetryPolicy(),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )


def test_primary_sdk_models_serialize_without_transport_fields() -> None:
    profile = AccountProfile(
        id=7,
        name="Иван",
        email=None,
        phone="+7999",
    )
    listing = Listing(
        id=101,
        user_id=7,
        title="Смартфон",
        description=None,
        status="active",
        price=1000.0,
        url=None,
    )
    stats = ListingStats(
        item_id=101,
        views=42,
        contacts=None,
        favorites=3,
    )
    calls = CallStats(
        item_id=101,
        calls=4,
        answered_calls=3,
        missed_calls=1,
    )
    spendings = AccountSpendings(
        items=[
            SpendingRecord(
                item_id=101,
                amount=77.5,
                service="xl",
            )
        ],
        total=77.5,
    )
    service = PromotionService(
        item_id=101,
        service_code="x2",
        service_name="X2",
        price=9900,
        status="available",
    )
    order = PromotionOrderModel(
        order_id="ord-1",
        item_id=101,
        service_code="x2",
        status="created",
        created_at=None,
    )
    forecast = PromotionForecast(
        item_id=101,
        min_views=10,
        max_views=25,
        total_price=7000,
        total_old_price=None,
    )

    assert profile.to_dict() == {"id": 7, "name": "Иван", "email": None, "phone": "+7999"}
    assert listing.to_dict() == {
        "id": 101,
        "user_id": 7,
        "title": "Смартфон",
        "description": None,
        "status": "active",
        "price": 1000.0,
        "url": None,
    }
    assert stats.model_dump() == {
        "item_id": 101,
        "views": 42,
        "contacts": None,
        "favorites": 3,
    }
    assert calls.to_dict() == {
        "item_id": 101,
        "calls": 4,
        "answered_calls": 3,
        "missed_calls": 1,
    }
    assert spendings.to_dict() == {
        "items": [{"item_id": 101, "amount": 77.5, "service": "xl"}],
        "total": 77.5,
    }
    assert service.to_dict() == {
        "item_id": 101,
        "service_code": "x2",
        "service_name": "X2",
        "price": 9900,
        "status": "available",
    }
    assert order.to_dict() == {
        "order_id": "ord-1",
        "item_id": 101,
        "service_code": "x2",
        "status": "created",
        "created_at": None,
    }
    assert forecast.to_dict() == {
        "item_id": 101,
        "min_views": 10,
        "max_views": 25,
        "total_price": 7000,
        "total_old_price": None,
    }
    assert isinstance(order, PromotionOrderModel)


def test_primary_read_methods_return_stable_sdk_models() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/core/v1/accounts/self":
            return httpx.Response(200, json={"id": 7, "name": "Иван"})
        if path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(200, json={"id": 101, "user_id": 7, "title": "Смартфон"})
        if path == "/stats/v1/accounts/7/items":
            return httpx.Response(
                200,
                json={"items": [{"item_id": 101, "views": 42, "contacts": 5, "favorites": 3}]},
            )
        if path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(
                200,
                json={
                    "items": [{"item_id": 101, "calls": 4, "answered_calls": 3, "missed_calls": 1}]
                },
            )
        if path == "/stats/v2/accounts/7/spendings":
            return httpx.Response(
                200,
                json={"items": [{"item_id": 101, "amount": 77.5, "service": "xl"}]},
            )
        if path == "/promotion/v1/items/services/get":
            assert json.loads(request.content.decode()) == {"itemIds": [101]}
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "itemId": 101,
                            "serviceCode": "x2",
                            "serviceName": "X2",
                            "price": 9900,
                            "status": "available",
                        }
                    ]
                },
            )
        if path == "/promotion/v1/items/services/orders/get":
            assert json.loads(request.content.decode()) == {"itemIds": [101]}
            return httpx.Response(
                200,
                json={"items": [{"orderId": "ord-1", "itemId": 101, "serviceCode": "x2"}]},
            )
        assert path == "/promotion/v1/items/services/bbip/forecasts/get"
        return httpx.Response(
            200,
            json={"items": [{"itemId": 101, "min": 10, "max": 25, "totalPrice": 7000}]},
        )

    transport = make_transport(httpx.MockTransport(handler))

    profile = Account(transport, user_id=7).get_self()
    listing = Ad(transport, resource_id=101, user_id=7).get()
    stats = AdStats(transport, resource_id=101, user_id=7).get_item_stats()
    calls = AdStats(transport, resource_id=101, user_id=7).get_calls_stats()
    spendings = AdStats(transport, resource_id=101, user_id=7).get_account_spendings()
    services = PromotionOrder(transport, resource_id="ord-1").list_services(item_ids=[101])
    orders = PromotionOrder(transport, resource_id="ord-1").list_orders(item_ids=[101])
    forecasts = BbipPromotion(transport, resource_id=101).get_forecasts(
        items=[BbipForecastRequestItem(item_id=101, duration=7, price=1000, old_price=1200)]
    )

    assert isinstance(profile, AccountProfile)
    assert isinstance(listing, Listing)
    assert isinstance(stats.items[0], ListingStats)
    assert isinstance(calls.items[0], CallStats)
    assert isinstance(spendings, AccountSpendings)
    assert isinstance(services.items[0], PromotionService)
    assert isinstance(orders.items[0], PromotionOrderModel)
    assert isinstance(forecasts.items[0], PromotionForecast)
