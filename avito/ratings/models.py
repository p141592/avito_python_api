"""Типизированные модели раздела ratings."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import SerializableModel
from avito.ratings.enums import ReviewStage


@dataclass(slots=True, frozen=True)
class ReviewsQuery:
    """Query-параметры списка отзывов."""

    page: int | None = None
    limit: int | None = None

    def to_params(self) -> dict[str, int]:
        """Сериализует query-параметры списка отзывов."""

        params: dict[str, int] = {}
        if self.page is not None:
            params["page"] = self.page
        if self.limit is not None:
            params["limit"] = self.limit
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
class ReviewInfo(SerializableModel):
    """Информация об отзыве пользователя."""

    review_id: str | None
    score: int | None
    stage: ReviewStage | None
    text: str | None
    created_at: int | None
    can_answer: bool | None
    used_in_score: bool | None


@dataclass(slots=True, frozen=True)
class ReviewsResult(SerializableModel):
    """Список отзывов пользователя."""

    items: list[ReviewInfo]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class ReviewAnswerInfo(SerializableModel):
    """Информация об ответе на отзыв."""

    answer_id: str | None = None
    created_at: int | None = None
    success: bool | None = None


@dataclass(slots=True, frozen=True)
class RatingProfileInfo(SerializableModel):
    """Информация о рейтинговом профиле."""

    is_enabled: bool
    score: float | None = None
    reviews_count: int | None = None
    reviews_with_score_count: int | None = None
