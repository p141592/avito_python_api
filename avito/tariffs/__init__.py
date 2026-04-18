"""Пакет tariffs."""

from avito.tariffs.domain import DomainObject, Tariff
from avito.tariffs.models import TariffContractInfo, TariffInfo

__all__ = ("DomainObject", "Tariff", "TariffContractInfo", "TariffInfo")
