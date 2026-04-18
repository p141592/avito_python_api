"""Внутренние section clients для пакета tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.tariffs.mappers import map_tariff_info
from avito.tariffs.models import TariffInfo


@dataclass(slots=True)
class TariffsClient:
    """Выполняет HTTP-операции тарифов."""

    transport: Transport

    def get_tariff_info(self) -> TariffInfo:
        payload = self.transport.request_json(
            "GET",
            "/tariff/info/1",
            context=RequestContext("tariffs.info.get"),
        )
        return map_tariff_info(payload)
