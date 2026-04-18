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

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list_reviews_v1(self, *, query: ReviewsQuery | None = None) -> ReviewsResult:
        return RatingsClient(self.transport).list_reviews_v1(query=query)


@dataclass(slots=True, frozen=True)
class ReviewAnswer(DomainObject):
    """Доменный объект ответов на отзывы."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_review_answer_v1(self, *, review_id: int, text: str) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).create_review_answer_v1(
            CreateReviewAnswerRequest(review_id=review_id, text=text)
        )

    def delete_review_answer_v1(self, *, answer_id: int | str | None = None) -> ReviewAnswerInfo:
        return RatingsClient(self.transport).delete_review_answer_v1(
            answer_id=answer_id or self._require_answer_id()
        )

    def _require_answer_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `answer_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class RatingProfile(DomainObject):
    """Доменный объект рейтингового профиля."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_ratings_info_v1(self) -> RatingProfileInfo:
        return RatingsClient(self.transport).get_ratings_info_v1()


__all__ = ("DomainObject", "RatingProfile", "Review", "ReviewAnswer")
