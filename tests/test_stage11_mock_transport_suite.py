from __future__ import annotations

import httpx
import pytest

from avito.accounts import Account
from avito.ads import Ad, AdPromotion, AdStats
from avito.core import (
    AuthorizationError,
    ConflictError,
    RateLimitError,
    RetryPolicy,
    UnsupportedOperationError,
    UpstreamApiError,
    ValidationError,
)
from avito.promotion import (
    BbipForecastRequestItem,
    BbipOrderItem,
    BbipPromotion,
    PromotionOrder,
    TargetActionPricing,
    TrxPromotion,
)
from avito.promotion.models import TrxPromotionApplyItem
from tests.fake_transport import FakeTransport, json_response


def test_mock_transport_happy_path_read_methods_and_contract_snapshots(
    fake_transport: FakeTransport,
) -> None:
    fake_transport.add_json(
        "GET",
        "/core/v1/accounts/self",
        {"id": 7, "name": "Иван", "email": "ivan@example.com", "phone": "+79990000000"},
    )
    fake_transport.add(
        "GET",
        "/core/v1/accounts/7/items/101/",
        lambda request: json_response(
            {
                "id": 101,
                "user_id": 7,
                "title": "Смартфон",
                "price": 1000,
                "status": "active",
                "transport_debug": "ignored",
            }
        ),
    )
    fake_transport.add(
        "GET",
        "/core/v1/items",
        lambda request: json_response(
            {
                "items": {
                    "0": [
                        {"id": 101, "title": "Смартфон", "status": "active"},
                        {"id": 102, "title": "Ноутбук", "status": "active"},
                    ],
                    "2": [{"id": 103, "title": "Планшет", "status": "draft"}],
                }[request.params["offset"]],
                "total": 3,
            }
        ),
    )
    fake_transport.add_json(
        "POST",
        "/stats/v1/accounts/7/items",
        {"items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]},
    )
    fake_transport.add_json(
        "POST",
        "/core/v1/accounts/7/calls/stats/",
        {"items": [{"item_id": 101, "calls": 3, "answered_calls": 2, "missed_calls": 1}]},
    )
    fake_transport.add_json(
        "POST",
        "/stats/v2/accounts/7/spendings",
        {"items": [{"item_id": 101, "amount": 77.5, "service": "x2"}]},
    )
    fake_transport.add_json(
        "POST",
        "/promotion/v1/items/services/get",
        {
            "items": [
                {
                    "itemId": 101,
                    "serviceCode": "x2",
                    "serviceName": "X2",
                    "price": 9900,
                    "status": "available",
                    "internalOnly": "ignored",
                }
            ]
        },
    )
    fake_transport.add_json(
        "POST",
        "/promotion/v1/items/services/orders/get",
        {
            "items": [
                {
                    "orderId": "ord-1",
                    "itemId": 101,
                    "serviceCode": "x2",
                    "status": "created",
                    "createdAt": "2026-04-18T10:00:00+03:00",
                }
            ]
        },
    )
    fake_transport.add_json(
        "POST",
        "/promotion/v1/items/services/orders/status",
        {"orderId": "ord-1", "status": "processed", "items": [], "errors": []},
    )
    fake_transport.add_json(
        "POST",
        "/promotion/v1/items/services/bbip/forecasts/get",
        {
            "items": [
                {"itemId": 101, "min": 10, "max": 25, "totalPrice": 7000, "totalOldPrice": 8400}
            ]
        },
    )
    fake_transport.add_json(
        "POST",
        "/promotion/v1/items/services/bbip/suggests/get",
        {
            "items": [
                {
                    "itemId": 101,
                    "duration": {"from": 1, "to": 7, "recommended": 5},
                    "budgets": [{"price": 1000, "oldPrice": 1200, "isRecommended": True}],
                }
            ]
        },
    )
    fake_transport.add_json(
        "GET",
        "/cpxpromo/1/getBids/101",
        {
            "actionTypeID": 5,
            "selectedType": "manual",
            "manual": {
                "bidPenny": 1400,
                "limitPenny": 15000,
                "recBidPenny": 1500,
                "minBidPenny": 1000,
                "maxBidPenny": 2000,
                "minLimitPenny": 5000,
                "maxLimitPenny": 50000,
                "bids": [{"valuePenny": 1500, "minForecast": 2, "maxForecast": 5}],
            },
        },
    )
    fake_transport.add_json(
        "POST",
        "/cpxpromo/1/getPromotionsByItemIds",
        {
            "items": [
                {
                    "itemID": 102,
                    "actionTypeID": 7,
                    "autoPromotion": {"budgetPenny": 9000, "budgetType": "7d"},
                }
            ]
        },
    )

    transport = fake_transport.build()
    account = Account(transport, user_id=7)
    ad = Ad(transport, resource_id=101, user_id=7)
    stats = AdStats(transport, resource_id=101, user_id=7)
    promotion_order = PromotionOrder(transport, resource_id="ord-1")
    bbip = BbipPromotion(transport, resource_id=101)
    pricing = TargetActionPricing(transport, resource_id=101)

    profile = account.get_self()
    listing = ad.get()
    listings = ad.list(status="active", limit=2)
    item_stats = stats.get_item_stats()
    call_stats = stats.get_calls_stats()
    spendings = stats.get_account_spendings()
    services = promotion_order.list_services(item_ids=[101])
    orders = promotion_order.list_orders(item_ids=[101])
    statuses = promotion_order.get_order_status()
    forecasts = bbip.get_forecasts(
        items=[BbipForecastRequestItem(item_id=101, duration=7, price=1000, old_price=1200)]
    )
    suggests = bbip.get_suggests()
    bids = pricing.get_bids()
    promotions = pricing.get_promotions_by_item_ids(item_ids=[101, 102])

    assert profile.to_dict() == {
        "id": 7,
        "name": "Иван",
        "email": "ivan@example.com",
        "phone": "+79990000000",
    }
    assert listing.to_dict() == {
        "id": 101,
        "user_id": 7,
        "title": "Смартфон",
        "description": None,
        "status": "active",
        "price": 1000,
        "url": None,
    }
    assert listings.items.loaded_count == 2
    assert listings.items[0].title == "Смартфон"
    assert listings.items[2].title == "Планшет"
    assert fake_transport.count(method="GET", path="/core/v1/items") == 2
    assert item_stats.to_dict() == {
        "items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]
    }
    assert call_stats.to_dict() == {
        "items": [{"item_id": 101, "calls": 3, "answered_calls": 2, "missed_calls": 1}]
    }
    assert spendings.to_dict() == {
        "items": [{"item_id": 101, "amount": 77.5, "service": "x2"}],
        "total": 77.5,
    }
    assert services.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "service_code": "x2",
                "service_name": "X2",
                "price": 9900,
                "status": "available",
            }
        ]
    }
    assert orders.to_dict() == {
        "items": [
            {
                "order_id": "ord-1",
                "item_id": 101,
                "service_code": "x2",
                "status": "created",
                "created_at": "2026-04-18T10:00:00+03:00",
            }
        ]
    }
    assert statuses.to_dict() == {
        "order_id": "ord-1",
        "status": "processed",
        "total_price": None,
        "items": [],
        "errors": [],
    }
    assert forecasts.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "min_views": 10,
                "max_views": 25,
                "total_price": 7000,
                "total_old_price": 8400,
            }
        ]
    }
    assert suggests.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "duration": {"start": 1, "stop": 7, "recommended": 5},
                "budgets": [{"price": 1000, "old_price": 1200, "is_recommended": True}],
            }
        ]
    }
    assert bids.to_dict() == {
        "action_type_id": 5,
        "selected_type": "manual",
        "auto": None,
        "manual": {
            "bid_penny": 1400,
            "limit_penny": 15000,
            "rec_bid_penny": 1500,
            "min_bid_penny": 1000,
            "max_bid_penny": 2000,
            "min_limit_penny": 5000,
            "max_limit_penny": 50000,
            "bids": [
                {
                    "value_penny": 1500,
                    "min_forecast": 2,
                    "max_forecast": 5,
                    "compare": None,
                }
            ],
        },
    }
    assert promotions.to_dict() == {
        "items": [
            {
                "item_id": 102,
                "action_type_id": 7,
                "auto": {"budget_penny": 9000, "budget_type": "7d"},
                "manual": None,
            }
        ]
    }


def test_mock_transport_happy_path_write_methods_and_dry_run(
    fake_transport: FakeTransport,
) -> None:
    fake_transport.add_json(
        "PUT",
        "/core/v1/accounts/7/items/101/vas",
        {"success": True, "status": "applied"},
    )
    fake_transport.add_json(
        "PUT",
        "/core/v2/accounts/7/items/101/vas_packages",
        {"success": True, "status": "package_applied"},
    )
    fake_transport.add_json(
        "PUT",
        "/core/v2/items/101/vas/",
        {"success": True, "status": "v2_applied"},
    )
    fake_transport.add_json(
        "PUT",
        "/promotion/v1/items/services/bbip/orders/create",
        {"items": [{"itemId": 101, "success": True, "status": "created", "orderId": "ord-1"}]},
    )
    fake_transport.add_json(
        "POST",
        "/trx-promo/1/apply",
        {"success": {"items": [{"itemID": 101, "success": True}]}},
    )
    fake_transport.add_json(
        "POST",
        "/trx-promo/1/cancel",
        {"success": {"items": [{"itemID": 101, "success": True}]}},
    )
    fake_transport.add_json(
        "POST",
        "/cpxpromo/1/setAuto",
        {"items": [{"itemID": 101, "success": True, "status": "auto"}]},
    )
    fake_transport.add_json(
        "POST",
        "/cpxpromo/1/setManual",
        {"items": [{"itemID": 101, "success": True, "status": "manual"}]},
    )
    fake_transport.add_json(
        "POST",
        "/cpxpromo/1/remove",
        {"items": [{"itemID": 101, "success": True, "status": "removed"}]},
    )

    transport = fake_transport.build()
    ad_promotion = AdPromotion(transport, resource_id=101, user_id=7)
    bbip = BbipPromotion(transport, resource_id=101)
    trx = TrxPromotion(transport, resource_id=101)
    pricing = TargetActionPricing(transport, resource_id=101)

    previews = [
        ad_promotion.apply_vas(codes=["xl"], dry_run=True),
        ad_promotion.apply_vas_package(package_code="turbo", dry_run=True),
        ad_promotion.apply_vas_v2(codes=["highlight"], dry_run=True),
        bbip.create_order(
            items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)],
            dry_run=True,
        ),
        trx.apply(
            items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")],
            dry_run=True,
        ),
        trx.delete(dry_run=True),
        pricing.update_auto(action_type_id=5, budget_penny=8000, budget_type="7d", dry_run=True),
        pricing.update_manual(
            action_type_id=5,
            bid_penny=1500,
            limit_penny=15000,
            dry_run=True,
        ),
        pricing.delete(dry_run=True),
    ]

    assert fake_transport.requests == []
    assert [result.status for result in previews] == ["preview"] * len(previews)

    applied = [
        ad_promotion.apply_vas(codes=["xl"]),
        ad_promotion.apply_vas_package(package_code="turbo"),
        ad_promotion.apply_vas_v2(codes=["highlight"]),
        bbip.create_order(
            items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)]
        ),
        trx.apply(
            items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")]
        ),
        trx.delete(),
        pricing.update_auto(action_type_id=5, budget_penny=8000, budget_type="7d"),
        pricing.update_manual(action_type_id=5, bid_penny=1500, limit_penny=15000),
        pricing.delete(),
    ]

    assert [result.request_payload for result in applied] == [
        result.request_payload for result in previews
    ]
    assert all(result.applied is True for result in applied)
    assert fake_transport.last(
        method="PUT", path="/core/v1/accounts/7/items/101/vas"
    ).json_body == {"codes": ["xl"]}
    assert fake_transport.last(
        method="PUT", path="/promotion/v1/items/services/bbip/orders/create"
    ).json_body == {"items": [{"itemId": 101, "duration": 7, "price": 1000, "oldPrice": 1200}]}
    assert applied[3].to_dict() == {
        "action": "create_order",
        "target": {"item_ids": [101]},
        "status": "created",
        "applied": True,
        "request_payload": {
            "items": [{"itemId": 101, "duration": 7, "price": 1000, "oldPrice": 1200}]
        },
        "warnings": [],
        "upstream_reference": "ord-1",
        "details": {
            "items": [{"item_id": 101, "success": True, "status": "created", "message": None}]
        },
    }


@pytest.mark.parametrize(
    ("status_code", "error_cls"),
    [
        (400, ValidationError),
        (403, AuthorizationError),
        (409, ConflictError),
        (429, RateLimitError),
        (405, UnsupportedOperationError),
        (418, UpstreamApiError),
    ],
)
def test_mock_transport_maps_typed_errors_for_public_calls(
    fake_transport: FakeTransport,
    status_code: int,
    error_cls: type[Exception],
) -> None:
    fake_transport.add(
        "GET",
        "/core/v1/accounts/self",
        httpx.Response(
            status_code,
            json={
                "message": "request failed",
                "error": "E_TEST",
                "client_secret": "super-secret",
            },
            headers={"Authorization": "Bearer secret-token"},
        ),
    )
    transport = fake_transport.build(retry_policy=RetryPolicy(max_attempts=1))

    with pytest.raises(error_cls) as error:
        Account(transport).get_self()

    assert "accounts.get_self" in str(error.value)
    assert error.value.metadata == {"method": "GET", "path": "/core/v1/accounts/self"}
    assert error.value.payload["client_secret"] == "***"
    assert error.value.headers["authorization"] == "***"


def test_mock_transport_pagination_is_lazy_and_propagates_later_page_errors() -> None:
    fake_transport = FakeTransport()
    fake_transport.add(
        "GET",
        "/core/v1/items",
        json_response(
            {
                "items": [{"id": 101, "title": "Смартфон"}, {"id": 102, "title": "Ноутбук"}],
                "total": 4,
            }
        ),
        httpx.Response(429, json={"message": "page 2 failed"}, headers={"retry-after": "1"}),
    )
    transport = fake_transport.build(retry_policy=RetryPolicy(max_attempts=1))
    items = Ad(transport, user_id=7).list(limit=2)

    assert fake_transport.count(method="GET", path="/core/v1/items") == 1
    assert items.items[0].id == 101
    assert fake_transport.count(method="GET", path="/core/v1/items") == 1

    with pytest.raises(RateLimitError, match="page 2 failed"):
        _ = items.items[2]

    assert fake_transport.count(method="GET", path="/core/v1/items") == 2
    assert items.items[1].id == 102
    assert fake_transport.count(method="GET", path="/core/v1/items") == 2
