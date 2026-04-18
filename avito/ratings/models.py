"""Типизированные модели раздела ratings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class JsonRequest:
    """Типизированная обертка над JSON payload запроса."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class ReviewInfo:
    """Информация об отзыве пользователя."""

    review_id: str | None
    score: int | None
    stage: str | None
    text: str | None
    created_at: int | None
    can_answer: bool | None
    used_in_score: bool | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ReviewsResult:
    """Список отзывов пользователя."""

    items: list[ReviewInfo]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ReviewAnswerInfo:
    """Информация об ответе на отзыв."""

    answer_id: str | None = None
    created_at: int | None = None
    success: bool | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RatingProfileInfo:
    """Информация о рейтинговом профиле."""

    is_enabled: bool
    score: float | None = None
    reviews_count: int | None = None
    reviews_with_score_count: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)
