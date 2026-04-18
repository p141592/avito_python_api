"""Настройки аутентификации SDK Avito."""

from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Настройки OAuth и служебных токенов для transport-слоя."""

    model_config = SettingsConfigDict(
        env_prefix="AVITO_",
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CLIENT_ID", "AVITO_CLIENT_ID"),
    )
    client_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CLIENT_SECRET", "SECRET", "AVITO_CLIENT_SECRET", "AVITO_SECRET"),
    )
    scope: str | None = Field(default=None, validation_alias=AliasChoices("SCOPE", "AVITO_SCOPE"))
    refresh_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("REFRESH_TOKEN", "AVITO_REFRESH_TOKEN"),
    )
    token_url: str = Field(
        default="/token",
        validation_alias=AliasChoices("TOKEN_URL", "AVITO_TOKEN_URL"),
    )
    legacy_token_url: str = Field(
        default="/token",
        validation_alias=AliasChoices("LEGACY_TOKEN_URL", "AVITO_LEGACY_TOKEN_URL"),
    )
    autoteka_token_url: str = Field(
        default="/autoteka/token",
        validation_alias=AliasChoices("AUTOTEKA_TOKEN_URL", "AVITO_AUTOTEKA_TOKEN_URL"),
    )
    autoteka_client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AUTOTEKA_CLIENT_ID", "AVITO_AUTOTEKA_CLIENT_ID"),
    )
    autoteka_client_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AUTOTEKA_CLIENT_SECRET", "AVITO_AUTOTEKA_CLIENT_SECRET"),
    )
    autoteka_scope: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AUTOTEKA_SCOPE", "AVITO_AUTOTEKA_SCOPE"),
    )


__all__ = ("AuthSettings",)
