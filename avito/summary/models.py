"""Типизированные модели итоговых read-only сводок."""

from __future__ import annotations

from dataclasses import dataclass

from avito.ads.enums import ListingStatus
from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class ListingHealthItem(SerializableModel):
    """Health-сводка по одному объявлению."""

    item_id: int | None
    title: str | None
    status: ListingStatus | None
    price: float | None
    url: str | None
    is_visible: bool | None
    views: int | None = None
    contacts: int | None = None
    favorites: int | None = None
    calls: int | None = None
    spendings: float | None = None


@dataclass(slots=True, frozen=True)
class ListingHealthSummary(SerializableModel):
    """Итоговая health-сводка по объявлениям."""

    user_id: int
    items: list[ListingHealthItem]
    total_listings: int
    visible_listings: int
    active_listings: int
    total_views: int | None
    total_contacts: int | None
    total_favorites: int | None
    total_calls: int | None
    total_spendings: float | None


@dataclass(slots=True, frozen=True)
class ChatSummary(SerializableModel):
    """Итоговая read-only сводка по чатам."""

    user_id: int
    total_chats: int
    unread_chats: int
    unread_messages: int


@dataclass(slots=True, frozen=True)
class OrderSummary(SerializableModel):
    """Итоговая read-only сводка по заказам."""

    total_orders: int
    active_orders: int


@dataclass(slots=True, frozen=True)
class ReviewSummary(SerializableModel):
    """Итоговая read-only сводка по отзывам."""

    total_reviews: int
    average_score: float | None
    unanswered_reviews: int
    rating_score: float | None


@dataclass(slots=True, frozen=True)
class PromotionSummary(SerializableModel):
    """Итоговая read-only сводка по продвижению."""

    total_orders: int
    active_orders: int
    total_services: int
    available_services: int


@dataclass(slots=True, frozen=True)
class AccountHealthSummary(SerializableModel):
    """Итоговая read-only сводка по бизнес-аккаунту."""

    user_id: int
    balance_total: float | None
    balance_real: float | None
    balance_bonus: float | None
    listings: ListingHealthSummary
    chats: ChatSummary | None = None
    orders: OrderSummary | None = None
    reviews: ReviewSummary | None = None
    promotion: PromotionSummary | None = None


@dataclass(slots=True, frozen=True)
class CapabilityInfo(SerializableModel):
    """Описание доступности публичной операции SDK."""

    operation: str
    factory_method: str
    is_available: bool
    reasons: list[str]
    possible_error_codes: list[int]


@dataclass(slots=True, frozen=True)
class CapabilityDiscoveryResult(SerializableModel):
    """Список возможностей SDK для текущей конфигурации клиента."""

    items: list[CapabilityInfo]


__all__ = (
    "AccountHealthSummary",
    "CapabilityDiscoveryResult",
    "CapabilityInfo",
    "ChatSummary",
    "ListingHealthItem",
    "ListingHealthSummary",
    "OrderSummary",
    "PromotionSummary",
    "ReviewSummary",
)
