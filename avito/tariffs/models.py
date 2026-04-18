"""Типизированные модели раздела tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import enable_module_serialization


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


@dataclass(slots=True, frozen=True)
class TariffInfo:
    """Информация по текущему и запланированному тарифу."""

    current: TariffContractInfo | None = None
    scheduled: TariffContractInfo | None = None


enable_module_serialization(globals())
