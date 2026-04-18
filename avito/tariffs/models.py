"""Типизированные модели раздела tariffs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class TariffContractInfo:
    """Информация о текущем или запланированном тарифном контракте."""

    level: str | None
    is_active: bool | None
    start_time: int | None
    close_time: int | None
    bonus: int | None
    price: float | None
    original_price: float | None
    packages_count: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TariffInfo:
    """Информация по текущему и запланированному тарифу."""

    current: TariffContractInfo | None = None
    scheduled: TariffContractInfo | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)
