"""Мапперы JSON -> dataclass для пакета messenger."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.messenger.models import (
    ChatInfo,
    ChatsResult,
    MessageActionResult,
    MessageInfo,
    MessagesResult,
    MultiCreateSpecialOfferResult,
    SpecialOfferAvailableItem,
    SpecialOfferAvailableResult,
    SpecialOfferStatsResult,
    SubscriptionInfo,
    SubscriptionsResult,
    TariffInfo,
    UploadImageResult,
    UploadImagesResult,
    VoiceFile,
    VoiceFilesResult,
    WebhookActionResult,
)

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_chat(payload: object) -> ChatInfo:
    """Преобразует объект чата в dataclass."""

    data = _expect_mapping(payload)
    last_message = data.get("last_message")
    last_message_data = cast(Payload, last_message) if isinstance(last_message, Mapping) else {}
    return ChatInfo(
        id=_str(data, "id", "chat_id", "chatId"),
        user_id=_int(data, "user_id", "userId"),
        title=_str(data, "title", "name"),
        unread_count=_int(data, "unread_count", "unreadCount"),
        last_message_text=_str(last_message_data, "text", "message"),
        raw_payload=data,
    )


def map_chats(payload: object) -> ChatsResult:
    """Преобразует список чатов в dataclass."""

    data = _expect_mapping(payload)
    return ChatsResult(
        items=[map_chat(item) for item in _list(data, "chats", "items", "result")],
        total=_int(data, "total", "count"),
        raw_payload=data,
    )


def map_message(payload: object) -> MessageInfo:
    """Преобразует сообщение в dataclass."""

    data = _expect_mapping(payload)
    return MessageInfo(
        id=_str(data, "id", "message_id", "messageId"),
        chat_id=_str(data, "chat_id", "chatId"),
        author_id=_int(data, "author_id", "authorId", "user_id", "userId"),
        text=_str(data, "text", "message"),
        created_at=_str(data, "created_at", "createdAt"),
        direction=_str(data, "direction"),
        type=_str(data, "type"),
        raw_payload=data,
    )


def map_messages(payload: object) -> MessagesResult:
    """Преобразует список сообщений в dataclass."""

    data = _expect_mapping(payload)
    return MessagesResult(
        items=[map_message(item) for item in _list(data, "messages", "items", "result")],
        total=_int(data, "total", "count"),
        raw_payload=data,
    )


def map_message_action(payload: object) -> MessageActionResult:
    """Преобразует результат операции с сообщением."""

    data = _expect_mapping(payload)
    return MessageActionResult(
        success=bool(data.get("success", True)),
        message_id=_str(data, "message_id", "messageId", "id"),
        status=_str(data, "status", "message"),
        raw_payload=data,
    )


def map_voice_files(payload: object) -> VoiceFilesResult:
    """Преобразует список голосовых сообщений."""

    data = _expect_mapping(payload)
    return VoiceFilesResult(
        items=[
            VoiceFile(
                id=_str(item, "id", "voice_id", "voiceId"),
                url=_str(item, "url"),
                duration=_int(item, "duration"),
                transcript=_str(item, "transcript", "text"),
                raw_payload=item,
            )
            for item in _list(data, "voice_files", "items", "result")
        ],
        raw_payload=data,
    )


def map_upload_images(payload: object) -> UploadImagesResult:
    """Преобразует результат загрузки изображений."""

    data = _expect_mapping(payload)
    return UploadImagesResult(
        items=[
            UploadImageResult(
                image_id=_str(item, "image_id", "imageId", "id"),
                url=_str(item, "url"),
                raw_payload=item,
            )
            for item in _list(data, "images", "items", "result")
        ],
        raw_payload=data,
    )


def map_subscriptions(payload: object) -> SubscriptionsResult:
    """Преобразует список подписок webhook."""

    data = _expect_mapping(payload)
    return SubscriptionsResult(
        items=[
            SubscriptionInfo(
                url=_str(item, "url"),
                version=_str(item, "version"),
                status=_str(item, "status"),
                raw_payload=item,
            )
            for item in _list(data, "subscriptions", "items", "result")
        ],
        raw_payload=data,
    )


def map_webhook_action(payload: object) -> WebhookActionResult:
    """Преобразует результат операции с webhook."""

    data = _expect_mapping(payload)
    return WebhookActionResult(
        success=bool(data.get("success", True)),
        status=_str(data, "status", "message"),
        raw_payload=data,
    )


def map_available_special_offers(payload: object) -> SpecialOfferAvailableResult:
    """Преобразует доступные объявления спецпредложений."""

    data = _expect_mapping(payload)
    return SpecialOfferAvailableResult(
        items=[
            SpecialOfferAvailableItem(
                item_id=_int(item, "item_id", "itemId", "id"),
                title=_str(item, "title"),
                is_available=_bool(item, "is_available", "isAvailable", "available"),
                raw_payload=item,
            )
            for item in _list(data, "items", "result")
        ],
        raw_payload=data,
    )


def map_multi_create_result(payload: object) -> MultiCreateSpecialOfferResult:
    """Преобразует результат создания рассылки."""

    data = _expect_mapping(payload)
    return MultiCreateSpecialOfferResult(
        campaign_id=_str(data, "campaign_id", "campaignId", "id"),
        status=_str(data, "status"),
        raw_payload=data,
    )


def map_special_offer_stats(payload: object) -> SpecialOfferStatsResult:
    """Преобразует статистику рассылки."""

    data = _expect_mapping(payload)
    return SpecialOfferStatsResult(
        campaign_id=_str(data, "campaign_id", "campaignId", "id"),
        sent_count=_int(data, "sent_count", "sentCount"),
        delivered_count=_int(data, "delivered_count", "deliveredCount"),
        read_count=_int(data, "read_count", "readCount"),
        raw_payload=data,
    )


def map_tariff_info(payload: object) -> TariffInfo:
    """Преобразует информацию о тарифе."""

    data = _expect_mapping(payload)
    return TariffInfo(
        price=_float(data, "price", "amount"),
        currency=_str(data, "currency"),
        daily_limit=_int(data, "daily_limit", "dailyLimit", "limit"),
        raw_payload=data,
    )


__all__ = (
    "map_available_special_offers",
    "map_chat",
    "map_chats",
    "map_message",
    "map_message_action",
    "map_messages",
    "map_multi_create_result",
    "map_special_offer_stats",
    "map_subscriptions",
    "map_tariff_info",
    "map_upload_images",
    "map_voice_files",
    "map_webhook_action",
)
