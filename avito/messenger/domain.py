"""Доменные объекты пакета messenger."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.messenger.client import MediaClient, MessengerClient, SpecialOffersClient, WebhookClient
from avito.messenger.models import (
    ChatInfo,
    ChatsResult,
    MessageActionResult,
    MessagesResult,
    MultiCreateSpecialOfferResult,
    SpecialOfferAvailableResult,
    SpecialOfferStatsResult,
    SubscriptionsResult,
    TariffInfo,
    UploadImageFile,
    UploadImagesResult,
    VoiceFilesResult,
    WebhookActionResult,
)


@dataclass(slots=True, frozen=True)
class Chat(DomainObject):
    """Доменный объект чата."""

    chat_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> ChatInfo:
        """Получает чат по `chat_id`."""

        return MessengerClient(self.transport).get_chat(
            user_id=self._require_user_id(),
            chat_id=self._require_chat_id(),
        )

    def list(self) -> ChatsResult:
        """Получает список чатов пользователя."""

        return MessengerClient(self.transport).list_chats(user_id=self._require_user_id())

    def mark_read(self, *, idempotency_key: str | None = None) -> MessageActionResult:
        """Помечает чат как прочитанный."""

        return MessengerClient(self.transport).read_chat(
            user_id=self._require_user_id(),
            chat_id=self._require_chat_id(),
            idempotency_key=idempotency_key,
        )

    def blacklist(
        self,
        *,
        blacklisted_user_id: int,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Добавляет пользователя в blacklist."""

        return MessengerClient(self.transport).add_to_blacklist(
            user_id=self._require_user_id(),
            blacklisted_user_id=blacklisted_user_id,
            idempotency_key=idempotency_key,
        )

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)

    def _require_chat_id(self) -> str:
        if self.chat_id is None:
            raise ValidationError("Для операции требуется `chat_id`.")
        return str(self.chat_id)


@dataclass(slots=True, frozen=True)
class ChatMessage(DomainObject):
    """Доменный объект сообщения чата."""

    chat_id: int | str | None = None
    message_id: int | str | None = None
    user_id: int | str | None = None

    def list(self, *, chat_id: str | None = None) -> MessagesResult:
        """Получает список сообщений V3."""

        return MessengerClient(self.transport).list_messages(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
        )

    def send_message(
        self,
        *,
        chat_id: str | None = None,
        message: str,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Отправляет текстовое сообщение."""

        return MessengerClient(self.transport).send_message(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
            message=message,
            idempotency_key=idempotency_key,
        )

    def send_image(
        self,
        *,
        chat_id: str | None = None,
        image_id: str,
        caption: str | None = None,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Отправляет сообщение с изображением."""

        return MessengerClient(self.transport).send_image_message(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
            image_id=image_id,
            caption=caption,
            idempotency_key=idempotency_key,
        )

    def delete(
        self,
        *,
        chat_id: str | None = None,
        message_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Удаляет сообщение."""

        resolved_message_id = message_id or self._require_message_id()
        return MessengerClient(self.transport).delete_message(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
            message_id=resolved_message_id,
            idempotency_key=idempotency_key,
        )

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)

    def _require_chat_id(self) -> str:
        if self.chat_id is None:
            raise ValidationError("Для операции требуется `chat_id`.")
        return str(self.chat_id)

    def _require_message_id(self) -> str:
        if self.message_id is None:
            raise ValidationError("Для операции требуется `message_id`.")
        return str(self.message_id)


@dataclass(slots=True, frozen=True)
class ChatWebhook(DomainObject):
    """Доменный объект webhook мессенджера."""

    user_id: int | str | None = None

    def list(self) -> SubscriptionsResult:
        """Получает список webhook-подписок."""

        return WebhookClient(self.transport).get_subscriptions()

    def unsubscribe(self, *, url: str, idempotency_key: str | None = None) -> WebhookActionResult:
        """Отключает webhook."""

        return WebhookClient(self.transport).unsubscribe(url=url, idempotency_key=idempotency_key)

    def subscribe(
        self,
        *,
        url: str,
        secret: str | None = None,
        idempotency_key: str | None = None,
    ) -> WebhookActionResult:
        """Включает webhook v3."""

        return WebhookClient(self.transport).update_v3(
            url=url,
            secret=secret,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class ChatMedia(DomainObject):
    """Доменный объект media-функций мессенджера."""

    user_id: int | str | None = None

    def get_voice_files(self) -> VoiceFilesResult:
        """Получает голосовые сообщения."""

        return MediaClient(self.transport).get_voice_files(user_id=self._require_user_id())

    def upload_images(
        self,
        *,
        files: list[UploadImageFile],
        idempotency_key: str | None = None,
    ) -> UploadImagesResult:
        """Загружает изображения для сообщений."""

        return MediaClient(self.transport).upload_images(
            user_id=self._require_user_id(),
            files=files,
            idempotency_key=idempotency_key,
        )

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)


@dataclass(slots=True, frozen=True)
class SpecialOfferCampaign(DomainObject):
    """Доменный объект рассылки скидок и спецпредложений."""

    campaign_id: int | str | None = None
    user_id: int | str | None = None

    def get_available(self, *, item_ids: list[int]) -> SpecialOfferAvailableResult:
        """Получает объявления, доступные для рассылки."""

        return SpecialOffersClient(self.transport).get_available(item_ids=item_ids)

    def create_multi(
        self,
        *,
        item_ids: list[int],
        message: str,
        discount_percent: int | None = None,
        idempotency_key: str | None = None,
    ) -> MultiCreateSpecialOfferResult:
        """Создает рассылку спецпредложений."""

        return SpecialOffersClient(self.transport).create_multi(
            item_ids=item_ids,
            message=message,
            discount_percent=discount_percent,
            idempotency_key=idempotency_key,
        )

    def confirm_multi(
        self,
        *,
        campaign_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WebhookActionResult:
        """Подтверждает и оплачивает рассылку."""

        return SpecialOffersClient(self.transport).confirm_multi(
            campaign_id=campaign_id or self._require_campaign_id(),
            idempotency_key=idempotency_key,
        )

    def get_stats(self, *, campaign_id: str | None = None) -> SpecialOfferStatsResult:
        """Получает статистику рассылки."""

        return SpecialOffersClient(self.transport).get_stats(
            campaign_id=campaign_id or self._require_campaign_id()
        )

    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе спецпредложений."""

        return SpecialOffersClient(self.transport).get_tariff_info()

    def _require_campaign_id(self) -> str:
        if self.campaign_id is None:
            raise ValidationError("Для операции требуется `campaign_id`.")
        return str(self.campaign_id)


__all__ = (
    "Chat",
    "ChatMedia",
    "ChatMessage",
    "ChatWebhook",
    "SpecialOfferCampaign",
)
