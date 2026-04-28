"""Enum-значения раздела ratings."""

from __future__ import annotations

from enum import Enum


class ReviewStage(str, Enum):
    """Этап обработки отзыва."""

    UNKNOWN = "__unknown__"
    DONE = "done"
    FELL_THROUGH = "fell_through"
    NOT_AGREE = "not_agree"
    NOT_COMMUNICATE = "not_communicate"


class ReviewAnswerStatus(str, Enum):
    """Статус ответа на отзыв."""

    UNKNOWN = "__unknown__"
    MODERATION = "moderation"
    PUBLISHED = "published"
    REJECTED = "rejected"


__all__ = ("ReviewAnswerStatus", "ReviewStage")
