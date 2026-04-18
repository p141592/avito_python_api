"""Типизированные модели раздела ratings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class ReviewsQuery:
    """Query-параметры списка отзывов."""

    page: int | None = None

    def to_params(self) -> dict[str, int]:
        """Сериализует query-параметры списка отзывов."""

        params: dict[str, int] = {}
        if self.page is not None:
            params["page"] = self.page
        return params


@dataclass(slots=True, frozen=True)
class CreateReviewAnswerRequest:
    """Запрос создания ответа на отзыв."""

    review_id: int
    text: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос создания ответа."""

        return {"reviewId": self.review_id, "text": self.text}


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
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ReviewsResult:
    """Список отзывов пользователя."""

    items: list[ReviewInfo]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ReviewAnswerInfo:
    """Информация об ответе на отзыв."""

    answer_id: str | None = None
    created_at: int | None = None
    success: bool | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RatingProfileInfo:
    """Информация о рейтинговом профиле."""

    is_enabled: bool
    score: float | None = None
    reviews_count: int | None = None
    reviews_with_score_count: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


enable_module_serialization(globals())
