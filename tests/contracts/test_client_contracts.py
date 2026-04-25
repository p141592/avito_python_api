from __future__ import annotations

import httpx
import pytest

from avito import AuthSettings, AvitoClient, AvitoSettings
from avito.accounts import Account, AccountHierarchy
from avito.ads import Ad, AdPromotion, AdStats, AutoloadArchive, AutoloadProfile, AutoloadReport
from avito.auth import AlternateTokenClient, AuthProvider, TokenClient
from avito.autoteka import (
    AutotekaMonitoring,
    AutotekaReport,
    AutotekaScoring,
    AutotekaValuation,
    AutotekaVehicle,
)
from avito.core import Transport
from avito.core.exceptions import ConfigurationError
from avito.core.types import ApiTimeouts
from avito.cpa import CallTrackingCall, CpaArchive, CpaCall, CpaChat, CpaLead
from avito.jobs import Application, JobDictionary, JobWebhook, Resume, Vacancy
from avito.messenger import Chat, ChatMedia, ChatMessage, ChatWebhook, SpecialOfferCampaign
from avito.orders import DeliveryOrder, DeliveryTask, Order, OrderLabel, SandboxDelivery, Stock
from avito.promotion import (
    AutostrategyCampaign,
    BbipPromotion,
    CpaAuction,
    PromotionOrder,
    TargetActionPricing,
    TrxPromotion,
)
from avito.ratings import RatingProfile, Review, ReviewAnswer
from avito.realty import RealtyAnalyticsReport, RealtyBooking, RealtyListing, RealtyPricing
from avito.summary import AccountHealthSummary, CapabilityDiscoveryResult, ListingHealthSummary
from avito.tariffs import Tariff
from tests.helpers.transport import make_transport


def test_single_client_exposes_domain_factories() -> None:
    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )

    assert isinstance(client.auth(), AuthProvider)
    assert isinstance(client.account(1), Account)
    assert isinstance(client.account_hierarchy(1), AccountHierarchy)
    assert isinstance(client.ad(1), Ad)
    assert isinstance(client.ad_stats(1), AdStats)
    assert isinstance(client.ad_promotion(1), AdPromotion)
    assert isinstance(client.autoload_profile(1), AutoloadProfile)
    assert isinstance(client.autoload_report(1), AutoloadReport)
    assert isinstance(client.autoload_archive(1), AutoloadArchive)
    assert isinstance(client.chat("chat-1", user_id=1), Chat)
    assert isinstance(client.chat_message("msg-1", chat_id="chat-1", user_id=1), ChatMessage)
    assert isinstance(client.chat_webhook(), ChatWebhook)
    assert isinstance(client.chat_media(user_id=1), ChatMedia)
    assert isinstance(client.special_offer_campaign(1), SpecialOfferCampaign)
    assert isinstance(client.promotion_order(1), PromotionOrder)
    assert isinstance(client.bbip_promotion(1), BbipPromotion)
    assert isinstance(client.trx_promotion(1), TrxPromotion)
    assert isinstance(client.cpa_auction(1), CpaAuction)
    assert isinstance(client.target_action_pricing(1), TargetActionPricing)
    assert isinstance(client.autostrategy_campaign(1), AutostrategyCampaign)
    assert isinstance(client.order(), Order)
    assert isinstance(client.order_label(1), OrderLabel)
    assert isinstance(client.delivery_order(), DeliveryOrder)
    assert isinstance(client.sandbox_delivery(), SandboxDelivery)
    assert isinstance(client.delivery_task(1), DeliveryTask)
    assert isinstance(client.stock(), Stock)
    assert isinstance(client.vacancy(1), Vacancy)
    assert isinstance(client.application(), Application)
    assert isinstance(client.resume(1), Resume)
    assert isinstance(client.job_webhook(), JobWebhook)
    assert isinstance(client.job_dictionary(1), JobDictionary)
    assert isinstance(client.cpa_lead(), CpaLead)
    assert isinstance(client.cpa_chat(1), CpaChat)
    assert isinstance(client.cpa_call(), CpaCall)
    assert isinstance(client.cpa_archive(1), CpaArchive)
    assert isinstance(client.call_tracking_call(1), CallTrackingCall)
    assert isinstance(client.autoteka_vehicle(1), AutotekaVehicle)
    assert isinstance(client.autoteka_report(1), AutotekaReport)
    assert isinstance(client.autoteka_monitoring(), AutotekaMonitoring)
    assert isinstance(client.autoteka_scoring(1), AutotekaScoring)
    assert isinstance(client.autoteka_valuation(), AutotekaValuation)
    assert isinstance(client.realty_listing(1), RealtyListing)
    assert isinstance(client.realty_booking(1), RealtyBooking)
    assert isinstance(client.realty_pricing(1), RealtyPricing)
    assert isinstance(client.realty_analytics_report(1), RealtyAnalyticsReport)
    assert isinstance(client.review(), Review)
    assert isinstance(client.review_answer(1), ReviewAnswer)
    assert isinstance(client.rating_profile(), RatingProfile)
    assert isinstance(client.tariff(1), Tariff)


def test_client_exposes_read_only_summary_methods() -> None:
    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )

    assert isinstance(client.capabilities(), CapabilityDiscoveryResult)
    assert hasattr(client, "business_summary")
    assert hasattr(client, "account_health")
    assert hasattr(client, "listing_health")
    assert hasattr(client, "chat_summary")
    assert hasattr(client, "order_summary")
    assert hasattr(client, "review_summary")
    assert hasattr(client, "promotion_summary")

    client.close()


def test_listing_health_combines_listing_stats_calls_and_spendings() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/core/v1/items":
            assert request.url.params["user_id"] == "7"
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 101,
                            "title": "Смартфон",
                            "status": "active",
                            "price": 1000,
                            "url": "https://www.avito.ru/item",
                            "visible": True,
                        }
                    ],
                    "total": 1,
                },
            )
        if request.url.path == "/stats/v1/accounts/7/items":
            return httpx.Response(
                200,
                json={"items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]},
            )
        if request.url.path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(200, json={"items": [{"item_id": 101, "calls": 3}]})
        if request.url.path == "/stats/v2/accounts/7/spendings":
            return httpx.Response(200, json={"items": [{"item_id": 101, "amount": 77.5}]})
        raise AssertionError(request.url.path)

    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )
    client.transport = make_transport(httpx.MockTransport(handler), user_id=7)

    summary = client.listing_health()

    assert isinstance(summary, ListingHealthSummary)
    assert summary.total_listings == 1
    assert summary.active_listings == 1
    assert summary.visible_listings == 1
    assert summary.total_views == 45
    assert summary.total_calls == 3
    assert summary.total_spendings == 77.5
    assert summary.items[0].title == "Смартфон"
    client.close()


def test_account_health_builds_final_business_summary() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/core/v1/accounts/7/balance/":
            return httpx.Response(200, json={"user_id": 7, "real": 100, "bonus": 25, "total": 125})
        if path == "/core/v1/items":
            return httpx.Response(200, json={"items": [{"id": 101, "status": "active"}], "total": 1})
        if path == "/stats/v1/accounts/7/items":
            return httpx.Response(200, json={"items": [{"item_id": 101, "views": 10}]})
        if path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(200, json={"items": [{"item_id": 101, "calls": 2}]})
        if path == "/stats/v2/accounts/7/spendings":
            return httpx.Response(200, json={"items": [{"item_id": 101, "amount": 15.5}]})
        if path == "/messenger/v2/accounts/7/chats":
            return httpx.Response(
                200,
                json={"chats": [{"id": "c1", "unreadCount": 4}, {"id": "c2", "unreadCount": 0}]},
            )
        if path == "/order-management/1/orders":
            return httpx.Response(
                200,
                json={"orders": [{"id": "o1", "status": "new"}, {"id": "o2", "status": "unknown"}]},
            )
        if path == "/ratings/v1/reviews":
            return httpx.Response(
                200,
                json={
                    "total": 2,
                    "reviews": [
                        {"id": 1, "score": 5, "canAnswer": True},
                        {"id": 2, "score": 3, "canAnswer": False},
                    ],
                },
            )
        if path == "/ratings/v1/info":
            return httpx.Response(200, json={"isEnabled": True, "rating": {"score": 4.5}})
        if path == "/promotion/v1/items/services/orders/get":
            return httpx.Response(200, json={"orders": [{"orderId": "p1", "status": "applied"}]})
        if path == "/promotion/v1/items/services/get":
            return httpx.Response(
                200,
                json={"services": [{"itemId": 101, "status": "available"}]},
            )
        raise AssertionError(path)

    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )
    client.transport = make_transport(httpx.MockTransport(handler), user_id=7)

    summary = client.business_summary()

    assert isinstance(summary, AccountHealthSummary)
    assert summary.balance_total == 125
    assert summary.listings.total_views == 10
    assert summary.chats is not None
    assert summary.chats.unread_messages == 4
    assert summary.orders is not None
    assert summary.orders.active_orders == 1
    assert summary.reviews is not None
    assert summary.reviews.average_score == 4
    assert summary.promotion is not None
    assert summary.promotion.available_services == 1
    client.close()


def test_package_exports_auth_settings_as_public_config_contract() -> None:
    assert AuthSettings.__name__ == "AuthSettings"


def test_removed_legacy_factory_names_are_absent() -> None:
    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )

    with pytest.raises(AttributeError):
        _ = client.autoload_legacy  # type: ignore[attr-defined]

    with pytest.raises(AttributeError):
        _ = client.cpa_legacy  # type: ignore[attr-defined]


def test_debug_info_and_context_manager_do_not_leak_secrets() -> None:
    transport_http_client = httpx.Client()
    token_http_client = httpx.Client()
    alternate_http_client = httpx.Client()
    autoteka_http_client = httpx.Client()

    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(client_id="client-id", client_secret="super-secret"),
    )
    auth_provider = AuthProvider(
        settings.auth,
        token_client=TokenClient(settings.auth, client=token_http_client),
        alternate_token_client=AlternateTokenClient(settings.auth, client=alternate_http_client),
        autoteka_token_client=TokenClient(settings.auth, client=autoteka_http_client),
    )
    client = AvitoClient(settings)
    client.transport = Transport(settings, auth_provider=auth_provider, client=transport_http_client)
    client.auth_provider = auth_provider

    info = client.debug_info()
    assert info.requires_auth is True
    assert "secret" not in repr(info).lower()

    with client as managed_client:
        assert managed_client.debug_info().requires_auth is True

    assert transport_http_client.is_closed is True
    assert token_http_client.is_closed is True
    assert alternate_http_client.is_closed is True
    assert autoteka_http_client.is_closed is True


def test_auth_token_clients_use_explicit_sdk_timeouts() -> None:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        timeouts=ApiTimeouts(connect=2.5, read=11.0, write=13.0, pool=3.0),
        auth=AuthSettings(client_id="client-id", client_secret="super-secret"),
    )

    client = AvitoClient(settings)
    token_timeout = client.auth_provider.token_flow().client.timeout
    alternate_timeout = client.auth_provider.alternate_token_flow().client.timeout
    autoteka_timeout = client.auth_provider.autoteka_token_client.client.timeout

    assert token_timeout.connect == 2.5
    assert token_timeout.read == 11.0
    assert token_timeout.write == 13.0
    assert token_timeout.pool == 3.0
    assert alternate_timeout.connect == 2.5
    assert alternate_timeout.read == 11.0
    assert alternate_timeout.write == 13.0
    assert alternate_timeout.pool == 3.0
    assert autoteka_timeout.connect == 2.5
    assert autoteka_timeout.read == 11.0
    assert autoteka_timeout.write == 13.0
    assert autoteka_timeout.pool == 3.0

    client.close()


def test_closed_client_rejects_new_domain_factories() -> None:
    client = AvitoClient(
        AvitoSettings(auth=AuthSettings(client_id="client-id", client_secret="client-secret"))
    )

    client.close()

    with pytest.raises(ConfigurationError, match="Клиент закрыт"):
        client.account()
