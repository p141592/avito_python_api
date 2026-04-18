"""Настройки аутентификации SDK Avito."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from avito._env import resolve_env_aliases
from avito.core.exceptions import ConfigurationError


class AuthSettings(BaseModel):
    """Единственный публичный контракт OAuth-конфигурации SDK."""

    ENV_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "client_id": ("AVITO_AUTH__CLIENT_ID", "AVITO_CLIENT_ID", "CLIENT_ID"),
        "client_secret": (
            "AVITO_AUTH__CLIENT_SECRET",
            "AVITO_CLIENT_SECRET",
            "AVITO_SECRET",
            "CLIENT_SECRET",
            "SECRET",
        ),
        "scope": ("AVITO_AUTH__SCOPE", "AVITO_SCOPE", "SCOPE"),
        "refresh_token": (
            "AVITO_AUTH__REFRESH_TOKEN",
            "AVITO_REFRESH_TOKEN",
            "REFRESH_TOKEN",
        ),
        "token_url": ("AVITO_AUTH__TOKEN_URL", "AVITO_TOKEN_URL", "TOKEN_URL"),
        "legacy_token_url": (
            "AVITO_AUTH__LEGACY_TOKEN_URL",
            "AVITO_LEGACY_TOKEN_URL",
            "LEGACY_TOKEN_URL",
        ),
        "autoteka_token_url": (
            "AVITO_AUTH__AUTOTEKA_TOKEN_URL",
            "AVITO_AUTOTEKA_TOKEN_URL",
            "AUTOTEKA_TOKEN_URL",
        ),
        "autoteka_client_id": (
            "AVITO_AUTH__AUTOTEKA_CLIENT_ID",
            "AVITO_AUTOTEKA_CLIENT_ID",
            "AUTOTEKA_CLIENT_ID",
        ),
        "autoteka_client_secret": (
            "AVITO_AUTH__AUTOTEKA_CLIENT_SECRET",
            "AVITO_AUTOTEKA_CLIENT_SECRET",
            "AUTOTEKA_CLIENT_SECRET",
        ),
        "autoteka_scope": (
            "AVITO_AUTH__AUTOTEKA_SCOPE",
            "AVITO_AUTOTEKA_SCOPE",
            "AUTOTEKA_SCOPE",
        ),
    }

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AVITO_AUTH__CLIENT_ID", "AVITO_CLIENT_ID", "CLIENT_ID"),
    )
    client_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AVITO_AUTH__CLIENT_SECRET",
            "AVITO_CLIENT_SECRET",
            "AVITO_SECRET",
            "CLIENT_SECRET",
            "SECRET",
        ),
    )
    scope: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AVITO_AUTH__SCOPE", "AVITO_SCOPE", "SCOPE"),
    )
    refresh_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AVITO_AUTH__REFRESH_TOKEN", "AVITO_REFRESH_TOKEN", "REFRESH_TOKEN"
        ),
    )
    token_url: str = Field(
        default="/token",
        validation_alias=AliasChoices("AVITO_AUTH__TOKEN_URL", "AVITO_TOKEN_URL", "TOKEN_URL"),
    )
    legacy_token_url: str = Field(
        default="/token",
        validation_alias=AliasChoices(
            "AVITO_AUTH__LEGACY_TOKEN_URL",
            "AVITO_LEGACY_TOKEN_URL",
            "LEGACY_TOKEN_URL",
        ),
    )
    autoteka_token_url: str = Field(
        default="/autoteka/token",
        validation_alias=AliasChoices(
            "AVITO_AUTH__AUTOTEKA_TOKEN_URL",
            "AVITO_AUTOTEKA_TOKEN_URL",
            "AUTOTEKA_TOKEN_URL",
        ),
    )
    autoteka_client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AVITO_AUTH__AUTOTEKA_CLIENT_ID",
            "AVITO_AUTOTEKA_CLIENT_ID",
            "AUTOTEKA_CLIENT_ID",
        ),
    )
    autoteka_client_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AVITO_AUTH__AUTOTEKA_CLIENT_SECRET",
            "AVITO_AUTOTEKA_CLIENT_SECRET",
            "AUTOTEKA_CLIENT_SECRET",
        ),
    )
    autoteka_scope: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "AVITO_AUTH__AUTOTEKA_SCOPE",
            "AVITO_AUTOTEKA_SCOPE",
            "AUTOTEKA_SCOPE",
        ),
    )

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
