from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import (
    AutostrategyCampaign,
    BbipForecastRequestItem,
    BbipOrderItem,
    BbipPromotion,
    CpaAuction,
    CreateItemBid,
    PromotionOrder,
    TargetActionPricing,
    TrxPromotion,
    TrxPromotionApplyItem,
)
from avito.promotion.models import (
    CampaignListFilter,
    CampaignOrderBy,
    CampaignUpdateTimeFilter,
    CreateAutostrategyBudgetRequest,
    CreateAutostrategyCampaignRequest,
    ListAutostrategyCampaignsRequest,
    UpdateAutostrategyCampaignRequest,
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


def test_promotion_dictionary_and_orders_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/promotion/v1/items/services/dict":
            return httpx.Response(200, json={"items": [{"code": "x2", "title": "X2"}]})
        if path == "/promotion/v1/items/services/get":
            assert payload == {"itemIds": [101]}
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
            assert payload == {"itemIds": [101]}
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "orderId": "ord-1",
                            "itemId": 101,
                            "serviceCode": "x2",
                            "status": "created",
                        }
                    ]
                },
            )
        assert path == "/promotion/v1/items/services/orders/status"
        assert payload == {"orderIds": ["ord-1"]}
        return httpx.Response(
            200,
            json={"orderId": "ord-1", "status": "processed", "items": [], "errors": []},
        )

    promotion = PromotionOrder(make_transport(httpx.MockTransport(handler)), resource_id="ord-1")

    dictionary = promotion.get_service_dictionary()
    services = promotion.list_services(item_ids=[101])
    orders = promotion.list_orders(item_ids=[101])
    statuses = promotion.get_order_status()

    assert dictionary.items[0].code == "x2"
    assert services.items[0].price == 9900
    assert orders.items[0].order_id == "ord-1"
    assert statuses.status == "processed"


def test_bbip_and_trxpromo_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/promotion/v1/items/services/bbip/forecasts/get":
            assert payload == {
                "items": [{"itemId": 101, "duration": 7, "price": 1000, "oldPrice": 1200}]
            }
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "itemId": 101,
                            "min": 10,
                            "max": 25,
                            "totalPrice": 7000,
                            "totalOldPrice": 8400,
                        }
                    ]
                },
            )
        if path == "/promotion/v1/items/services/bbip/orders/create":
            assert request.method == "PUT"
            assert payload == {
                "items": [{"itemId": 101, "duration": 7, "price": 1000, "oldPrice": 1200}]
            }
            return httpx.Response(
                200, json={"items": [{"itemId": 101, "success": True, "status": "created"}]}
            )
        if path == "/promotion/v1/items/services/bbip/suggests/get":
            assert payload == {"itemIds": [101]}
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "itemId": 101,
                            "duration": {"from": 1, "to": 7, "recommended": 5},
                            "budgets": [{"price": 1000, "oldPrice": 1200, "isRecommended": True}],
                        }
                    ]
                },
            )
        if path == "/trx-promo/1/apply":
            assert payload == {
                "items": [{"itemID": 101, "commission": 1500, "dateFrom": "2026-04-18"}]
            }
            return httpx.Response(
                200, json={"success": {"items": [{"itemID": 101, "success": True}]}}
            )
        if path == "/trx-promo/1/cancel":
            assert payload == {"items": [{"itemID": 101}]}
            return httpx.Response(
                200, json={"success": {"items": [{"itemID": 101, "success": True}]}}
            )
        assert path == "/trx-promo/1/commissions"
        assert request.url.params["itemIDs"] == "101"
        return httpx.Response(
            200,
            json={
                "success": {
                    "items": [
                        {
                            "itemID": 101,
                            "commission": 1500,
                            "isActive": True,
                            "validCommissionRange": {
                                "valueMin": 100,
                                "valueMax": 2000,
                                "step": 100,
                            },
                        }
                    ]
                }
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    bbip = BbipPromotion(transport, resource_id=101)
    trx = TrxPromotion(transport, resource_id=101)

    forecasts = bbip.get_forecasts(
        items=[BbipForecastRequestItem(item_id=101, duration=7, price=1000, old_price=1200)]
    )
    order_result = bbip.create_order(
        items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)]
    )
    suggests = bbip.get_suggests()
    applied = trx.apply(
        items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")]
    )
    cancelled = trx.delete()
    commissions = trx.get_commissions()

    assert forecasts.items[0].max_views == 25
    assert order_result.status == "created"
    assert order_result.applied is True
    assert suggests.items[0].duration is not None and suggests.items[0].duration.recommended == 5
    assert applied.applied is True
    assert cancelled.applied is True
    assert commissions.items[0].valid_commission_range is not None
    assert commissions.items[0].valid_commission_range.value_max == 2000


def test_cpa_auction_and_target_action_pricing_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/auction/1/bids" and request.method == "GET":
            assert request.url.params["fromItemID"] == "100"
            assert request.url.params["batchSize"] == "50"
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "itemID": 101,
                            "pricePenny": 1300,
                            "expirationTime": "2026-04-18T10:00:00+03:00",
                            "availablePrices": [{"pricePenny": 1200, "goodness": 1}],
                        }
                    ]
                },
            )
        if path == "/auction/1/bids":
            assert payload == {"items": [{"itemID": 101, "pricePenny": 1500}]}
            return httpx.Response(200, json={"items": [{"itemID": 101, "success": True}]})
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
        if path == "/cpxpromo/1/getPromotionsByItemIds":
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
        if path == "/cpxpromo/1/remove":
            assert payload == {"itemID": 101}
            return httpx.Response(
                200, json={"items": [{"itemID": 101, "success": True, "status": "removed"}]}
            )
        if path == "/cpxpromo/1/setAuto":
            assert payload == {
                "itemID": 101,
                "actionTypeID": 5,
                "budgetPenny": 8000,
                "budgetType": "7d",
            }
            return httpx.Response(
                200, json={"items": [{"itemID": 101, "success": True, "status": "auto"}]}
            )
        assert path == "/cpxpromo/1/setManual"
        assert payload == {"itemID": 101, "actionTypeID": 5, "bidPenny": 1500, "limitPenny": 15000}
        return httpx.Response(
            200, json={"items": [{"itemID": 101, "success": True, "status": "manual"}]}
        )

    transport = make_transport(httpx.MockTransport(handler))
    auction = CpaAuction(transport)
    pricing = TargetActionPricing(transport, resource_id=101)

    bids = auction.get_user_bids(from_item_id=100, batch_size=50)
    saved = auction.create_item_bids(items=[CreateItemBid(item_id=101, price_penny=1500)])
    details = pricing.get_bids()
    promotions = pricing.get_promotions_by_item_ids(item_ids=[101, 102])
    removed = pricing.delete()
    auto = pricing.update_auto(action_type_id=5, budget_penny=8000, budget_type="7d")
    manual = pricing.update_manual(action_type_id=5, bid_penny=1500, limit_penny=15000)

    assert bids.items[0].available_prices[0].price_penny == 1200
    assert saved.applied is True
    assert details.manual is not None and details.manual.bids[0].compare == 10
    assert promotions.items[0].auto is not None
    assert removed.status == "removed"
    assert auto.status == "auto"
    assert manual.status == "manual"


def test_autostrategy_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/autostrategy/v1/budget":
            assert payload == {
                "campaignType": "AS",
                "startTime": "2026-04-20T00:00:00Z",
                "finishTime": "2026-04-27T00:00:00Z",
                "items": [101, 102],
            }
            return httpx.Response(
                200,
                json={
                    "calcId": 501,
                    "budget": {
                        "recommended": {
                            "total": 10100,
                            "real": 10000,
                            "bonus": 100,
                            "viewsFrom": 30,
                            "viewsTo": 50,
                        },
                        "minimal": {"total": 5100, "real": 5000, "bonus": 100},
                        "priceRanges": [
                            {
                                "priceFrom": 10000,
                                "priceTo": 20000,
                                "percent": 90,
                                "viewsFrom": 20,
                                "viewsTo": 40,
                            }
                        ],
                    },
                },
            )
        if path == "/autostrategy/v1/campaign/create":
            assert payload == {
                "campaignType": "AS",
                "title": "Весенняя кампания",
                "budget": 10000,
                "calcId": 501,
                "items": [101, 102],
                "startTime": "2026-04-20T00:00:00Z",
                "finishTime": "2026-04-27T00:00:00Z",
            }
            return httpx.Response(
                200,
                json={"campaign": {"campaignId": 77, "campaignType": "AS", "version": 3}},
            )
        if path == "/autostrategy/v1/campaign/edit":
            assert payload == {"campaignId": 77, "version": 3, "title": "Обновленная кампания"}
            return httpx.Response(
                200,
                json={"campaign": {"campaignId": 77, "campaignType": "AS", "version": 4}},
            )
        if path == "/autostrategy/v1/campaign/info":
            assert payload == {"campaignId": 77}
            return httpx.Response(
                200,
                json={
                    "campaign": {
                        "campaignId": 77,
                        "campaignType": "AS",
                        "statusId": 1,
                        "budget": 10000,
                        "balance": 9000,
                        "title": "Весенняя кампания",
                        "version": 4,
                    },
                    "forecast": {
                        "calls": {"from": 2, "to": 5},
                        "views": {"from": 30, "to": 50},
                    },
                    "items": [{"itemId": 101, "isActive": True}],
                },
            )
        if path == "/autostrategy/v1/campaign/stop":
            assert payload == {"campaignId": 77, "version": 4}
            return httpx.Response(
                200,
                json={"campaign": {"campaignId": 77, "campaignType": "AS", "version": 5}},
            )
        if path == "/autostrategy/v1/campaigns":
            assert payload == {
                "limit": 20,
                "offset": 10,
                "statusId": [1, 2],
                "orderBy": [{"column": "startTime", "direction": "asc"}],
                "filter": {
                    "byUpdateTime": {
                        "from": "2026-04-01T00:00:00Z",
                        "to": "2026-04-30T00:00:00Z",
                    }
                },
            }
            return httpx.Response(
                200,
                json={
                    "campaigns": [
                        {
                            "campaignId": 77,
                            "campaignType": "AS",
                            "statusId": 1,
                            "budget": 10000,
                        }
                    ],
                    "totalCount": 1,
                },
            )
        assert path == "/autostrategy/v1/stat"
        assert payload == {"campaignId": 77}
        return httpx.Response(
            200,
            json={
                "stat": [
                    {
                        "date": "2026-04-18",
                        "calls": 30,
                        "views": 500,
                        "callsForecast": {"from": 25, "to": 35},
                        "viewsForecast": {"from": 450, "to": 550},
                    }
                ],
                "totals": {"calls": 30, "views": 500},
            },
        )

    campaign = AutostrategyCampaign(make_transport(httpx.MockTransport(handler)), resource_id=77)

    budget = campaign.create_budget(
        request=CreateAutostrategyBudgetRequest(
            campaign_type="AS",
            start_time="2026-04-20T00:00:00Z",
            finish_time="2026-04-27T00:00:00Z",
            items=[101, 102],
        )
    )
    created = campaign.create(
        request=CreateAutostrategyCampaignRequest(
            campaign_type="AS",
            title="Весенняя кампания",
            budget=10000,
            calc_id=501,
            items=[101, 102],
            start_time="2026-04-20T00:00:00Z",
            finish_time="2026-04-27T00:00:00Z",
        )
    )
    updated = campaign.update(
        request=UpdateAutostrategyCampaignRequest(
            campaign_id=77,
            version=3,
            title="Обновленная кампания",
        )
    )
    info = campaign.get()
    stopped = campaign.delete(version=4)
    campaigns = campaign.list(
        request=ListAutostrategyCampaignsRequest(
            limit=20,
            offset=10,
            status_id=[1, 2],
            order_by=[CampaignOrderBy(column="startTime", direction="asc")],
            filter=CampaignListFilter(
                by_update_time=CampaignUpdateTimeFilter(
                    from_time="2026-04-01T00:00:00Z",
                    to_time="2026-04-30T00:00:00Z",
                )
            ),
        )
    )
    stat = campaign.get_stat()

    assert budget.calc_id == 501
    assert budget.recommended is not None and budget.recommended.total == 10100
    assert created.campaign is not None and created.campaign.version == 3
    assert updated.campaign is not None and updated.campaign.version == 4
    assert info.campaign is not None and info.campaign.balance == 9000
    assert info.items[0].item_id == 101
    assert stopped.campaign is not None and stopped.campaign.version == 5
    assert campaigns.items[0].campaign_id == 77
    assert campaigns.total_count == 1
    assert stat.totals is not None and stat.totals.views == 500
    assert stat.items[0].calls == 30
