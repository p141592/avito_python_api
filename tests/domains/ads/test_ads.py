from __future__ import annotations

import json
import logging
from datetime import datetime

import httpx
import pytest

from avito.ads import Ad, AdPromotion, AdStats
from avito.ads.enums import ListingStatus
from tests.helpers.transport import make_transport


def test_ads_list_uses_lazy_pagination_with_list_like_items() -> None:
    seen_offsets: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/core/v1/items"
        assert request.url.params["user_id"] == "7"
        assert request.url.params["status"] == "active"
        assert request.url.params["limit"] == "2"

        offset = request.url.params["offset"]
        seen_offsets.append(offset)
        page_items = {
            "0": [{"id": 101, "title": "Смартфон"}, {"id": 102, "title": "Ноутбук"}],
            "2": [{"id": 103, "title": "Планшет"}, {"id": 104, "title": "Наушники"}],
            "4": [{"id": 105, "title": "Камера"}],
        }
        return httpx.Response(200, json={"items": page_items[offset], "total": 5})

    ad = Ad(make_transport(httpx.MockTransport(handler)), user_id=7)

    items = ad.list(status="active", limit=2)

    assert seen_offsets == ["0"]
    assert items[3].item_id == 104
    assert seen_offsets == ["0", "2"]
    assert [item.title for item in items.materialize()] == [
        "Смартфон",
        "Ноутбук",
        "Планшет",
        "Наушники",
        "Камера",
    ]
    assert seen_offsets == ["0", "2", "4"]


def test_ads_domain_covers_item_stats_spendings_and_promotion() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(
                200,
                json={"id": 101, "user_id": 7, "title": "Смартфон", "price": 1000, "status": "active"},
            )
        if request.url.path == "/stats/v1/accounts/7/items":
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]}
            )
        if request.url.path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(
                200,
                json={"items": [{"item_id": 101, "calls": 3, "answered_calls": 2, "missed_calls": 1}]},
            )
        if request.url.path == "/stats/v2/accounts/7/spendings":
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "amount": 77.5, "service": "xl"}]}
            )
        if request.url.path == "/core/v1/accounts/7/items/101/vas":
            assert json.loads(request.content.decode()) == {"codes": ["xl"]}
            return httpx.Response(200, json={"success": True, "status": "applied"})
        assert request.url.path == "/core/v1/items/101/update_price"
        assert json.loads(request.content.decode()) == {"price": 1500}
        return httpx.Response(200, json={"item_id": 101, "price": 1500, "status": "updated"})

    transport = make_transport(httpx.MockTransport(handler))
    ad = Ad(transport, item_id=101, user_id=7)
    stats = AdStats(transport, item_id=101, user_id=7)
    promotion = AdPromotion(transport, item_id=101, user_id=7)

    item = ad.get()
    updated = ad.update_price(price=1500)
    item_stats = stats.get_item_stats()
    calls = stats.get_calls_stats()
    spendings = stats.get_account_spendings()
    applied = promotion.apply_vas(codes=["xl"])

    assert item.title == "Смартфон"
    assert updated.status == "updated"
    assert item_stats.items[0].views == 45
    assert calls.items[0].answered_calls == 2
    assert spendings.total == 77.5
    assert applied.status == "applied"


def test_ad_stats_accept_datetime_filters_and_serialize_isoformat() -> None:
    seen_payloads: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_payloads.append(json.loads(request.content.decode()))
        return httpx.Response(200, json={"items": [{"item_id": 101, "views": 10}]})

    stats = AdStats(make_transport(httpx.MockTransport(handler)), item_id=101, user_id=7)
    started_at = datetime.fromisoformat("2026-04-18T00:00:00+03:00")
    finished_at = datetime.fromisoformat("2026-04-18T23:59:59+03:00")

    stats.get_item_analytics(item_ids=[101], date_from=started_at, date_to=finished_at)

    assert seen_payloads[0]["dateFrom"] == "2026-04-18T00:00:00+03:00"
    assert seen_payloads[0]["dateTo"] == "2026-04-18T23:59:59+03:00"


def test_ads_unknown_enum_maps_to_unknown_and_warns_once(caplog: pytest.LogCaptureFixture) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/core/v1/accounts/7/items/101/"
        return httpx.Response(
            200,
            json={
                "id": 101,
                "user_id": 7,
                "title": "Смартфон",
                "price": 1000,
                "status": "mystery-status",
            },
        )

    caplog.set_level(logging.WARNING, logger="avito.core.enums")
    ad = Ad(make_transport(httpx.MockTransport(handler)), item_id=101, user_id=7)

    first = ad.get()
    second = ad.get()

    assert first.status is ListingStatus.UNKNOWN
    assert second.status is ListingStatus.UNKNOWN
    records = [
        record
        for record in caplog.records
        if getattr(record, "enum", None) == "ads.listing_status"
        and getattr(record, "value", None) == "mystery-status"
    ]
    assert len(records) == 1
