"""Внутренние section clients для пакета messenger."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.messenger.mappers import (
    map_available_special_offers,
    map_chat,
    map_chats,
    map_message_action,
    map_messages,
    map_multi_create_result,
    map_special_offer_stats,
    map_subscriptions,
    map_tariff_info,
    map_upload_images,
    map_voice_files,
    map_webhook_action,
)
from avito.messenger.models import (
    BlacklistRequest,
    ChatInfo,
    ChatsResult,
    MessageActionResult,
    MessagesResult,
    MultiConfirmSpecialOfferRequest,
    MultiCreateSpecialOfferRequest,
    MultiCreateSpecialOfferResult,
    SendImageMessageRequest,
    SendMessageRequest,
    SpecialOfferAvailableRequest,
    SpecialOfferAvailableResult,
    SpecialOfferStatsRequest,
    SpecialOfferStatsResult,
    SubscriptionsResult,
    TariffInfo,
    UnsubscribeWebhookRequest,
    UpdateWebhookRequest,
    UploadImagesResult,
    VoiceFilesResult,
    WebhookActionResult,
)


@dataclass(slots=True)
class MessengerClient:
    """Выполняет HTTP-операции чатов и сообщений."""

    transport: Transport

    def list_chats(self, *, user_id: int) -> ChatsResult:
        """Получает список чатов пользователя."""

        payload = self.transport.request_json(
            "GET",
            f"/messenger/v2/accounts/{user_id}/chats",
            context=RequestContext("messenger.list_chats"),
        )
        return map_chats(payload)

    def get_chat(self, *, user_id: int, chat_id: str) -> ChatInfo:
        """Получает информацию по чату."""

        payload = self.transport.request_json(
            "GET",
            f"/messenger/v2/accounts/{user_id}/chats/{chat_id}",
            context=RequestContext("messenger.get_chat"),
        )
        return map_chat(payload)

    def read_chat(self, *, user_id: int, chat_id: str) -> MessageActionResult:
        """Помечает чат как прочитанный."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/read",
            context=RequestContext("messenger.read_chat", allow_retry=True),
        )
        return map_message_action(payload)

    def add_to_blacklist(self, *, user_id: int, request: BlacklistRequest) -> MessageActionResult:
        """Добавляет пользователя в blacklist."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v2/accounts/{user_id}/blacklist",
            context=RequestContext("messenger.add_to_blacklist", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_message_action(payload)

    def send_message(
        self, *, user_id: int, chat_id: str, request: SendMessageRequest
    ) -> MessageActionResult:
        """Отправляет текстовое сообщение."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages",
            context=RequestContext("messenger.send_message", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_message_action(payload)

    def send_image_message(
        self, *, user_id: int, chat_id: str, request: SendImageMessageRequest
    ) -> MessageActionResult:
        """Отправляет сообщение с изображением."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image",
            context=RequestContext("messenger.send_image_message", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_message_action(payload)

    def delete_message(self, *, user_id: int, chat_id: str, message_id: str) -> MessageActionResult:
        """Удаляет сообщение."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}",
            context=RequestContext("messenger.delete_message", allow_retry=True),
        )
        return map_message_action(payload)

    def list_messages(self, *, user_id: int, chat_id: str) -> MessagesResult:
        """Получает список сообщений V3."""

        payload = self.transport.request_json(
            "GET",
            f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/",
            context=RequestContext("messenger.list_messages"),
        )
        return map_messages(payload)


@dataclass(slots=True)
class WebhookClient:
    """Выполняет HTTP-операции webhook мессенджера."""

    transport: Transport

    def get_subscriptions(self) -> SubscriptionsResult:
        """Получает список подписок webhook."""

        payload = self.transport.request_json(
            "POST",
            "/messenger/v1/subscriptions",
            context=RequestContext("messenger.webhook.get_subscriptions", allow_retry=True),
        )
        return map_subscriptions(payload)

    def unsubscribe(self, request: UnsubscribeWebhookRequest) -> WebhookActionResult:
        """Отключает webhook."""

        payload = self.transport.request_json(
            "POST",
            "/messenger/v1/webhook/unsubscribe",
            context=RequestContext("messenger.webhook.unsubscribe", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_webhook_action(payload)

    def update_v3(self, request: UpdateWebhookRequest) -> WebhookActionResult:
        """Включает уведомления webhook v3."""

        payload = self.transport.request_json(
            "POST",
            "/messenger/v3/webhook",
            context=RequestContext("messenger.webhook.update_v3", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_webhook_action(payload)


@dataclass(slots=True)
class MediaClient:
    """Выполняет HTTP-операции media uploads и voice files."""

    transport: Transport

    def get_voice_files(self, *, user_id: int) -> VoiceFilesResult:
        """Получает голосовые сообщения."""

        payload = self.transport.request_json(
            "GET",
            f"/messenger/v1/accounts/{user_id}/getVoiceFiles",
            context=RequestContext("messenger.media.get_voice_files"),
        )
        return map_voice_files(payload)

    def upload_images(
        self,
        *,
        user_id: int,
        files: dict[str, object],
    ) -> UploadImagesResult:
        """Загружает изображения для сообщений."""

        payload = self.transport.request_json(
            "POST",
            f"/messenger/v1/accounts/{user_id}/uploadImages",
            context=RequestContext("messenger.media.upload_images", allow_retry=True),
            files=files,
        )
        return map_upload_images(payload)


@dataclass(slots=True)
class SpecialOffersClient:
    """Выполняет HTTP-операции рассылок скидок и спецпредложений."""

    transport: Transport

    def get_available(self, request: SpecialOfferAvailableRequest) -> SpecialOfferAvailableResult:
        """Получает доступные объявления для рассылки."""

        payload = self.transport.request_json(
            "POST",
            "/special-offers/v1/available",
            context=RequestContext("messenger.special_offers.get_available", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_available_special_offers(payload)

    def create_multi(
        self, request: MultiCreateSpecialOfferRequest
    ) -> MultiCreateSpecialOfferResult:
        """Создает рассылку спецпредложений."""

        payload = self.transport.request_json(
            "POST",
            "/special-offers/v1/multiCreate",
            context=RequestContext("messenger.special_offers.create_multi", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_multi_create_result(payload)

    def confirm_multi(self, request: MultiConfirmSpecialOfferRequest) -> WebhookActionResult:
        """Подтверждает и оплачивает рассылку."""

        payload = self.transport.request_json(
            "POST",
            "/special-offers/v1/multiConfirm",
            context=RequestContext("messenger.special_offers.confirm_multi", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_webhook_action(payload)

    def get_stats(self, request: SpecialOfferStatsRequest) -> SpecialOfferStatsResult:
        """Получает статистику рассылки."""

        payload = self.transport.request_json(
            "POST",
            "/special-offers/v1/stats",
            context=RequestContext("messenger.special_offers.get_stats", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_special_offer_stats(payload)

    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе спецпредложений."""

        payload = self.transport.request_json(
            "POST",
            "/special-offers/v1/tariffInfo",
            context=RequestContext("messenger.special_offers.get_tariff_info", allow_retry=True),
        )
        return map_tariff_info(payload)


__all__ = ("MediaClient", "MessengerClient", "SpecialOffersClient", "WebhookClient")
