"""Высокоуровневый единый клиент SDK Avito."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType

import httpx

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
from avito.config import AvitoSettings
from avito.core import Transport, TransportDebugInfo
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

    def __init__(
        self,
        settings: AvitoSettings | None = None,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        if client_id is not None or client_secret is not None:
            from avito.auth.settings import AuthSettings

            auth = AuthSettings(client_id=client_id, client_secret=client_secret)
            settings = AvitoSettings(auth=auth)
        self.settings = (settings or AvitoSettings.from_env()).validate_required()
        self.auth_provider = self._build_auth_provider()
        self.transport = Transport(self.settings, auth_provider=self.auth_provider)

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = ".env") -> AvitoClient:
        """Создает клиент из переменных окружения и optional `.env` файла."""

        return cls(AvitoSettings.from_env(env_file=env_file))

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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Закрывает клиент при выходе из контекстного менеджера."""

        self.close()

    def _build_auth_provider(self) -> AuthProvider:
        token_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        alternate_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        autoteka_http_client = httpx.Client(base_url=self.settings.base_url.rstrip("/"))
        return AuthProvider(
            self.settings.auth,
            token_client=TokenClient(self.settings.auth, client=token_http_client),
            alternate_token_client=AlternateTokenClient(
                self.settings.auth, client=alternate_http_client
            ),
            autoteka_token_client=TokenClient(
                self.settings.auth,
                token_url=self.settings.auth.autoteka_token_url,
                client=autoteka_http_client,
            ),
        )

    def account(self, user_id: int | str | None = None) -> Account:
        """Создает доменный объект аккаунта."""

        return Account(self.transport, user_id=user_id)

    def account_hierarchy(self, user_id: int | str | None = None) -> AccountHierarchy:
        """Создает доменный объект иерархии аккаунта."""

        return AccountHierarchy(self.transport, user_id=user_id)

    def ad(self, item_id: int | str | None = None, user_id: int | str | None = None) -> Ad:
        """Создает доменный объект объявления."""

        return Ad(self.transport, item_id=item_id, user_id=user_id)

    def ad_stats(
        self, item_id: int | str | None = None, user_id: int | str | None = None
    ) -> AdStats:
        """Создает доменный объект статистики объявления."""

        return AdStats(self.transport, item_id=item_id, user_id=user_id)

    def ad_promotion(
        self, item_id: int | str | None = None, user_id: int | str | None = None
    ) -> AdPromotion:
        """Создает доменный объект продвижения объявления."""

        return AdPromotion(self.transport, item_id=item_id, user_id=user_id)

    def autoload_profile(self, user_id: int | str | None = None) -> AutoloadProfile:
        """Создает доменный объект профиля автозагрузки."""

        return AutoloadProfile(self.transport, user_id=user_id)

    def autoload_report(self, report_id: int | str | None = None) -> AutoloadReport:
        """Создает доменный объект отчета автозагрузки."""

        return AutoloadReport(self.transport, report_id=report_id)

    def autoload_archive(self, report_id: int | str | None = None) -> AutoloadArchive:
        """Создает доменный объект архивных операций автозагрузки."""

        return AutoloadArchive(self.transport, report_id=report_id)

    def chat(self, chat_id: int | str | None = None, *, user_id: int | str | None = None) -> Chat:
        """Создает доменный объект чата."""

        return Chat(self.transport, chat_id=chat_id, user_id=user_id)

    def chat_message(
        self,
        message_id: int | str | None = None,
        *,
        chat_id: int | str | None = None,
        user_id: int | str | None = None,
    ) -> ChatMessage:
        """Создает доменный объект сообщения чата."""

        return ChatMessage(self.transport, chat_id=chat_id, message_id=message_id, user_id=user_id)

    def chat_webhook(self) -> ChatWebhook:
        """Создает доменный объект webhook мессенджера."""

        return ChatWebhook(self.transport)

    def chat_media(
        self,
        media_id: int | str | None = None,
        *,
        user_id: int | str | None = None,
    ) -> ChatMedia:
        """Создает доменный объект медиа мессенджера."""

        _ = media_id
        return ChatMedia(self.transport, user_id=user_id)

    def special_offer_campaign(self, campaign_id: int | str | None = None) -> SpecialOfferCampaign:
        """Создает доменный объект рассылки спецпредложений."""

        return SpecialOfferCampaign(self.transport, campaign_id=campaign_id)

    def promotion_order(self, order_id: int | str | None = None) -> PromotionOrder:
        """Создает доменный объект заявки на продвижение."""

        return PromotionOrder(self.transport, order_id=order_id)

    def bbip_promotion(self, item_id: int | str | None = None) -> BbipPromotion:
        """Создает доменный объект BBIP-продвижения."""

        return BbipPromotion(self.transport, item_id=item_id)

    def trx_promotion(self, item_id: int | str | None = None) -> TrxPromotion:
        """Создает доменный объект TrxPromo."""

        return TrxPromotion(self.transport, item_id=item_id)

    def cpa_auction(self, item_id: int | str | None = None) -> CpaAuction:
        """Создает доменный объект CPA-аукциона."""

        return CpaAuction(self.transport, item_id=item_id)

    def target_action_pricing(self, item_id: int | str | None = None) -> TargetActionPricing:
        """Создает доменный объект цены целевого действия."""

        return TargetActionPricing(self.transport, item_id=item_id)

    def autostrategy_campaign(self, campaign_id: int | str | None = None) -> AutostrategyCampaign:
        """Создает доменный объект автостратегии."""

        return AutostrategyCampaign(self.transport, campaign_id=campaign_id)

    def order(self, order_id: int | str | None = None) -> Order:
        """Создает доменный объект заказа."""

        _ = order_id
        return Order(self.transport)

    def order_label(self, task_id: int | str | None = None) -> OrderLabel:
        """Создает доменный объект этикетки заказа."""

        return OrderLabel(self.transport, task_id=task_id)

    def delivery_order(self, order_id: int | str | None = None) -> DeliveryOrder:
        """Создает доменный объект доставки."""

        _ = order_id
        return DeliveryOrder(self.transport)

    def sandbox_delivery(self, sandbox_id: int | str | None = None) -> SandboxDelivery:
        """Создает доменный объект песочницы доставки."""

        _ = sandbox_id
        return SandboxDelivery(self.transport)

    def delivery_task(self, task_id: int | str | None = None) -> DeliveryTask:
        """Создает доменный объект задачи доставки."""

        return DeliveryTask(self.transport, task_id=task_id)

    def stock(self, stock_id: int | str | None = None) -> Stock:
        """Создает доменный объект остатков."""

        _ = stock_id
        return Stock(self.transport)

    def vacancy(self, vacancy_id: int | str | None = None) -> Vacancy:
        """Создает доменный объект вакансии."""

        return Vacancy(self.transport, vacancy_id=vacancy_id)

    def application(self, application_id: int | str | None = None) -> Application:
        """Создает доменный объект отклика."""

        _ = application_id
        return Application(self.transport)

    def resume(self, resume_id: int | str | None = None) -> Resume:
        """Создает доменный объект резюме."""

        return Resume(self.transport, resume_id=resume_id)

    def job_webhook(self) -> JobWebhook:
        """Создает доменный объект webhook раздела Работа."""

        return JobWebhook(self.transport)

    def job_dictionary(self, dictionary_id: int | str | None = None) -> JobDictionary:
        """Создает доменный объект словаря Работа."""

        return JobDictionary(self.transport, dictionary_id=dictionary_id)

    def cpa_lead(self, lead_id: int | str | None = None) -> CpaLead:
        """Создает доменный объект CPA-лида."""

        _ = lead_id
        return CpaLead(self.transport)

    def cpa_chat(self, chat_id: int | str | None = None) -> CpaChat:
        """Создает доменный объект CPA-чата."""

        return CpaChat(self.transport, action_id=chat_id)

    def cpa_call(self, call_id: int | str | None = None) -> CpaCall:
        """Создает доменный объект CPA-звонка."""

        _ = call_id
        return CpaCall(self.transport)

    def cpa_archive(self, call_id: int | str | None = None) -> CpaArchive:
        """Создает доменный объект архивных операций CPA."""

        return CpaArchive(self.transport, call_id=call_id)

    def call_tracking_call(self, call_id: int | str | None = None) -> CallTrackingCall:
        """Создает доменный объект CallTracking."""

        return CallTrackingCall(self.transport, call_id=call_id)

    def autoteka_vehicle(self, vehicle_id: int | str | None = None) -> AutotekaVehicle:
        """Создает доменный объект транспортного средства Автотеки."""

        return AutotekaVehicle(self.transport, vehicle_id=vehicle_id)

    def autoteka_report(self, report_id: int | str | None = None) -> AutotekaReport:
        """Создает доменный объект отчета Автотеки."""

        return AutotekaReport(self.transport, report_id=report_id)

    def autoteka_monitoring(self, monitoring_id: int | str | None = None) -> AutotekaMonitoring:
        """Создает доменный объект мониторинга Автотеки."""

        _ = monitoring_id
        return AutotekaMonitoring(self.transport)

    def autoteka_scoring(self, scoring_id: int | str | None = None) -> AutotekaScoring:
        """Создает доменный объект скоринга Автотеки."""

        return AutotekaScoring(self.transport, scoring_id=scoring_id)

    def autoteka_valuation(self, valuation_id: int | str | None = None) -> AutotekaValuation:
        """Создает доменный объект оценки Автотеки."""

        _ = valuation_id
        return AutotekaValuation(self.transport)

    def realty_listing(
        self,
        item_id: int | str | None = None,
        *,
        user_id: int | str | None = None,
    ) -> RealtyListing:
        """Создает доменный объект объявления недвижимости."""

        return RealtyListing(self.transport, item_id=item_id, user_id=user_id)

    def realty_booking(
        self,
        item_id: int | str | None = None,
        *,
        user_id: int | str | None = None,
    ) -> RealtyBooking:
        """Создает доменный объект бронирования недвижимости."""

        return RealtyBooking(self.transport, item_id=item_id, user_id=user_id)

    def realty_pricing(
        self,
        item_id: int | str | None = None,
        *,
        user_id: int | str | None = None,
    ) -> RealtyPricing:
        """Создает доменный объект цен недвижимости."""

        return RealtyPricing(self.transport, item_id=item_id, user_id=user_id)

    def realty_analytics_report(
        self,
        item_id: int | str | None = None,
        *,
        user_id: int | str | None = None,
    ) -> RealtyAnalyticsReport:
        """Создает доменный объект аналитического отчета недвижимости."""

        return RealtyAnalyticsReport(self.transport, item_id=item_id, user_id=user_id)

    def review(self, review_id: int | str | None = None) -> Review:
        """Создает доменный объект отзыва."""

        _ = review_id
        return Review(self.transport)

    def review_answer(self, answer_id: int | str | None = None) -> ReviewAnswer:
        """Создает доменный объект ответа на отзыв."""

        return ReviewAnswer(self.transport, answer_id=answer_id)

    def rating_profile(self, profile_id: int | str | None = None) -> RatingProfile:
        """Создает доменный объект рейтингового профиля."""

        _ = profile_id
        return RatingProfile(self.transport)

    def tariff(self, tariff_id: int | str | None = None) -> Tariff:
        """Создает доменный объект тарифа."""

        return Tariff(self.transport, tariff_id=tariff_id)


__all__ = ("AvitoClient",)
