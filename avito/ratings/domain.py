"""Доменные объекты пакета ratings."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.ratings.client import RatingsClient
from avito.ratings.models import (
    RatingProfileInfo,
    ReviewAnswerInfo,
    ReviewsQuery,
    ReviewsResult,
)


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

    def create(
        self,
        *,
        review_id: int,
        text: str,
        idempotency_key: str | None = None,
    ) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).create_review_answer(
            review_id=review_id,
            text=text,
            idempotency_key=idempotency_key,
        )

    def delete(
        self,
        *,
        answer_id: int | str | None = None,
        idempotency_key: str | None = None,
    ) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).delete_review_answer(
            answer_id=answer_id or self._require_answer_id(),
            idempotency_key=idempotency_key,
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


__all__ = ("RatingProfile", "Review", "ReviewAnswer")
