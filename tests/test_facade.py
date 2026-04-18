from avito import AvitoClient
from avito.accounts import Account, AccountHierarchy
from avito.ads import Ad, AdPromotion, AdStats, AutoloadLegacy, AutoloadProfile, AutoloadReport
from avito.auth import AuthProvider
from avito.autoteka import (
    AutotekaMonitoring,
    AutotekaReport,
    AutotekaScoring,
    AutotekaValuation,
    AutotekaVehicle,
)
from avito.cpa import CallTrackingCall, CpaCall, CpaChat, CpaLead, CpaLegacy
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
from avito.tariffs import Tariff


def test_single_client_exposes_domain_factories() -> None:
    client = AvitoClient()

    assert isinstance(client.auth(), AuthProvider)
    assert isinstance(client.account(1), Account)
    assert isinstance(client.account_hierarchy(1), AccountHierarchy)
    assert isinstance(client.ad(1), Ad)
    assert isinstance(client.ad_stats(1), AdStats)
    assert isinstance(client.ad_promotion(1), AdPromotion)
    assert isinstance(client.autoload_profile(1), AutoloadProfile)
    assert isinstance(client.autoload_report(1), AutoloadReport)
    assert isinstance(client.autoload_legacy(1), AutoloadLegacy)
    assert isinstance(client.chat("chat-1", user_id=1), Chat)
    assert isinstance(client.chat_message("msg-1", chat_id="chat-1", user_id=1), ChatMessage)
    assert isinstance(client.chat_webhook(), ChatWebhook)
    assert isinstance(client.chat_media("media-1", user_id=1), ChatMedia)
    assert isinstance(client.special_offer_campaign(1), SpecialOfferCampaign)
    assert isinstance(client.promotion_order(1), PromotionOrder)
    assert isinstance(client.bbip_promotion(1), BbipPromotion)
    assert isinstance(client.trx_promotion(1), TrxPromotion)
    assert isinstance(client.cpa_auction(1), CpaAuction)
    assert isinstance(client.target_action_pricing(1), TargetActionPricing)
    assert isinstance(client.autostrategy_campaign(1), AutostrategyCampaign)
    assert isinstance(client.order(1), Order)
    assert isinstance(client.order_label(1), OrderLabel)
    assert isinstance(client.delivery_order(1), DeliveryOrder)
    assert isinstance(client.sandbox_delivery(1), SandboxDelivery)
    assert isinstance(client.delivery_task(1), DeliveryTask)
    assert isinstance(client.stock(1), Stock)
    assert isinstance(client.vacancy(1), Vacancy)
    assert isinstance(client.application(1), Application)
    assert isinstance(client.resume(1), Resume)
    assert isinstance(client.job_webhook(), JobWebhook)
    assert isinstance(client.job_dictionary(1), JobDictionary)
    assert isinstance(client.cpa_lead(1), CpaLead)
    assert isinstance(client.cpa_chat(1), CpaChat)
    assert isinstance(client.cpa_call(1), CpaCall)
    assert isinstance(client.cpa_legacy(1), CpaLegacy)
    assert isinstance(client.call_tracking_call(1), CallTrackingCall)
    assert isinstance(client.autoteka_vehicle(1), AutotekaVehicle)
    assert isinstance(client.autoteka_report(1), AutotekaReport)
    assert isinstance(client.autoteka_monitoring(1), AutotekaMonitoring)
    assert isinstance(client.autoteka_scoring(1), AutotekaScoring)
    assert isinstance(client.autoteka_valuation(1), AutotekaValuation)
    assert isinstance(client.realty_listing(1), RealtyListing)
    assert isinstance(client.realty_booking(1), RealtyBooking)
    assert isinstance(client.realty_pricing(1), RealtyPricing)
    assert isinstance(client.realty_analytics_report(1), RealtyAnalyticsReport)
    assert isinstance(client.review(1), Review)
    assert isinstance(client.review_answer(1), ReviewAnswer)
    assert isinstance(client.rating_profile(1), RatingProfile)
    assert isinstance(client.tariff(1), Tariff)
