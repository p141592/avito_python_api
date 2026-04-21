"""Типизированные модели раздела tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class TariffContractInfo(SerializableModel):
    """Информация о текущем или запланированном тарифном контракте."""

    level: str | None
    is_active: bool | None
    start_time: int | None
    close_time: int | None
    bonus: int | None
    price: float | None
    original_price: float | None
    packages_count: int | None


@dataclass(slots=True, frozen=True)
class TariffInfo(SerializableModel):
    """Информация по текущему и запланированному тарифу."""

    current: TariffContractInfo | None = None
    scheduled: TariffContractInfo | None = None
