"""Базовый доменный объект SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avito.core.exceptions import ValidationError

if TYPE_CHECKING:
    from avito.core.transport import Transport


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект с доступом к transport-слою."""

    transport: Transport

    def _resolve_user_id(self, user_id: int | str | None = None) -> int:
        """Возвращает user_id из аргумента, настроек SDK или профиля текущего пользователя."""

        if user_id is not None:
            return int(user_id)

        configured_user_id = self.transport.debug_info().user_id
        if configured_user_id is not None:
            return configured_user_id

        from avito.accounts.client import AccountsClient

        profile = AccountsClient(self.transport).get_self()
        if profile.user_id is None:
            raise ValidationError(
                "Для операции требуется `user_id`: передайте его в фабрику клиента, "
                "в метод операции или задайте `AVITO_USER_ID`."
            )
        return profile.user_id


__all__ = ("DomainObject",)
