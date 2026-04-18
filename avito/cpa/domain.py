"""Доменные объекты пакета cpa."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import Transport, ValidationError
from avito.cpa.client import (
    CallTrackingClient,
    CpaCallsClient,
    CpaChatsClient,
    CpaLeadsClient,
    CpaLegacyClient,
)
from avito.cpa.models import (
    CallTrackingCallResponse,
    CallTrackingCallsRequest,
    CallTrackingCallsResult,
    CallTrackingGetCallByIdRequest,
    CallTrackingRecord,
    CpaActionResult,
    CpaAudioRecord,
    CpaBalanceInfo,
    CpaCallByIdRequest,
    CpaCallComplaintRequest,
    CpaCallInfo,
    CpaCallsByTimeRequest,
    CpaCallsResult,
    CpaChatInfo,
    CpaChatsByTimeRequest,
    CpaChatsResult,
    CpaLeadComplaintRequest,
    CpaPhonesFromChatsRequest,
    CpaPhonesResult,
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

    def create_complaint_by_action_id(
        self,
        *,
        request: CpaLeadComplaintRequest,
    ) -> CpaActionResult:
        return CpaLeadsClient(self.transport).create_complaint_by_action_id(request)

    def create_balance_info_v3(self) -> CpaBalanceInfo:
        return CpaLeadsClient(self.transport).get_balance_info_v3()


@dataclass(slots=True, frozen=True)
class CpaChat(DomainObject):
    """Доменный объект CPA-чата."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, action_id: int | str | None = None) -> CpaChatInfo:
        return CpaChatsClient(self.transport).get_by_action_id(
            action_id=action_id or self._require_resource_id()
        )

    def list(
        self,
        *,
        request: CpaChatsByTimeRequest,
        version: int = 2,
    ) -> CpaChatsResult:
        client = CpaChatsClient(self.transport)
        if version == 1:
            return client.list_by_time_v1(request)
        return client.list_by_time_v2(request)

    def get_phones_info_from_chats(
        self,
        *,
        request: CpaPhonesFromChatsRequest,
    ) -> CpaPhonesResult:
        return CpaChatsClient(self.transport).get_phones_info(request)

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `action_id` или `chat_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class CpaCall(DomainObject):
    """Доменный объект CPA-звонка."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list(self, *, request: CpaCallsByTimeRequest) -> CpaCallsResult:
        return CpaCallsClient(self.transport).list_by_time_v2(request)

    def create_complaint(self, *, request: CpaCallComplaintRequest) -> CpaActionResult:
        return CpaCallsClient(self.transport).create_complaint(request)


@dataclass(slots=True, frozen=True)
class CpaLegacy(DomainObject):
    """Доменный объект legacy-операций CPA."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_call(self, *, call_id: int | str | None = None) -> CpaAudioRecord:
        return CpaLegacyClient(self.transport).get_record(
            call_id=call_id or self._require_resource_id()
        )

    def get_balance_info_v2(self) -> CpaBalanceInfo:
        return CpaLegacyClient(self.transport).get_balance_info_v2()

    def get_call_by_id_v2(self, *, request: CpaCallByIdRequest) -> CpaCallInfo:
        return CpaLegacyClient(self.transport).get_call_by_id_v2(request)

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class CallTrackingCall(DomainObject):
    """Доменный объект CallTracking."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self, *, call_id: int | None = None) -> CallTrackingCallResponse:
        resolved_call_id = call_id or (
            int(self.resource_id) if self.resource_id is not None else None
        )
        if resolved_call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return CallTrackingClient(self.transport).get_call_by_id(
            CallTrackingGetCallByIdRequest(call_id=resolved_call_id)
        )

    def list(self, *, request: CallTrackingCallsRequest) -> CallTrackingCallsResult:
        return CallTrackingClient(self.transport).get_calls(request)

    def download(self, *, call_id: int | str | None = None) -> CallTrackingRecord:
        return CallTrackingClient(self.transport).get_record_by_call_id(
            call_id=call_id or self._require_resource_id()
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.resource_id)


__all__ = ("CallTrackingCall", "CpaCall", "CpaChat", "CpaLead", "CpaLegacy", "DomainObject")
