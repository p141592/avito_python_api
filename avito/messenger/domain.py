"""Доменные объекты пакета messenger."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
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

    __swagger_domain__ = "messenger"
    __sdk_factory__ = "chat"
    __sdk_factory_args__ = {"chat_id": "path.chat_id", "user_id": "path.user_id"}

    chat_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/messenger/v2/accounts/{user_id}/chats/{chat_id}",
        spec="Мессенджер.json",
        operation_id="getChatByIdV2",
    )
    def get(self) -> ChatInfo:
        """Получает чат по `chat_id`.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).get_chat(
            user_id=self._require_user_id(),
            chat_id=self._require_chat_id(),
        )

    @swagger_operation(
        "GET",
        "/messenger/v2/accounts/{user_id}/chats",
        spec="Мессенджер.json",
        operation_id="getChatsV2",
    )
    def list(self) -> ChatsResult:
        """Получает список чатов пользователя.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).list_chats(user_id=self._require_user_id())

    @swagger_operation(
        "POST",
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/read",
        spec="Мессенджер.json",
        operation_id="chatRead",
    )
    def mark_read(self, *, idempotency_key: str | None = None) -> MessageActionResult:
        """Помечает чат как прочитанный.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).read_chat(
            user_id=self._require_user_id(),
            chat_id=self._require_chat_id(),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/messenger/v2/accounts/{user_id}/blacklist",
        spec="Мессенджер.json",
        operation_id="postBlacklistV2",
        method_args={"blacklisted_user_id": "body.blacklisted_user_id"},
    )
    def blacklist(
        self,
        *,
        blacklisted_user_id: int,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Добавляет пользователя в blacklist.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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

    __swagger_domain__ = "messenger"
    __sdk_factory__ = "chat_message"
    __sdk_factory_args__ = {
        "message_id": "path.message_id",
        "chat_id": "path.chat_id",
        "user_id": "path.user_id",
    }

    chat_id: int | str | None = None
    message_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages",
        spec="Мессенджер.json",
        operation_id="getMessagesV3",
    )
    def list(self, *, chat_id: str | None = None) -> MessagesResult:
        """Получает список сообщений V3.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).list_messages(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
        )

    @swagger_operation(
        "POST",
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages",
        spec="Мессенджер.json",
        operation_id="postSendMessage",
        method_args={"message": "body.message"},
    )
    def send_message(
        self,
        *,
        chat_id: str | None = None,
        message: str,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Отправляет текстовое сообщение.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).send_message(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
            message=message,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image",
        spec="Мессенджер.json",
        operation_id="postSendImageMessage",
        method_args={"image_id": "body.image_id"},
    )
    def send_image(
        self,
        *,
        chat_id: str | None = None,
        image_id: str,
        caption: str | None = None,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Отправляет сообщение с изображением.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MessengerClient(self.transport).send_image_message(
            user_id=self._require_user_id(),
            chat_id=chat_id or self._require_chat_id(),
            image_id=image_id,
            caption=caption,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}",
        spec="Мессенджер.json",
        operation_id="deleteMessage",
    )
    def delete(
        self,
        *,
        chat_id: str | None = None,
        message_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> MessageActionResult:
        """Удаляет сообщение.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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

    __swagger_domain__ = "messenger"
    __sdk_factory__ = "chat_webhook"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/messenger/v1/subscriptions",
        spec="Мессенджер.json",
        operation_id="getSubscriptions",
    )
    def list(self) -> SubscriptionsResult:
        """Получает список webhook-подписок.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).get_subscriptions()

    @swagger_operation(
        "POST",
        "/messenger/v1/webhook/unsubscribe",
        spec="Мессенджер.json",
        operation_id="postWebhookUnsubscribe",
        method_args={"url": "body.url"},
    )
    def unsubscribe(self, *, url: str, idempotency_key: str | None = None) -> WebhookActionResult:
        """Отключает webhook.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).unsubscribe(url=url, idempotency_key=idempotency_key)

    @swagger_operation(
        "POST",
        "/messenger/v3/webhook",
        spec="Мессенджер.json",
        operation_id="postWebhookV3",
        method_args={"url": "body.url"},
    )
    def subscribe(
        self,
        *,
        url: str,
        secret: str | None = None,
        idempotency_key: str | None = None,
    ) -> WebhookActionResult:
        """Включает webhook v3.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).update_v3(
            url=url,
            secret=secret,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class ChatMedia(DomainObject):
    """Доменный объект media-функций мессенджера."""

    __swagger_domain__ = "messenger"
    __sdk_factory__ = "chat_media"
    __sdk_factory_args__ = {"user_id": "path.user_id"}

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/messenger/v1/accounts/{user_id}/getVoiceFiles",
        spec="Мессенджер.json",
        operation_id="getVoiceFiles",
    )
    def get_voice_files(self) -> VoiceFilesResult:
        """Получает голосовые сообщения.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MediaClient(self.transport).get_voice_files(user_id=self._require_user_id())

    @swagger_operation(
        "POST",
        "/messenger/v1/accounts/{user_id}/uploadImages",
        spec="Мессенджер.json",
        operation_id="uploadImages",
        method_args={"files": "body.files"},
    )
    def upload_images(
        self,
        *,
        files: list[UploadImageFile],
        idempotency_key: str | None = None,
    ) -> UploadImagesResult:
        """Загружает изображения для сообщений.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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

    __swagger_domain__ = "messenger"
    __sdk_factory__ = "special_offer_campaign"
    __sdk_factory_args__ = {"campaign_id": "path.campaign_id"}

    campaign_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/special-offers/v1/available",
        spec="Рассылкаскидокиспецпредложенийвмессенджере.json",
        operation_id="openApiAvailable",
        method_args={"item_ids": "body.item_ids"},
    )
    def get_available(self, *, item_ids: list[int]) -> SpecialOfferAvailableResult:
        """Получает объявления, доступные для рассылки.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecialOffersClient(self.transport).get_available(item_ids=item_ids)

    @swagger_operation(
        "POST",
        "/special-offers/v1/multiCreate",
        spec="Рассылкаскидокиспецпредложенийвмессенджере.json",
        operation_id="openApiMultiCreate",
        method_args={"item_ids": "body.item_ids", "message": "body.message"},
    )
    def create_multi(
        self,
        *,
        item_ids: list[int],
        message: str,
        discount_percent: int | None = None,
        idempotency_key: str | None = None,
    ) -> MultiCreateSpecialOfferResult:
        """Создает рассылку спецпредложений.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecialOffersClient(self.transport).create_multi(
            item_ids=item_ids,
            message=message,
            discount_percent=discount_percent,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/special-offers/v1/multiConfirm",
        spec="Рассылкаскидокиспецпредложенийвмессенджере.json",
        operation_id="openApiMultiConfirm",
    )
    def confirm_multi(
        self,
        *,
        campaign_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WebhookActionResult:
        """Подтверждает и оплачивает рассылку.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecialOffersClient(self.transport).confirm_multi(
            campaign_id=campaign_id or self._require_campaign_id(),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/special-offers/v1/stats",
        spec="Рассылкаскидокиспецпредложенийвмессенджере.json",
        operation_id="openApiStats",
    )
    def get_stats(self, *, campaign_id: str | None = None) -> SpecialOfferStatsResult:
        """Получает статистику рассылки.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecialOffersClient(self.transport).get_stats(
            campaign_id=campaign_id or self._require_campaign_id()
        )

    @swagger_operation(
        "POST",
        "/special-offers/v1/tariffInfo",
        spec="Рассылкаскидокиспецпредложенийвмессенджере.json",
        operation_id="openApiTariffInfo",
    )
    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе спецпредложений.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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
