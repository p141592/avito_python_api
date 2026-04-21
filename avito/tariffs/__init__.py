"""Пакет tariffs."""

from avito.tariffs.domain import Tariff
from avito.tariffs.models import TariffContractInfo, TariffInfo

__all__ = ("Tariff", "TariffContractInfo", "TariffInfo")
