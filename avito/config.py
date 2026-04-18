"""Конфигурация SDK Avito и параметры transport-слоя."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from avito._env import resolve_env_aliases
from avito.auth.settings import AuthSettings
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


def _default_timeouts() -> ApiTimeouts:
    return ApiTimeouts(_env_file=None)  # type: ignore[call-arg]


def _default_retry_policy() -> RetryPolicy:
    return RetryPolicy(_env_file=None)  # type: ignore[call-arg]


class AvitoSettings(BaseModel):
    """Единственный публичный контракт конфигурации SDK."""

    ENV_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "base_url": ("AVITO_BASE_URL", "BASE_URL"),
        "user_id": ("AVITO_USER_ID", "USER_ID"),
    }

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    base_url: str = Field(
        default="https://api.avito.ru",
        validation_alias=AliasChoices("BASE_URL", "AVITO_BASE_URL"),
    )
    user_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("USER_ID", "AVITO_USER_ID"),
    )
    auth: AuthSettings = Field(default_factory=AuthSettings)
    timeouts: ApiTimeouts = Field(default_factory=_default_timeouts)
    retry_policy: RetryPolicy = Field(default_factory=_default_retry_policy)

    @property
    def client_id(self) -> str | None:
        """Возвращает `client_id` для совместимости со старым API."""

        return self.auth.client_id

    @property
    def client_secret(self) -> str | None:
        """Возвращает `client_secret` для совместимости со старым API."""

        return self.auth.client_secret

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = ".env") -> AvitoSettings:
        """Загружает конфигурацию из окружения и optional `.env` файла."""

        resolved_values = resolve_env_aliases(cls.ENV_ALIASES, env_file=env_file)
        auth_settings = AuthSettings.from_env(env_file=env_file)
        return cls.model_validate(
            {
                **resolved_values,
                "auth": auth_settings,
                "timeouts": ApiTimeouts(_env_file=env_file),  # type: ignore[call-arg]
                "retry_policy": RetryPolicy(_env_file=env_file),  # type: ignore[call-arg]
            }
        ).validate_required()

    @classmethod
    def supported_env_vars(cls) -> dict[str, tuple[str, ...]]:
        """Возвращает документированный набор env-переменных SDK."""

        env_vars = dict(cls.ENV_ALIASES)
        env_vars.update(
            {
                f"auth.{field_name}": aliases
                for field_name, aliases in AuthSettings.supported_env_vars().items()
            }
        )
        return env_vars

    def validate_required(self) -> AvitoSettings:
        """Проверяет обязательные части публичной конфигурации SDK."""

        self.auth.validate_required()
        return self


__all__ = ("AvitoSettings",)
