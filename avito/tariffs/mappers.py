"""Мапперы JSON -> dataclass для пакета tariffs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.tariffs.models import TariffContractInfo, TariffInfo

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def _float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _map_contract(payload: Payload) -> TariffContractInfo | None:
    if not payload:
        return None
    price = _mapping(payload, "price")
    packages = payload.get("packages")
    packages_count = len(packages) if isinstance(packages, list) else None
    return TariffContractInfo(
        level=_str(payload, "level"),
        is_active=_bool(payload, "isActive"),
        start_time=_int(payload, "startTime"),
        close_time=_int(payload, "closeTime"),
        bonus=_int(payload, "bonus"),
        price=_float(price, "price"),
        original_price=_float(price, "originalPrice"),
        packages_count=packages_count,
    )


def map_tariff_info(payload: object) -> TariffInfo:
    """Преобразует информацию о тарифе."""

    data = _expect_mapping(payload)
    return TariffInfo(
        current=_map_contract(_mapping(data, "current")),
        scheduled=_map_contract(_mapping(data, "scheduled")),
    )
