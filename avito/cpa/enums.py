"""Enum-значения раздела cpa."""

from __future__ import annotations

from enum import IntEnum


class CpaCallStatusId(IntEnum):
    """Числовой статус CPA-звонка."""

    NEW = 0
    ACCEPTED = 1
    REJECTED = 2
    PAID = 3


__all__ = ("CpaCallStatusId",)
