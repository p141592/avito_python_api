"""Enum-значения раздела messenger."""

from __future__ import annotations

from enum import Enum


class MessageDirection(str, Enum):
    """Направление сообщения."""

    UNKNOWN = "__unknown__"
    IN = "in"
    OUT = "out"


class MessageType(str, Enum):
    """Тип сообщения."""

    UNKNOWN = "__unknown__"
    TEXT = "text"
    IMAGE = "image"


class MessageActionStatus(str, Enum):
    """Статус операции с сообщением или чатом."""

    UNKNOWN = "__unknown__"
    SENT = "sent"
    CONFIRMED = "confirmed"


class SubscriptionStatus(str, Enum):
    """Статус webhook-подписки."""

    UNKNOWN = "__unknown__"
    ACTIVE = "active"


class WebhookStatus(str, Enum):
    """Статус действия с webhook."""

    UNKNOWN = "__unknown__"
    SUBSCRIBED = "subscribed"
    CONFIRMED = "confirmed"


class SpecialOfferCampaignStatus(str, Enum):
    """Статус кампании спецпредложений."""

    UNKNOWN = "__unknown__"
    DRAFT = "draft"
    CONFIRMED = "confirmed"


__all__ = (
    "MessageActionStatus",
    "MessageDirection",
    "MessageType",
    "SpecialOfferCampaignStatus",
    "SubscriptionStatus",
    "WebhookStatus",
)
