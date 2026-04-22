"""Доменные объекты пакета cpa."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.cpa.client import (
    CallTrackingClient,
    CpaArchiveClient,
    CpaCallsClient,
    CpaChatsClient,
    CpaLeadsClient,
)
from avito.cpa.models import (
    CallTrackingCallResponse,
    CallTrackingCallsResult,
    CallTrackingRecord,
    CpaActionResult,
    CpaAudioRecord,
    CpaBalanceInfo,
    CpaCallInfo,
    CpaCallsResult,
    CpaChatInfo,
    CpaChatsResult,
    CpaPhonesResult,
)


@dataclass(slots=True, frozen=True)
class CpaLead(DomainObject):
    """Доменный объект CPA-лида и связанных lead-операций."""

    user_id: int | str | None = None

    def create_complaint_by_action_id(
        self,
        *,
        action_id: str,
        reason: str,
    ) -> CpaActionResult:
        return CpaLeadsClient(self.transport).create_complaint_by_action_id(
            action_id=action_id,
            reason=reason,
        )

    def get_balance_info(self) -> CpaBalanceInfo:
        return CpaLeadsClient(self.transport).get_balance_info()


@dataclass(slots=True, frozen=True)
class CpaChat(DomainObject):
    """Доменный объект CPA-чата."""

    action_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, action_id: int | str | None = None) -> CpaChatInfo:
        return CpaChatsClient(self.transport).get_by_action_id(
            action_id=action_id or self._require_action_id()
        )

    def list(
        self,
        *,
        created_at_from: str,
        limit: int | None = None,
        version: int = 2,
    ) -> CpaChatsResult:
        client = CpaChatsClient(self.transport)
        if version == 1:
            return client.list_by_time_classic(created_at_from=created_at_from, limit=limit)
        return client.list_by_time(created_at_from=created_at_from, limit=limit)

    def get_phones_info_from_chats(
        self,
        *,
        action_ids: Sequence[str],
    ) -> CpaPhonesResult:
        return CpaChatsClient(self.transport).get_phones_info(action_ids=list(action_ids))

    def _require_action_id(self) -> str:
        if self.action_id is None:
            raise ValidationError("Для операции требуется `action_id`.")
        return str(self.action_id)


@dataclass(slots=True, frozen=True)
class CpaCall(DomainObject):
    """Доменный объект CPA-звонка."""

    user_id: int | str | None = None

    def list(self, *, date_time_from: str, date_time_to: str) -> CpaCallsResult:
        return CpaCallsClient(self.transport).list_by_time(
            date_time_from=date_time_from,
            date_time_to=date_time_to,
        )

    def create_complaint(self, *, call_id: int, reason: str) -> CpaActionResult:
        return CpaCallsClient(self.transport).create_complaint(call_id=call_id, reason=reason)


@dataclass(slots=True, frozen=True)
class CpaArchive(DomainObject):
    """Доменный объект архивных операций CPA."""

    call_id: int | str | None = None
    user_id: int | str | None = None

    def get_call(self, *, call_id: int | str | None = None) -> CpaAudioRecord:
        return CpaArchiveClient(self.transport).get_record(
            call_id=call_id or self._require_call_id()
        )

    def get_balance_info(self) -> CpaBalanceInfo:
        return CpaArchiveClient(self.transport).get_balance_info()

    def get_call_by_id(self, *, call_id: int) -> CpaCallInfo:
        return CpaArchiveClient(self.transport).get_call_by_id(call_id=call_id)

    def _require_call_id(self) -> str:
        if self.call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.call_id)


@dataclass(slots=True, frozen=True)
class CallTrackingCall(DomainObject):
    """Доменный объект CallTracking."""

    call_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, call_id: int | None = None) -> CallTrackingCallResponse:
        resolved_call_id = call_id or (
            int(self.call_id) if self.call_id is not None else None
        )
        if resolved_call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return CallTrackingClient(self.transport).get_call_by_id(call_id=resolved_call_id)

    def list(
        self,
        *,
        date_time_from: str,
        date_time_to: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> CallTrackingCallsResult:
        return CallTrackingClient(self.transport).get_calls(
            date_time_from=date_time_from,
            date_time_to=date_time_to,
            limit=limit,
            offset=offset,
        )

    def download(self, *, call_id: int | str | None = None) -> CallTrackingRecord:
        return CallTrackingClient(self.transport).get_record_by_call_id(
            call_id=call_id or self._require_call_id()
        )

    def _require_call_id(self) -> str:
        if self.call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.call_id)


__all__ = ("CallTrackingCall", "CpaArchive", "CpaCall", "CpaChat", "CpaLead")
