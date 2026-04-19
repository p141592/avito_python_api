"""Доменные объекты пакета ratings."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import Transport, ValidationError
from avito.ratings.client import RatingsClient
from avito.ratings.models import (
    CreateReviewAnswerRequest,
    RatingProfileInfo,
    ReviewAnswerInfo,
    ReviewsQuery,
    ReviewsResult,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела ratings."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class Review(DomainObject):
    """Доменный объект отзывов."""

    user_id: int | str | None = None

    def list(self, *, query: ReviewsQuery | None = None) -> ReviewsResult:
        return RatingsClient(self.transport).list_reviews(query=query)


@dataclass(slots=True, frozen=True)
class ReviewAnswer(DomainObject):
    """Доменный объект ответов на отзывы."""

    answer_id: int | str | None = None
    user_id: int | str | None = None

    def create(self, *, review_id: int, text: str) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).create_review_answer(
            CreateReviewAnswerRequest(review_id=review_id, text=text)
        )

    def delete(self, *, answer_id: int | str | None = None) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).delete_review_answer(
            answer_id=answer_id or self._require_answer_id()
        )

    def _require_answer_id(self) -> str:
        if self.answer_id is None:
            raise ValidationError("Для операции требуется `answer_id`.")
        return str(self.answer_id)


@dataclass(slots=True, frozen=True)
class RatingProfile(DomainObject):
    """Доменный объект рейтингового профиля."""

    user_id: int | str | None = None

    def get(self) -> RatingProfileInfo:
        return RatingsClient(self.transport).get_ratings_info()


__all__ = ("DomainObject", "RatingProfile", "Review", "ReviewAnswer")
