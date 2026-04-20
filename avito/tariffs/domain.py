"""Доменные объекты пакета tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.domain import DomainObject
from avito.tariffs.client import TariffsClient
from avito.tariffs.models import TariffInfo


@dataclass(slots=True, frozen=True)
class Tariff(DomainObject):
    """Доменный объект тарифа."""

    tariff_id: int | str | None = None

    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе аккаунта."""

        return TariffsClient(self.transport).get_tariff_info()


__all__ = ("Tariff",)
