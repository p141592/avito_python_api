"""Enum-значения раздела ratings."""

from __future__ import annotations

from enum import Enum


class ReviewStage(str, Enum):
    """Этап обработки отзыва."""

    UNKNOWN = "__unknown__"
    DONE = "done"


__all__ = ("ReviewStage",)
