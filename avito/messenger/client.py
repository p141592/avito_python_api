"""Внутренние section clients для пакета messenger."""

from __future__ import annotations

from collections.abc import Sequence
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
    UploadImageFile,
    UploadImagesRequest,
    UploadImagesResult,
    VoiceFilesResult,
    WebhookActionResult,
)


@dataclass(slots=True, frozen=True)
class MessengerClient:
    """Выполняет HTTP-операции чатов и сообщений."""

    transport: Transport

    def list_chats(self, *, user_id: int) -> ChatsResult:
        """Получает список чатов пользователя."""

        return self.transport.request_public_model(
            "GET",
            f"/messenger/v2/accounts/{user_id}/chats",
            context=RequestContext("messenger.list_chats"),
            mapper=map_chats,
        )

    def get_chat(self, *, user_id: int, chat_id: str) -> ChatInfo:
        """Получает информацию по чату."""

        return self.transport.request_public_model(
            "GET",
            f"/messenger/v2/accounts/{user_id}/chats/{chat_id}",
            context=RequestContext("messenger.get_chat"),
            mapper=map_chat,
        )

    def read_chat(
        self,
        *,
        user_id: int,
        chat_id: str,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Помечает чат как прочитанный."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/read",
            context=RequestContext("messenger.read_chat", allow_retry=idempotency_key is not None),
            mapper=map_message_action,
            idempotency_key=idempotency_key,
        )

    def add_to_blacklist(
        self, *, user_id: int, blacklisted_user_id: int, idempotency_key: str | None = None
    ) -> MessageActionResult:
        """Добавляет пользователя в blacklist."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v2/accounts/{user_id}/blacklist",
            context=RequestContext(
                "messenger.add_to_blacklist",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_message_action,
            json_body=BlacklistRequest(blacklisted_user_id=blacklisted_user_id).to_payload(),
            idempotency_key=idempotency_key,
        )

    def send_message(
        self, *, user_id: int, chat_id: str, message: str, idempotency_key: str | None = None
    ) -> MessageActionResult:
        """Отправляет текстовое сообщение."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages",
            context=RequestContext("messenger.send_message", allow_retry=idempotency_key is not None),
            mapper=map_message_action,
            json_body=SendMessageRequest(message=message).to_payload(),
            idempotency_key=idempotency_key,
        )

    def send_image_message(
        self,
        *,
        user_id: int,
        chat_id: str,
        image_id: str,
        caption: str | None = None,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Отправляет сообщение с изображением."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image",
            context=RequestContext(
                "messenger.send_image_message",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_message_action,
            json_body=SendImageMessageRequest(image_id=image_id, caption=caption).to_payload(),
            idempotency_key=idempotency_key,
        )

    def delete_message(
        self,
        *,
        user_id: int,
        chat_id: str,
        message_id: str,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Удаляет сообщение."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}",
            context=RequestContext(
                "messenger.delete_message",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_message_action,
            idempotency_key=idempotency_key,
        )

    def list_messages(self, *, user_id: int, chat_id: str) -> MessagesResult:
        """Получает список сообщений V3."""

        return self.transport.request_public_model(
            "GET",
            f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/",
            context=RequestContext("messenger.list_messages"),
            mapper=map_messages,
        )


@dataclass(slots=True, frozen=True)
class WebhookClient:
    """Выполняет HTTP-операции webhook мессенджера."""

    transport: Transport

    def get_subscriptions(self) -> SubscriptionsResult:
        """Получает список подписок webhook."""

        return self.transport.request_public_model(
            "POST",
            "/messenger/v1/subscriptions",
            context=RequestContext("messenger.webhook.get_subscriptions", allow_retry=True),
            mapper=map_subscriptions,
        )

    def unsubscribe(self, *, url: str, idempotency_key: str | None = None) -> WebhookActionResult:
        """Отключает webhook."""

        return self.transport.request_public_model(
            "POST",
            "/messenger/v1/webhook/unsubscribe",
            context=RequestContext(
                "messenger.webhook.unsubscribe",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_webhook_action,
            json_body=UnsubscribeWebhookRequest(url=url).to_payload(),
            idempotency_key=idempotency_key,
        )

    def update_v3(
        self,
        *,
        url: str,
        secret: str | None = None,
        idempotency_key: str | None = None,
    ) -> WebhookActionResult:
        """Включает уведомления webhook v3."""

        return self.transport.request_public_model(
            "POST",
            "/messenger/v3/webhook",
            context=RequestContext(
                "messenger.webhook.update_v3",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_webhook_action,
            json_body=UpdateWebhookRequest(url=url, secret=secret).to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class MediaClient:
    """Выполняет HTTP-операции media uploads и voice files."""

    transport: Transport

    def get_voice_files(
        self,
        *,
        user_id: int,
        voice_ids: Sequence[str] | None = None,
    ) -> VoiceFilesResult:
        """Получает голосовые сообщения."""

        resolved_voice_ids = list(voice_ids or ["voice-1"])
        return self.transport.request_public_model(
            "GET",
            f"/messenger/v1/accounts/{user_id}/getVoiceFiles",
            context=RequestContext("messenger.media.get_voice_files"),
            mapper=map_voice_files,
            params={"voice_ids": ",".join(resolved_voice_ids)},
        )

    def upload_images(
        self,
        *,
        user_id: int,
        files: list[UploadImageFile],
        idempotency_key: str | None = None,
    ) -> UploadImagesResult:
        """Загружает изображения для сообщений."""

        return self.transport.request_public_model(
            "POST",
            f"/messenger/v1/accounts/{user_id}/uploadImages",
            context=RequestContext(
                "messenger.media.upload_images",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_upload_images,
            files=UploadImagesRequest(files=files).to_files(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class SpecialOffersClient:
    """Выполняет HTTP-операции рассылок скидок и спецпредложений."""

    transport: Transport

    def get_available(self, *, item_ids: list[int]) -> SpecialOfferAvailableResult:
        """Получает доступные объявления для рассылки."""

        return self.transport.request_public_model(
            "POST",
            "/special-offers/v1/available",
            context=RequestContext("messenger.special_offers.get_available", allow_retry=True),
            mapper=map_available_special_offers,
            json_body=SpecialOfferAvailableRequest(item_ids=item_ids).to_payload(),
        )

    def create_multi(
        self,
        *,
        item_ids: list[int],
        message: str,
        discount_percent: int | None = None,
        idempotency_key: str | None = None,
    ) -> MultiCreateSpecialOfferResult:
        """Создает рассылку спецпредложений."""

        return self.transport.request_public_model(
            "POST",
            "/special-offers/v1/multiCreate",
            context=RequestContext(
                "messenger.special_offers.create_multi",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_multi_create_result,
            json_body=MultiCreateSpecialOfferRequest(
                item_ids=item_ids,
                message=message,
                discount_percent=discount_percent,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def confirm_multi(
        self, *, campaign_id: str, idempotency_key: str | None = None
    ) -> WebhookActionResult:
        """Подтверждает и оплачивает рассылку."""

        return self.transport.request_public_model(
            "POST",
            "/special-offers/v1/multiConfirm",
            context=RequestContext(
                "messenger.special_offers.confirm_multi",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_webhook_action,
            json_body=MultiConfirmSpecialOfferRequest(campaign_id=campaign_id).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_stats(self, *, campaign_id: str) -> SpecialOfferStatsResult:
        """Получает статистику рассылки."""

        return self.transport.request_public_model(
            "POST",
            "/special-offers/v1/stats",
            context=RequestContext("messenger.special_offers.get_stats", allow_retry=True),
            mapper=map_special_offer_stats,
            json_body=SpecialOfferStatsRequest(campaign_id=campaign_id).to_payload(),
        )

    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе спецпредложений."""

        return self.transport.request_public_model(
            "POST",
            "/special-offers/v1/tariffInfo",
            context=RequestContext("messenger.special_offers.get_tariff_info", allow_retry=True),
            mapper=map_tariff_info,
        )


__all__ = ("MediaClient", "MessengerClient", "SpecialOffersClient", "WebhookClient")
