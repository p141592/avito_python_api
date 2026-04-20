from __future__ import annotations

import json
from datetime import datetime

import httpx

from avito.accounts import Account
from avito.ads import AdStats
from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


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


def test_account_operations_history_accepts_datetime_filters() -> None:
    date_from = datetime(2025, 1, 1, 10, 30, 0)
    date_to = datetime(2025, 1, 2, 18, 45, 0)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/core/v1/accounts/operations_history/"
        assert json.loads(request.content.decode()) == {
            "dateFrom": "2025-01-01T10:30:00",
            "dateTo": "2025-01-02T18:45:00",
            "limit": 5,
            "offset": 10,
        }
        return httpx.Response(200, json={"operations": [], "total": 0})

    transport = make_transport(httpx.MockTransport(handler))

    result = Account(transport, user_id=7).get_operations_history(
        date_from=date_from,
        date_to=date_to,
        limit=5,
        offset=10,
    )

    assert result == []


def test_ad_stats_accept_datetime_filters_and_serialize_isoformat() -> None:
    date_from = datetime(2025, 1, 1, 0, 0, 0)
    date_to = datetime(2025, 1, 31, 23, 59, 59)

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        assert body["itemIds"] == [101]
        assert body["dateFrom"] == "2025-01-01T00:00:00"
        assert body["dateTo"] == "2025-01-31T23:59:59"

        if request.url.path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(200, json={"items": []})
        if request.url.path == "/stats/v1/accounts/7/items":
            return httpx.Response(200, json={"items": []})
        if request.url.path == "/stats/v2/accounts/7/items":
            return httpx.Response(200, json={"items": [], "period": "month"})
        assert request.url.path == "/stats/v2/accounts/7/spendings"
        return httpx.Response(200, json={"items": [], "total": 0})

    transport = make_transport(httpx.MockTransport(handler))
    stats = AdStats(transport, item_id=101, user_id=7)

    calls = stats.get_calls_stats(date_from=date_from, date_to=date_to)
    item_stats = stats.get_item_stats(date_from=date_from, date_to=date_to)
    analytics = stats.get_item_analytics(date_from=date_from, date_to=date_to)
    spendings = stats.get_account_spendings(date_from=date_from, date_to=date_to)

    assert calls.items == []
    assert item_stats.items == []
    assert analytics.period == "month"
    assert spendings.total == 0
