"""Высокоуровневый единый клиент SDK Avito."""

from __future__ import annotations

import httpx

from avito.accounts import Account, AccountHierarchy
from avito.ads import Ad, AdPromotion, AdStats, AutoloadLegacy, AutoloadProfile, AutoloadReport
from avito.auth import AuthProvider, LegacyTokenClient, TokenClient
from avito.autoteka import (
    AutotekaMonitoring,
    AutotekaReport,
    AutotekaScoring,
    AutotekaValuation,
    AutotekaVehicle,
)
from avito.config import AvitoSettings
from avito.core import Transport, TransportDebugInfo
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


class AvitoClient:
    """Единственная публичная точка входа SDK с фабриками доменных объектов.

    Пример:
        ```python
        from avito import AvitoClient

        with AvitoClient() as avito:
            profile = avito.account().get_self()
            ad = avito.ad(42).get()
        ```
    """

    def __init__(self, settings: AvitoSettings | None = None) -> None:
        self.settings = settings or AvitoSettings.from_env()
        self.auth_provider = self._build_auth_provider()
        self.transport = Transport(self.settings, auth_provider=self.auth_provider)

    def auth(self) -> AuthProvider:
        """Возвращает объект аутентификации и token-flow операций."""

        return self.auth_provider

    def debug_info(self) -> TransportDebugInfo:
        """Возвращает безопасный снимок transport-настроек для диагностики."""

        return self.transport.debug_info()

    def close(self) -> None:
        """Закрывает внутренние HTTP-клиенты SDK."""

        self.transport.close()
        self.auth_provider.close()

    def __enter__(self) -> AvitoClient:
        """Открывает клиент как контекстный менеджер."""

        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        """Закрывает клиент при выходе из контекстного менеджера."""

        self.close()

    def _build_auth_provider(self) -> AuthProvider:
        token_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        legacy_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        autoteka_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        return AuthProvider(
            self.settings.auth,
            token_client=TokenClient(self.settings.auth, client=token_http_client),
            legacy_token_client=LegacyTokenClient(self.settings.auth, client=legacy_http_client),
            autoteka_token_client=TokenClient(
                self.settings.auth,
                token_url=self.settings.auth.autoteka_token_url,
                client=autoteka_http_client,
            ),
        )

    def account(self, user_id: int | str | None = None) -> Account:
        """Создает доменный объект аккаунта."""

        return Account(self.transport, resource_id=user_id, user_id=user_id)

    def account_hierarchy(self, user_id: int | str | None = None) -> AccountHierarchy:
        """Создает доменный объект иерархии аккаунта."""

        return AccountHierarchy(self.transport, resource_id=user_id, user_id=user_id)

    def ad(self, item_id: int | str | None = None, user_id: int | str | None = None) -> Ad:
        """Создает доменный объект объявления."""

        return Ad(self.transport, resource_id=item_id, user_id=user_id)

    def ad_stats(
        self, item_id: int | str | None = None, user_id: int | str | None = None
    ) -> AdStats:
        """Создает доменный объект статистики объявления."""

        return AdStats(self.transport, resource_id=item_id, user_id=user_id)

    def ad_promotion(
        self, item_id: int | str | None = None, user_id: int | str | None = None
    ) -> AdPromotion:
        """Создает доменный объект продвижения объявления."""

        return AdPromotion(self.transport, resource_id=item_id, user_id=user_id)

    def autoload_profile(self, user_id: int | str | None = None) -> AutoloadProfile:
        """Создает доменный объект профиля автозагрузки."""

        return AutoloadProfile(self.transport, resource_id=user_id, user_id=user_id)

    def autoload_report(self, report_id: int | str | None = None) -> AutoloadReport:
        """Создает доменный объект отчета автозагрузки."""

        return AutoloadReport(self.transport, resource_id=report_id)

    def autoload_legacy(self, report_id: int | str | None = None) -> AutoloadLegacy:
        """Создает доменный объект legacy-операций автозагрузки."""

        return AutoloadLegacy(self.transport, resource_id=report_id)

    def chat(self, chat_id: int | str | None = None, *, user_id: int | str | None = None) -> Chat:
        """Создает доменный объект чата."""

        return Chat(self.transport, resource_id=chat_id, user_id=user_id)

    def chat_message(
        self,
        message_id: int | str | None = None,
        *,
        chat_id: int | str | None = None,
        user_id: int | str | None = None,
    ) -> ChatMessage:
        """Создает доменный объект сообщения чата."""

        resource_id = message_id if message_id is not None else chat_id
        return ChatMessage(self.transport, resource_id=resource_id, user_id=user_id)

    def chat_webhook(self) -> ChatWebhook:
        """Создает доменный объект webhook мессенджера."""

        return ChatWebhook(self.transport)

    def chat_media(
        self, media_id: int | str | None = None, *, user_id: int | str | None = None
    ) -> ChatMedia:
        """Создает доменный объект медиа мессенджера."""

        return ChatMedia(self.transport, resource_id=media_id, user_id=user_id)

    def special_offer_campaign(self, campaign_id: int | str | None = None) -> SpecialOfferCampaign:
        """Создает доменный объект рассылки спецпредложений."""

        return SpecialOfferCampaign(self.transport, resource_id=campaign_id)

    def promotion_order(self, order_id: int | str | None = None) -> PromotionOrder:
        """Создает доменный объект заявки на продвижение."""

        return PromotionOrder(self.transport, resource_id=order_id)

    def bbip_promotion(self, item_id: int | str | None = None) -> BbipPromotion:
        """Создает доменный объект BBIP-продвижения."""

        return BbipPromotion(self.transport, resource_id=item_id)

    def trx_promotion(self, item_id: int | str | None = None) -> TrxPromotion:
        """Создает доменный объект TrxPromo."""

        return TrxPromotion(self.transport, resource_id=item_id)

    def cpa_auction(self, item_id: int | str | None = None) -> CpaAuction:
        """Создает доменный объект CPA-аукциона."""

        return CpaAuction(self.transport, resource_id=item_id)

    def target_action_pricing(self, item_id: int | str | None = None) -> TargetActionPricing:
        """Создает доменный объект цены целевого действия."""

        return TargetActionPricing(self.transport, resource_id=item_id)

    def autostrategy_campaign(self, campaign_id: int | str | None = None) -> AutostrategyCampaign:
        """Создает доменный объект автостратегии."""

        return AutostrategyCampaign(self.transport, resource_id=campaign_id)

    def order(self, order_id: int | str | None = None) -> Order:
        """Создает доменный объект заказа."""

        return Order(self.transport, resource_id=order_id)

    def order_label(self, task_id: int | str | None = None) -> OrderLabel:
        """Создает доменный объект этикетки заказа."""

        return OrderLabel(self.transport, resource_id=task_id)

    def delivery_order(self, order_id: int | str | None = None) -> DeliveryOrder:
        """Создает доменный объект доставки."""

        return DeliveryOrder(self.transport, resource_id=order_id)

    def sandbox_delivery(self, task_id: int | str | None = None) -> SandboxDelivery:
        """Создает доменный объект песочницы доставки."""

        return SandboxDelivery(self.transport, resource_id=task_id)

    def delivery_task(self, task_id: int | str | None = None) -> DeliveryTask:
        """Создает доменный объект задачи доставки."""

        return DeliveryTask(self.transport, resource_id=task_id)

    def stock(self, stock_id: int | str | None = None) -> Stock:
        """Создает доменный объект остатков."""

        return Stock(self.transport, resource_id=stock_id)

    def vacancy(self, vacancy_id: int | str | None = None) -> Vacancy:
        """Создает доменный объект вакансии."""

        return Vacancy(self.transport, resource_id=vacancy_id)

    def application(self, application_id: int | str | None = None) -> Application:
        """Создает доменный объект отклика."""

        return Application(self.transport, resource_id=application_id)

    def resume(self, resume_id: int | str | None = None) -> Resume:
        """Создает доменный объект резюме."""

        return Resume(self.transport, resource_id=resume_id)

    def job_webhook(self) -> JobWebhook:
        """Создает доменный объект webhook раздела Работа."""

        return JobWebhook(self.transport)

    def job_dictionary(self, dictionary_id: int | str | None = None) -> JobDictionary:
        """Создает доменный объект словаря Работа."""

        return JobDictionary(self.transport, resource_id=dictionary_id)

    def cpa_lead(self, lead_id: int | str | None = None) -> CpaLead:
        """Создает доменный объект CPA-лида."""

        return CpaLead(self.transport, resource_id=lead_id)

    def cpa_chat(self, chat_id: int | str | None = None) -> CpaChat:
        """Создает доменный объект CPA-чата."""

        return CpaChat(self.transport, resource_id=chat_id)

    def cpa_call(self, call_id: int | str | None = None) -> CpaCall:
        """Создает доменный объект CPA-звонка."""

        return CpaCall(self.transport, resource_id=call_id)

    def cpa_legacy(self, legacy_id: int | str | None = None) -> CpaLegacy:
        """Создает доменный объект legacy-операций CPA."""

        return CpaLegacy(self.transport, resource_id=legacy_id)

    def call_tracking_call(self, call_id: int | str | None = None) -> CallTrackingCall:
        """Создает доменный объект CallTracking."""

        return CallTrackingCall(self.transport, resource_id=call_id)

    def autoteka_vehicle(self, vehicle_id: int | str | None = None) -> AutotekaVehicle:
        """Создает доменный объект транспортного средства Автотеки."""

        return AutotekaVehicle(self.transport, resource_id=vehicle_id)

    def autoteka_report(self, report_id: int | str | None = None) -> AutotekaReport:
        """Создает доменный объект отчета Автотеки."""

        return AutotekaReport(self.transport, resource_id=report_id)

    def autoteka_monitoring(self, monitoring_id: int | str | None = None) -> AutotekaMonitoring:
        """Создает доменный объект мониторинга Автотеки."""

        return AutotekaMonitoring(self.transport, resource_id=monitoring_id)

    def autoteka_scoring(self, scoring_id: int | str | None = None) -> AutotekaScoring:
        """Создает доменный объект скоринга Автотеки."""

        return AutotekaScoring(self.transport, resource_id=scoring_id)

    def autoteka_valuation(self, valuation_id: int | str | None = None) -> AutotekaValuation:
        """Создает доменный объект оценки Автотеки."""

        return AutotekaValuation(self.transport, resource_id=valuation_id)

    def realty_listing(self, item_id: int | str | None = None) -> RealtyListing:
        """Создает доменный объект объявления недвижимости."""

        return RealtyListing(self.transport, resource_id=item_id)

    def realty_booking(self, booking_id: int | str | None = None) -> RealtyBooking:
        """Создает доменный объект бронирования недвижимости."""

        return RealtyBooking(self.transport, resource_id=booking_id)

    def realty_pricing(self, item_id: int | str | None = None) -> RealtyPricing:
        """Создает доменный объект цен недвижимости."""

        return RealtyPricing(self.transport, resource_id=item_id)

    def realty_analytics_report(self, report_id: int | str | None = None) -> RealtyAnalyticsReport:
        """Создает доменный объект аналитического отчета недвижимости."""

        return RealtyAnalyticsReport(self.transport, resource_id=report_id)

    def review(self, review_id: int | str | None = None) -> Review:
        """Создает доменный объект отзыва."""

        return Review(self.transport, resource_id=review_id)

    def review_answer(self, answer_id: int | str | None = None) -> ReviewAnswer:
        """Создает доменный объект ответа на отзыв."""

        return ReviewAnswer(self.transport, resource_id=answer_id)

    def rating_profile(self, profile_id: int | str | None = None) -> RatingProfile:
        """Создает доменный объект рейтингового профиля."""

        return RatingProfile(self.transport, resource_id=profile_id)

    def tariff(self, tariff_id: int | str | None = None) -> Tariff:
        """Создает доменный объект тарифа."""

        return Tariff(self.transport, resource_id=tariff_id)


__all__ = ("AvitoClient",)
