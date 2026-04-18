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
    PromotionOrderStatusResult,
    TargetActionGetBidsResult,
    TargetActionPricing,
    TargetActionPromotion,
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


def test_promotion_read_methods_return_documented_models() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/promotion/v1/items/services/orders/status":
            assert payload == {"orderIds": ["ord-1"]}
            return httpx.Response(
                200,
                json={
                    "orderId": "ord-1",
                    "status": "processed",
                    "totalPrice": 26166,
                    "items": [
                        {
                            "itemId": 101,
                            "price": 9900,
                            "slug": "x2",
                            "status": "processed",
                            "errorReason": None,
                        }
                    ],
                    "errors": [{"itemId": 102, "errorCode": 1005, "errorText": "Недоступно"}],
                },
            )
        if path == "/cpxpromo/1/getBids/101":
            return httpx.Response(
                200,
                json={
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
        assert path == "/cpxpromo/1/getPromotionsByItemIds"
        assert payload == {"itemIDs": [101, 102]}
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "itemID": 102,
                        "actionTypeID": 7,
                        "autoPromotion": {"budgetPenny": 9000, "budgetType": "7d"},
                    }
                ]
            },
        )

    transport = make_transport(httpx.MockTransport(handler))

    status = PromotionOrder(transport, resource_id="ord-1").get_order_status()
    bids = TargetActionPricing(transport, resource_id=101).get_bids()
    promotions = TargetActionPricing(transport, resource_id=101).get_promotions_by_item_ids(
        item_ids=[101, 102]
    )

    assert isinstance(status, PromotionOrderStatusResult)
    assert isinstance(bids, TargetActionGetBidsResult)
    assert isinstance(promotions.items[0], TargetActionPromotion)

    assert status.to_dict() == {
        "order_id": "ord-1",
        "status": "processed",
        "total_price": 26166,
        "items": [
            {
                "item_id": 101,
                "price": 9900,
                "slug": "x2",
                "status": "processed",
                "error_reason": None,
            }
        ],
        "errors": [{"item_id": 102, "error_code": 1005, "error_text": "Недоступно"}],
    }
    assert bids.to_dict()["manual"]["bids"][0]["compare"] == 10
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


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/promotion/v1/items/services/orders/status", {"items": []}),
        ("/cpxpromo/1/getBids/102", {"items": []}),
        ("/cpxpromo/1/getPromotionsByItemIds", {"items": [{"itemID": 102}]}),
    ],
)
def test_documented_read_mappers_raise_on_invalid_shape(path: str, body: dict[str, object]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    transport = make_transport(httpx.MockTransport(handler))

    with pytest.raises(ResponseMappingError):
        if path == "/promotion/v1/items/services/orders/status":
            PromotionOrder(transport, resource_id="ord-2").get_order_status()
        elif path == "/cpxpromo/1/getBids/102":
            TargetActionPricing(transport, resource_id=102).get_bids()
        else:
            TargetActionPricing(transport, resource_id=102).get_promotions_by_item_ids(
                item_ids=[102]
            )
