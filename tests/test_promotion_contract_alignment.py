from __future__ import annotations

import json

import httpx
import pytest

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import ResponseMappingError, Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import (
    PromotionOrder,
    TargetActionGetBidsResult,
    TargetActionPricing,
    TargetActionPromotionsByItemIdsResult,
)


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


def test_target_action_get_bids_maps_single_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/cpxpromo/1/getBids/101"
        return httpx.Response(
            200,
            json={
                "actionTypeID": 5,
                "selectedType": "manual",
                "auto": {
                    "budgetPenny": 10000,
                    "budgetType": "daily",
                    "minBudgetPenny": 3000,
                    "maxBudgetPenny": 50000,
                    "dailyBudget": {
                        "budgets": [
                            {
                                "valuePenny": 10000,
                                "minForecast": 1,
                                "maxForecast": 3,
                                "compare": 7,
                            }
                        ]
                    },
                },
                "manual": {
                    "bidPenny": 1400,
                    "limitPenny": 15000,
                    "recBidPenny": 1500,
                    "minBidPenny": 1000,
                    "maxBidPenny": 2000,
                    "minLimitPenny": 5000,
                    "maxLimitPenny": 50000,
                    "bids": [
                        {
                            "valuePenny": 1500,
                            "minForecast": 2,
                            "maxForecast": 5,
                            "compare": 10,
                        }
                    ],
                },
            },
        )

    result = TargetActionPricing(make_transport(httpx.MockTransport(handler)), resource_id=101).get_bids()

    assert isinstance(result, TargetActionGetBidsResult)
    assert result.action_type_id == 5
    assert result.selected_type == "manual"
    assert result.auto is not None and result.auto.daily_budget[0].budget_penny == 10000
    assert result.manual is not None and result.manual.bids[0].compare == 10
    assert result.to_dict() == {
        "action_type_id": 5,
        "selected_type": "manual",
        "auto": {
            "budget_penny": 10000,
            "budget_type": "daily",
            "min_budget_penny": 3000,
            "max_budget_penny": 50000,
            "daily_budget": [
                {
                    "budget_penny": 10000,
                    "min_forecast": 1,
                    "max_forecast": 3,
                    "compare": 7,
                }
            ],
            "weekly_budget": [],
            "monthly_budget": [],
        },
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
                    "compare": 10,
                }
            ],
        },
    }


def test_target_action_get_promotions_by_item_ids_maps_items_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/cpxpromo/1/getPromotionsByItemIds"
        assert json.loads(request.content.decode()) == {"itemIDs": [101, 102]}
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "itemID": 101,
                        "actionTypeID": 5,
                        "manualPromotion": {
                            "bidPenny": 1400,
                            "limitPenny": 15000,
                        },
                    },
                    {
                        "itemID": 102,
                        "actionTypeID": 7,
                        "autoPromotion": {
                            "budgetPenny": 9000,
                            "budgetType": "7d",
                        },
                    },
                ]
            },
        )

    result = TargetActionPricing(
        make_transport(httpx.MockTransport(handler)),
        resource_id=101,
    ).get_promotions_by_item_ids(item_ids=[101, 102])

    assert isinstance(result, TargetActionPromotionsByItemIdsResult)
    assert result.items[0].manual is not None and result.items[0].manual.bid_penny == 1400
    assert result.items[1].auto is not None and result.items[1].auto.budget_type == "7d"
    assert result.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "action_type_id": 5,
                "auto": None,
                "manual": {"bid_penny": 1400, "limit_penny": 15000},
            },
            {
                "item_id": 102,
                "action_type_id": 7,
                "auto": {"budget_penny": 9000, "budget_type": "7d"},
                "manual": None,
            },
        ]
    }


def test_promotion_order_status_preserves_top_level_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/promotion/v1/items/services/orders/status"
        assert json.loads(request.content.decode()) == {"orderIds": ["ord-1"]}
        return httpx.Response(
            200,
            json={
                "orderId": "ord-1",
                "status": "processed",
                "totalPrice": 26166,
                "items": [],
                "errors": [],
            },
        )

    result = PromotionOrder(
        make_transport(httpx.MockTransport(handler)),
        resource_id="ord-1",
    ).get_order_status()

    assert result.order_id == "ord-1"
    assert result.status == "processed"
    assert result.total_price == 26166
    assert result.to_dict() == {
        "order_id": "ord-1",
        "status": "processed",
        "total_price": 26166,
        "items": [],
        "errors": [],
    }


def test_promotion_order_status_preserves_item_price_slug_and_error_reason() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "orderId": "ord-2",
                "status": "partial",
                "totalPrice": 10000,
                "items": [
                    {
                        "itemId": 101,
                        "price": 9900,
                        "slug": "x2",
                        "status": "processed",
                        "errorReason": "none",
                    }
                ],
                "errors": [{"itemId": 102, "errorCode": 1005, "errorText": "Недоступно"}],
            },
        )

    result = PromotionOrder(
        make_transport(httpx.MockTransport(handler)),
        resource_id="ord-2",
    ).get_order_status()

    assert result.items[0].item_id == 101
    assert result.items[0].price == 9900
    assert result.items[0].slug == "x2"
    assert result.items[0].error_reason == "none"
    assert result.errors[0].error_code == 1005


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/cpxpromo/1/getBids/101", {"selectedType": "manual"}),
        ("/cpxpromo/1/getPromotionsByItemIds", {"items": [{"itemID": 101}]}),
        ("/promotion/v1/items/services/orders/status", {"status": "processed"}),
    ],
)
def test_promotion_documented_shape_raises_response_mapping_error(
    path: str,
    body: dict[str, object],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    transport = make_transport(httpx.MockTransport(handler))

    with pytest.raises(ResponseMappingError):
        if path == "/cpxpromo/1/getBids/101":
            TargetActionPricing(transport, resource_id=101).get_bids()
        elif path == "/cpxpromo/1/getPromotionsByItemIds":
            TargetActionPricing(transport, resource_id=101).get_promotions_by_item_ids(
                item_ids=[101]
            )
        else:
            PromotionOrder(transport, resource_id="ord-1").get_order_status()
