"""Типизированные модели раздела messenger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class ChatInfo:
    """Информация о чате."""

    id: str | None
    user_id: int | None
    title: str | None
    unread_count: int | None
    last_message_text: str | None


@dataclass(slots=True, frozen=True)
class ChatsResult:
    """Список чатов."""

    items: list[ChatInfo]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class SendMessageRequest:
    """Запрос отправки текстового сообщения."""

    message: str
    type: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует сообщение для API."""

        return {
            key: value
            for key, value in {"message": self.message, "type": self.type}.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class SendImageMessageRequest:
    """Запрос отправки сообщения с изображением."""

    image_id: str
    caption: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует сообщение с изображением."""

        return {
            key: value
            for key, value in {"imageId": self.image_id, "caption": self.caption}.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class MessageInfo:
    """Информация о сообщении чата."""

    id: str | None
    chat_id: str | None
    author_id: int | None
    text: str | None
    created_at: str | None
    direction: str | None
    type: str | None


@dataclass(slots=True, frozen=True)
class MessagesResult:
    """Список сообщений чата."""

    items: list[MessageInfo]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class MessageActionResult:
    """Результат операции с сообщением или чатом."""

    success: bool
    message_id: str | None = None
    status: str | None = None


@dataclass(slots=True, frozen=True)
class VoiceFile:
    """Голосовое сообщение."""

    id: str | None
    url: str | None
    duration: int | None
    transcript: str | None


@dataclass(slots=True, frozen=True)
class VoiceFilesResult:
    """Список голосовых сообщений."""

    items: list[VoiceFile]


@dataclass(slots=True, frozen=True)
class UploadImageResult:
    """Результат загрузки изображения."""

    image_id: str | None
    url: str | None


@dataclass(slots=True, frozen=True)
class UploadImagesResult:
    """Список загруженных изображений."""

    items: list[UploadImageResult]


@dataclass(slots=True, frozen=True)
class UploadImageFile:
    """Файл изображения для загрузки в мессенджер."""

    field_name: str
    filename: str
    content: bytes | BinaryIO
    content_type: str


@dataclass(slots=True, frozen=True)
class UploadImagesRequest:
    """Запрос загрузки изображений для сообщений."""

    files: list[UploadImageFile]

    def to_files(self) -> dict[str, object]:
        """Сериализует multipart-структуру для transport."""

        return {
            file.field_name: (file.filename, file.content, file.content_type) for file in self.files
        }


@dataclass(slots=True, frozen=True)
class SubscriptionInfo:
    """Подписка webhook мессенджера."""

    url: str | None
    version: str | None
    status: str | None


@dataclass(slots=True, frozen=True)
class SubscriptionsResult:
    """Список webhook-подписок."""

    items: list[SubscriptionInfo]


@dataclass(slots=True, frozen=True)
class UnsubscribeWebhookRequest:
    """Запрос отключения webhook."""

    url: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос отключения webhook."""

        return {"url": self.url}


@dataclass(slots=True, frozen=True)
class UpdateWebhookRequest:
    """Запрос включения webhook v3."""

    url: str
    secret: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос включения webhook."""

        return {
            key: value
            for key, value in {"url": self.url, "secret": self.secret}.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class WebhookActionResult:
    """Результат операции с webhook."""

    success: bool
    status: str | None = None


@dataclass(slots=True, frozen=True)
class BlacklistRequest:
    """Запрос добавления пользователя в blacklist."""

    blacklisted_user_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос blacklist."""

        return {"blacklistedUserId": self.blacklisted_user_id}


@dataclass(slots=True, frozen=True)
class SpecialOfferAvailableRequest:
    """Запрос доступных объявлений для спецпредложений."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос доступных объявлений."""

        return {"itemIds": self.item_ids}


@dataclass(slots=True, frozen=True)
class SpecialOfferAvailableItem:
    """Доступное объявление для рассылки спецпредложений."""

    item_id: int | None
    title: str | None
    is_available: bool | None


@dataclass(slots=True, frozen=True)
class SpecialOfferAvailableResult:
    """Результат получения доступных объявлений."""

    items: list[SpecialOfferAvailableItem]


@dataclass(slots=True, frozen=True)
class MultiCreateSpecialOfferRequest:
    """Запрос создания рассылки."""

    item_ids: list[int]
    message: str
    discount_percent: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос создания рассылки."""

        return {
            key: value
            for key, value in {
                "itemIds": self.item_ids,
                "message": self.message,
                "discountPercent": self.discount_percent,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class MultiCreateSpecialOfferResult:
    """Результат создания рассылки."""

    campaign_id: str | None
    status: str | None


@dataclass(slots=True, frozen=True)
class MultiConfirmSpecialOfferRequest:
    """Запрос подтверждения и оплаты рассылки."""

    campaign_id: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос подтверждения рассылки."""

        return {"campaignId": self.campaign_id}


@dataclass(slots=True, frozen=True)
class SpecialOfferStatsRequest:
    """Запрос статистики рассылки."""

    campaign_id: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статистики рассылки."""

        return {"campaignId": self.campaign_id}


@dataclass(slots=True, frozen=True)
class SpecialOfferStatsResult:
    """Статистика рассылки."""

    campaign_id: str | None
    sent_count: int | None
    delivered_count: int | None
    read_count: int | None


@dataclass(slots=True, frozen=True)
class TariffInfo:
    """Информация о тарифе рассылок."""

    price: float | None
    currency: str | None
    daily_limit: int | None


__all__ = (
    "BlacklistRequest",
    "ChatInfo",
    "ChatsResult",
    "MessageActionResult",
    "MessageInfo",
    "MessagesResult",
    "MultiConfirmSpecialOfferRequest",
    "MultiCreateSpecialOfferRequest",
    "MultiCreateSpecialOfferResult",
    "SendImageMessageRequest",
    "SendMessageRequest",
    "SpecialOfferAvailableItem",
    "SpecialOfferAvailableRequest",
    "SpecialOfferAvailableResult",
    "SpecialOfferStatsRequest",
    "SpecialOfferStatsResult",
    "SubscriptionInfo",
    "SubscriptionsResult",
    "TariffInfo",
    "UnsubscribeWebhookRequest",
    "UpdateWebhookRequest",
    "UploadImageFile",
    "UploadImagesRequest",
    "UploadImageResult",
    "UploadImagesResult",
    "VoiceFile",
    "VoiceFilesResult",
    "WebhookActionResult",
)

enable_module_serialization(globals())
