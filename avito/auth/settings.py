"""Настройки аутентификации SDK Avito."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from avito._env import resolve_env_aliases
from avito.core.exceptions import ConfigurationError


@dataclass(slots=True, frozen=True)
class AuthSettings:
    """Единственный публичный контракт OAuth-конфигурации SDK."""

    ENV_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "client_id": ("AVITO_CLIENT_ID",),
        "client_secret": ("AVITO_CLIENT_SECRET", "AVITO_SECRET"),
        "scope": ("AVITO_SCOPE",),
        "refresh_token": ("AVITO_REFRESH_TOKEN",),
        "token_url": ("AVITO_TOKEN_URL",),
        "alternate_token_url": ("AVITO_ALTERNATE_TOKEN_URL",),
        "autoteka_token_url": ("AVITO_AUTOTEKA_TOKEN_URL",),
        "autoteka_client_id": ("AVITO_AUTOTEKA_CLIENT_ID",),
        "autoteka_client_secret": ("AVITO_AUTOTEKA_CLIENT_SECRET",),
        "autoteka_scope": ("AVITO_AUTOTEKA_SCOPE",),
    }

    client_id: str | None = None
    client_secret: str | None = None
    scope: str | None = None
    refresh_token: str | None = None
    token_url: str = "/token"
    alternate_token_url: str = "/token"
    autoteka_token_url: str = "/autoteka/token"
    autoteka_client_id: str | None = None
    autoteka_client_secret: str | None = None
    autoteka_scope: str | None = None

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = ".env") -> AuthSettings:
        """Загружает auth-настройки из процесса и optional `.env` файла."""

        resolved_values = resolve_env_aliases(cls.ENV_ALIASES, env_file=env_file)
        return cls(**resolved_values).validate_required()

    @classmethod
    def supported_env_vars(cls) -> dict[str, tuple[str, ...]]:
        """Возвращает документированный набор env-переменных и alias-имен."""

        return dict(cls.ENV_ALIASES)

    def validate_required(self) -> AuthSettings:
        """Проверяет обязательные поля OAuth-конфигурации."""

        missing_fields: list[str] = []
        if not self.client_id:
            missing_fields.append("client_id: " + ", ".join(self.ENV_ALIASES["client_id"]))
        if not self.client_secret:
            missing_fields.append("client_secret: " + ", ".join(self.ENV_ALIASES["client_secret"]))
        if missing_fields:
            raise ConfigurationError(
                "Не заданы обязательные настройки OAuth. Ожидаются "
                + "; ".join(missing_fields)
                + "."
            )
        return self


__all__ = ("AuthSettings",)
