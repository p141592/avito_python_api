from __future__ import annotations

import inspect
import json

import httpx

from avito.accounts import Account, AccountProfile
from avito.accounts.mappers import map_account_profile
from avito.ads import Ad, Listing
from avito.ads.mappers import map_ad_item
from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import BbipPromotion, PromotionOrder, PromotionService, PromotionServicesResult
from avito.promotion.mappers import map_promotion_services


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


def test_public_packages_do_not_export_transport_shapes_or_mappers() -> None:
    import avito.accounts as accounts
    import avito.ads as ads
    import avito.cpa as cpa
    import avito.jobs as jobs
    import avito.orders as orders
    import avito.promotion as promotion

    for module in (accounts, ads, cpa, jobs, orders, promotion):
        exported_names = set(getattr(module, "__all__", ()))
        assert "JsonRequest" not in exported_names
        assert "Transport" not in exported_names
        assert not any(name.startswith("map_") for name in exported_names)
        assert not any(name.endswith("Client") for name in exported_names)


def test_public_domain_signatures_hide_internal_request_wrappers() -> None:
    methods = (
        Account.get_self,
        Ad.get,
        Ad.list,
        PromotionOrder.list_services,
        PromotionOrder.list_orders,
        PromotionOrder.get_order_status,
        BbipPromotion.get_suggests,
    )
    banned_tokens = ("JsonRequest", "CreateBbip", "ListPromotion", "GetPromotionOrderStatusRequest")

    for method in methods:
        signature_text = str(inspect.signature(method))
        doc_text = inspect.getdoc(method) or ""
        public_text = f"{signature_text}\n{doc_text}"
        for token in banned_tokens:
            assert token not in public_text


def test_public_methods_return_sdk_models_not_transport_shapes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None

        if path == "/core/v1/accounts/self":
            return httpx.Response(200, json={"user_id": 7, "title": "Shop 7"})
        if path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(
                200,
                json={
                    "item_id": 101,
                    "userId": 7,
                    "title": "Ноутбук",
                    "price": 55000,
                    "link": "https://example.test/items/101",
                },
            )
        assert path == "/promotion/v1/items/services/get"
        assert payload == {"itemIds": [101]}
        return httpx.Response(
            200,
            json={
                "services": [
                    {
                        "itemID": 101,
                        "code": "xl",
                        "name": "XL",
                        "pricePenny": 12900,
                        "status": "available",
                    }
                ]
            },
        )

    transport = make_transport(httpx.MockTransport(handler))

    profile = Account(transport, user_id=7).get_self()
    listing = Ad(transport, resource_id=101, user_id=7).get()
    services = PromotionOrder(transport).list_services(item_ids=[101])

    assert isinstance(profile, AccountProfile)
    assert isinstance(listing, Listing)
    assert isinstance(services, PromotionServicesResult)
    assert isinstance(services.items[0], PromotionService)

    assert profile.to_dict() == {"id": 7, "name": "Shop 7", "email": None, "phone": None}
    assert listing.to_dict() == {
        "id": 101,
        "user_id": 7,
        "title": "Ноутбук",
        "description": None,
        "status": None,
        "price": 55000.0,
        "url": "https://example.test/items/101",
    }
    assert services.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "service_code": "xl",
                "service_name": "XL",
                "price": 12900,
                "status": "available",
            }
        ]
    }
    assert "_payload" not in profile.to_dict()
    assert "_payload" not in listing.to_dict()
    assert "_payload" not in services.to_dict()


def test_mappers_keep_stable_contract_for_happy_and_partial_payloads() -> None:
    happy_profile = map_account_profile(
        {"id": 7, "name": "Main shop", "email": "shop@example.test"}
    )
    partial_profile = map_account_profile({"user_id": 7, "title": "Main shop"})

    happy_listing = map_ad_item(
        {
            "id": 101,
            "user_id": 7,
            "title": "Phone",
            "description": "Flagship",
            "status": "active",
            "price": 99990,
            "url": "https://example.test/items/101",
        }
    )
    partial_listing = map_ad_item({"itemId": 101, "userId": 7, "title": "Phone"})

    happy_services = map_promotion_services(
        {
            "items": [
                {
                    "itemId": 101,
                    "serviceCode": "highlight",
                    "serviceName": "Highlight",
                    "price": 4900,
                    "status": "active",
                }
            ]
        }
    )
    partial_services = map_promotion_services({"services": [{"itemID": 101, "code": "highlight"}]})

    assert happy_profile.to_dict() == {
        "id": 7,
        "name": "Main shop",
        "email": "shop@example.test",
        "phone": None,
    }
    assert partial_profile.to_dict() == {
        "id": 7,
        "name": "Main shop",
        "email": None,
        "phone": None,
    }

    assert happy_listing.to_dict() == {
        "id": 101,
        "user_id": 7,
        "title": "Phone",
        "description": "Flagship",
        "status": "active",
        "price": 99990.0,
        "url": "https://example.test/items/101",
    }
    assert partial_listing.to_dict() == {
        "id": 101,
        "user_id": 7,
        "title": "Phone",
        "description": None,
        "status": None,
        "price": None,
        "url": None,
    }

    assert happy_services.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "service_code": "highlight",
                "service_name": "Highlight",
                "price": 4900,
                "status": "active",
            }
        ]
    }
    assert partial_services.to_dict() == {
        "items": [
            {
                "item_id": 101,
                "service_code": "highlight",
                "service_name": None,
                "price": None,
                "status": None,
            }
        ]
    }
