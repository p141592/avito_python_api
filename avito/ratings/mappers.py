"""Мапперы JSON -> dataclass для пакета ratings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.ratings.models import RatingProfileInfo, ReviewAnswerInfo, ReviewInfo, ReviewsResult

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def _float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def map_review_answer(payload: object) -> ReviewAnswerInfo:
    """Преобразует ответ на создание или удаление ответа."""

    data = _expect_mapping(payload)
    return ReviewAnswerInfo(
        answer_id=_str(data, "id"),
        created_at=_int(data, "createdAt"),
        success=_bool(data, "success"),
        _payload=data,
    )


def map_rating_profile(payload: object) -> RatingProfileInfo:
    """Преобразует профиль рейтинга."""

    data = _expect_mapping(payload)
    rating = _mapping(data, "rating")
    return RatingProfileInfo(
        is_enabled=bool(data.get("isEnabled", False)),
        score=_float(rating, "score"),
        reviews_count=_int(rating, "reviewsCount"),
        reviews_with_score_count=_int(rating, "reviewsWithScoreCount"),
        _payload=data,
    )


def map_reviews(payload: object) -> ReviewsResult:
    """Преобразует список отзывов."""

    data = _expect_mapping(payload)
    return ReviewsResult(
        items=[
            ReviewInfo(
                review_id=_str(item, "id"),
                score=_int(item, "score"),
                stage=_str(item, "stage"),
                text=_str(item, "text"),
                created_at=_int(item, "createdAt"),
                can_answer=_bool(item, "canAnswer"),
                used_in_score=_bool(item, "usedInScore"),
                _payload=item,
            )
            for item in _list(data, "reviews", "items")
        ],
        total=_int(data, "total"),
        _payload=data,
    )
