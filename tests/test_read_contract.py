from __future__ import annotations

import json

import httpx

from avito.accounts import Account
from avito.accounts.models import AccountProfile
from avito.ads import Ad, AdStats, Listing
from avito.ads.models import AccountSpendings, CallStats, ListingStats
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


def test_read_methods_return_stable_sdk_models() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/core/v1/accounts/self":
            return httpx.Response(200, json={"id": 7, "name": "Иван", "email": "user@example.com"})
        if path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(200, json={"id": 101, "user_id": 7, "title": "Смартфон"})
        if path == "/core/v1/items":
            assert request.url.params["user_id"] == "7"
            return httpx.Response(
                200, json={"items": [{"id": 101, "title": "Смартфон"}], "total": 1}
            )
        if path == "/stats/v1/accounts/7/items":
            body = json.loads(request.content.decode())
            assert body["itemIds"] == [101]
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
        assert path == "/stats/v2/accounts/7/spendings"
        return httpx.Response(
            200,
            json={"items": [{"item_id": 101, "amount": 77.5, "service": "xl"}]},
        )

    transport = make_transport(httpx.MockTransport(handler))

    profile = Account(transport, user_id=7).get_self()
    listing = Ad(transport, resource_id=101, user_id=7).get()
    listings = Ad(transport, user_id=7).list()
    item_stats = AdStats(transport, resource_id=101, user_id=7).get_item_stats()
    calls_stats = AdStats(transport, resource_id=101, user_id=7).get_calls_stats()
    spendings = AdStats(transport, resource_id=101, user_id=7).get_account_spendings()

    assert isinstance(profile, AccountProfile)
    assert isinstance(listing, Listing)
    assert isinstance(listings.items[0], Listing)
    assert isinstance(item_stats.items[0], ListingStats)
    assert isinstance(calls_stats.items[0], CallStats)
    assert isinstance(spendings, AccountSpendings)


def test_read_methods_handle_empty_and_partial_upstream_payloads() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/core/v1/accounts/self":
            return httpx.Response(200, json={})
        if path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(200, json={"id": 101})
        if path == "/core/v1/items":
            return httpx.Response(200, json={})
        if path == "/stats/v1/accounts/7/items":
            return httpx.Response(200, json={"items": [{"item_id": 101}]})
        if path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(200, json={})
        assert path == "/stats/v2/accounts/7/spendings"
        return httpx.Response(200, json={"items": [{"item_id": 101}]})

    transport = make_transport(httpx.MockTransport(handler))

    profile = Account(transport, user_id=7).get_self()
    listing = Ad(transport, resource_id=101, user_id=7).get()
    listings = Ad(transport, user_id=7).list()
    item_stats = AdStats(transport, resource_id=101, user_id=7).get_item_stats()
    calls_stats = AdStats(transport, resource_id=101, user_id=7).get_calls_stats()
    spendings = AdStats(transport, resource_id=101, user_id=7).get_account_spendings()

    assert profile.to_dict() == {"id": None, "name": None, "email": None, "phone": None}
    assert listing.to_dict() == {
        "id": 101,
        "user_id": None,
        "title": None,
        "description": None,
        "status": None,
        "price": None,
        "url": None,
    }
    assert listings.items == []
    assert item_stats.items[0].to_dict() == {
        "item_id": 101,
        "views": None,
        "contacts": None,
        "favorites": None,
    }
    assert calls_stats.items == []
    assert spendings.to_dict() == {
        "items": [{"item_id": 101, "amount": None, "service": None}],
        "total": None,
    }
