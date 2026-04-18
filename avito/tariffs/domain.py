"""Доменные объекты пакета tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import Transport
from avito.tariffs.client import TariffsClient
from avito.tariffs.models import TariffInfo


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела tariffs."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class Tariff(DomainObject):
    """Доменный объект тарифа."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_tariff_info(self) -> TariffInfo:
        return TariffsClient(self.transport).get_tariff_info()


__all__ = ("DomainObject", "Tariff")
