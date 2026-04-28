"""Enum-значения раздела autoteka."""

from __future__ import annotations

from enum import Enum


class AutotekaStatus(str, Enum):
    """Статус сущности Автотеки."""

    UNKNOWN = "__unknown__"
    PROCESSING = "processing"
    SUCCESS = "success"
    NOT_FOUND = "notFound"
    INCOMPLETE = "incomplete"
    OK = "ok"
    WARNING = "warning"


__all__ = ("AutotekaStatus",)
