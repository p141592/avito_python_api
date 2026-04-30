"""Внутренние section clients для пакета ratings."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.ratings.mappers import map_rating_profile, map_review_answer, map_reviews
from avito.ratings.models import (
    CreateReviewAnswerRequest,
    RatingProfileInfo,
    ReviewAnswerInfo,
    ReviewsQuery,
    ReviewsResult,
)


@dataclass(slots=True, frozen=True)
class RatingsClient:
    """Выполняет HTTP-операции рейтингов и отзывов."""

    transport: Transport

    def create_review_answer(
        self,
        *,
        review_id: int,
        text: str,
        idempotency_key: str | None = None,
    ) -> ReviewAnswerInfo:
        return self.transport.request_public_model(
            "POST",
            "/ratings/v1/answers",
            context=RequestContext("ratings.answers.create", allow_retry=idempotency_key is not None),
            mapper=map_review_answer,
            json_body=CreateReviewAnswerRequest(review_id=review_id, text=text).to_payload(),
            idempotency_key=idempotency_key,
        )

    def delete_review_answer(
        self,
        *,
        answer_id: int | str,
        idempotency_key: str | None = None,
    ) -> ReviewAnswerInfo:
        return self.transport.request_public_model(
            "DELETE",
            f"/ratings/v1/answers/{answer_id}",
            context=RequestContext("ratings.answers.delete", allow_retry=idempotency_key is not None),
            mapper=map_review_answer,
            idempotency_key=idempotency_key,
        )

    def get_ratings_info(self) -> RatingProfileInfo:
        return self.transport.request_public_model(
            "GET",
            "/ratings/v1/info",
            context=RequestContext("ratings.info.get"),
            mapper=map_rating_profile,
        )

    def list_reviews(self, *, query: ReviewsQuery | None = None) -> ReviewsResult:
        resolved_query = ReviewsQuery(
            offset=query.offset if query is not None and query.offset is not None else 0,
            page=query.page if query is not None and query.page is not None else 1,
            limit=query.limit if query is not None and query.limit is not None else 50,
        )
        return self.transport.request_public_model(
            "GET",
            "/ratings/v1/reviews",
            context=RequestContext("ratings.reviews.list"),
            mapper=map_reviews,
            params=resolved_query.to_params(),
        )
