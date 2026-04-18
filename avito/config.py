"""Конфигурация SDK Avito и параметры transport-слоя."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from avito.auth.settings import AuthSettings
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


class AvitoSettings(BaseSettings):
    """Корневая конфигурация SDK с настройками transport и авторизации."""

    model_config = SettingsConfigDict(
        env_prefix="AVITO_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    base_url: str = "https://api.avito.ru"
    user_id: int | None = None
    auth: AuthSettings = Field(default_factory=AuthSettings)
    timeouts: ApiTimeouts = Field(default_factory=ApiTimeouts)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)

    @property
    def client_id(self) -> str | None:
        """Возвращает client id для совместимости с ранними версиями SDK."""

        return self.auth.client_id

    @property
    def client_secret(self) -> str | None:
        """Возвращает client secret для совместимости с ранними версиями SDK."""

        return self.auth.client_secret

    @classmethod
    def from_env(cls) -> AvitoSettings:
        """Загружает конфигурацию SDK из переменных окружения."""

        return cls()


__all__ = ("AvitoSettings",)
