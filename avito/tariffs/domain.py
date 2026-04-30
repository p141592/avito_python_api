"""Доменные объекты пакета tariffs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.tariffs.models import TariffInfo
from avito.tariffs.operations import GET_TARIFF_INFO


@dataclass(slots=True, frozen=True)
class Tariff(DomainObject):
    """Доменный объект тарифа."""

    __swagger_domain__ = "tariffs"
    __sdk_factory__ = "tariff"
    __sdk_factory_args__ = {"tariff_id": "path.tariff_id"}

    tariff_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/tariff/info/1",
        spec="Тарифы.json",
        operation_id="getTariffInfo",
    )
    def get_tariff_info(self) -> TariffInfo:
        """Получает информацию о тарифе аккаунта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_TARIFF_INFO)


__all__ = ("Tariff",)
