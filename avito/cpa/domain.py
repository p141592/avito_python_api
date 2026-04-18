"""Доменные объекты пакета cpa."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import Transport
from avito.cpa.client import (
    CallTrackingClient,
    CpaCallsClient,
    CpaChatsClient,
    CpaLeadsClient,
    CpaLegacyClient,
)
from avito.cpa.models import (
    CallTrackingCallInfo,
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
    JsonRequest,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела cpa."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class CpaLead(DomainObject):
    """Доменный объект CPA-лида и связанных lead-операций."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_complaint_by_action_id(self, *, payload: Mapping[str, object]) -> CpaActionResult:
        return CpaLeadsClient(self.transport).create_complaint_by_action_id(JsonRequest(payload))

    def create_balance_info_v3(self, *, payload: Mapping[str, object] | None = None) -> CpaBalanceInfo:
        return CpaLeadsClient(self.transport).get_balance_info_v3(JsonRequest(payload or {}))


@dataclass(slots=True, frozen=True)
class CpaChat(DomainObject):
    """Доменный объект CPA-чата."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, action_id: int | str | None = None) -> CpaChatInfo:
        return CpaChatsClient(self.transport).get_by_action_id(action_id=action_id or self._require_resource_id())

    def list(
        self,
        *,
        payload: Mapping[str, object],
        version: int = 2,
    ) -> CpaChatsResult:
        client = CpaChatsClient(self.transport)
        request = JsonRequest(payload)
        if version == 1:
            return client.list_by_time_v1(request)
        return client.list_by_time_v2(request)

    def get_phones_info_from_chats(self, *, payload: Mapping[str, object]) -> CpaPhonesResult:
        return CpaChatsClient(self.transport).get_phones_info(JsonRequest(payload))

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `action_id` или `chat_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class CpaCall(DomainObject):
    """Доменный объект CPA-звонка."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list(self, *, payload: Mapping[str, object]) -> CpaCallsResult:
        return CpaCallsClient(self.transport).list_by_time_v2(JsonRequest(payload))

    def create_create_complaint(self, *, payload: Mapping[str, object]) -> CpaActionResult:
        return CpaCallsClient(self.transport).create_complaint(JsonRequest(payload))


@dataclass(slots=True, frozen=True)
class CpaLegacy(DomainObject):
    """Доменный объект legacy-операций CPA."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def legacy_get_call(self, *, call_id: int | str | None = None) -> CpaAudioRecord:
        return CpaLegacyClient(self.transport).get_record(call_id=call_id or self._require_resource_id())

    def legacy_create_balance_info_v2(
        self,
        *,
        payload: Mapping[str, object] | None = None,
    ) -> CpaBalanceInfo:
        return CpaLegacyClient(self.transport).get_balance_info_v2(JsonRequest(payload or {}))

    def legacy_create_call_by_id_v2(self, *, payload: Mapping[str, object]) -> CpaCallInfo:
        return CpaLegacyClient(self.transport).get_call_by_id_v2(JsonRequest(payload))

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `call_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class CallTrackingCall(DomainObject):
    """Доменный объект CallTracking."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, payload: Mapping[str, object] | None = None) -> CallTrackingCallInfo:
        request_payload = dict(payload or {})
        if "callId" not in request_payload and self.resource_id is not None:
            request_payload["callId"] = self.resource_id
        return CallTrackingClient(self.transport).get_call_by_id(JsonRequest(request_payload))

    def list(self, *, payload: Mapping[str, object]) -> CallTrackingCallsResult:
        return CallTrackingClient(self.transport).get_calls(JsonRequest(payload))

    def download(self, *, call_id: int | str | None = None) -> CallTrackingRecord:
        return CallTrackingClient(self.transport).get_record_by_call_id(
            call_id=call_id or self._require_resource_id()
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `call_id`.")
        return str(self.resource_id)


__all__ = ("CallTrackingCall", "CpaCall", "CpaChat", "CpaLead", "CpaLegacy", "DomainObject")
