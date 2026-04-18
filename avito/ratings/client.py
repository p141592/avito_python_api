"""Внутренние section clients для пакета ratings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.ratings.mappers import map_rating_profile, map_review_answer, map_reviews
from avito.ratings.models import JsonRequest, RatingProfileInfo, ReviewAnswerInfo, ReviewsResult


@dataclass(slots=True)
class RatingsClient:
    """Выполняет HTTP-операции рейтингов и отзывов."""

    transport: Transport

    def create_review_answer_v1(self, request: JsonRequest) -> ReviewAnswerInfo:
        payload = self.transport.request_json(
            "POST",
            "/ratings/v1/answers",
            context=RequestContext("ratings.answers.create", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_review_answer(payload)

    def delete_review_answer_v1(self, *, answer_id: int | str) -> ReviewAnswerInfo:
        payload = self.transport.request_json(
            "DELETE",
            f"/ratings/v1/answers/{answer_id}",
            context=RequestContext("ratings.answers.delete", allow_retry=True),
        )
        return map_review_answer(payload)

    def get_ratings_info_v1(self) -> RatingProfileInfo:
        payload = self.transport.request_json(
            "GET",
            "/ratings/v1/info",
            context=RequestContext("ratings.info.get"),
        )
        return map_rating_profile(payload)

    def list_reviews_v1(self, *, params: Mapping[str, object] | None = None) -> ReviewsResult:
        payload = self.transport.request_json(
            "GET",
            "/ratings/v1/reviews",
            context=RequestContext("ratings.reviews.list"),
            params=params,
        )
        return map_reviews(payload)
