"""Публичные экспорты пакета SDK для Avito."""

from typing import TYPE_CHECKING

from avito.client import AvitoClient
from avito.config import AvitoSettings

if TYPE_CHECKING:
    from avito.auth.settings import AuthSettings

__all__ = ("AuthSettings", "AvitoClient", "AvitoSettings")


def __getattr__(name: str) -> object:
    if name == "AuthSettings":
        from avito.auth.settings import AuthSettings

        return AuthSettings
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
