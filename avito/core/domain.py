"""Базовый доменный объект SDK."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.transport import Transport


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект с доступом к transport-слою."""

    transport: Transport


__all__ = ("DomainObject",)
