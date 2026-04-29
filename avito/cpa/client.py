"""Внутренние section clients для пакета cpa."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.core.mapping import request_public_model
from avito.cpa.mappers import (
    map_balance,
    map_call_item,
    map_call_tracking_call_item,
    map_call_tracking_calls,
    map_calls,
    map_chat_item,
    map_chats,
    map_cpa_action,
    map_phones,
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

_CPA_HEADERS = {"X-Source": "avito-py"}


def _cpa_context(operation_name: str, *, allow_retry: bool = False) -> RequestContext:
    return RequestContext(
        operation_name,
        allow_retry=allow_retry,
        headers=_CPA_HEADERS,
    )


@dataclass(slots=True, frozen=True)
class CpaChatsClient:
    """Выполняет HTTP-операции CPA-чатов."""

    transport: Transport

    def get_by_action_id(self, *, action_id: int | str) -> CpaChatInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/cpa/v1/chatByActionId/{action_id}",
            context=_cpa_context("cpa.chats.get_by_action_id"),
            mapper=map_chat_item,
        )

    def list_by_time_classic(self, *, created_at_from: str, limit: int | None = None) -> CpaChatsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/chatsByTime",
            context=_cpa_context("cpa.chats.list_by_time_classic", allow_retry=True),
            mapper=map_chats,
            json_body=CpaChatsByTimeRequest(
                created_at_from=created_at_from,
                limit=limit,
            ).to_payload(),
        )

    def list_by_time(self, *, created_at_from: str, limit: int | None = None) -> CpaChatsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/chatsByTime",
            context=_cpa_context("cpa.chats.list_by_time", allow_retry=True),
            mapper=map_chats,
            json_body=CpaChatsByTimeRequest(
                created_at_from=created_at_from,
                limit=limit,
            ).to_payload(),
        )

    def get_phones_info(self, *, action_ids: list[str]) -> CpaPhonesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/phonesInfoFromChats",
            context=_cpa_context("cpa.chats.get_phones_info", allow_retry=True),
            mapper=map_phones,
            json_body=CpaPhonesFromChatsRequest(action_ids=action_ids).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class CpaCallsClient:
    """Выполняет HTTP-операции CPA-звонков."""

    transport: Transport

    def list_by_time(self, *, date_time_from: str, date_time_to: str) -> CpaCallsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/callsByTime",
            context=_cpa_context("cpa.calls.list_by_time", allow_retry=True),
            mapper=map_calls,
            json_body=CpaCallsByTimeRequest(
                date_time_from=date_time_from,
                date_time_to=date_time_to,
            ).to_payload(),
        )

    def create_complaint(
        self,
        *,
        call_id: int,
        reason: str,
        idempotency_key: str | None = None,
    ) -> CpaActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/createComplaint",
            context=_cpa_context(
                "cpa.calls.create_complaint",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_cpa_action,
            json_body=CpaCallComplaintRequest(call_id=call_id, reason=reason).to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class CpaLeadsClient:
    """Выполняет HTTP-операции CPA-лидов и связанных сущностей."""

    transport: Transport

    def create_complaint_by_action_id(
        self,
        *,
        action_id: str,
        reason: str,
        idempotency_key: str | None = None,
    ) -> CpaActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/createComplaintByActionId",
            context=_cpa_context(
                "cpa.leads.create_complaint_by_action_id",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_cpa_action,
            json_body=CpaLeadComplaintRequest(action_id=action_id, reason=reason).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_balance_info(self) -> CpaBalanceInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v3/balanceInfo",
            context=_cpa_context("cpa.leads.get_balance_info", allow_retry=True),
            mapper=map_balance,
            json_body={},
        )


@dataclass(slots=True, frozen=True)
class CpaArchiveClient:
    """Выполняет архивные HTTP-операции CPA."""

    transport: Transport

    def get_record(self, *, call_id: int | str) -> CpaAudioRecord:
        binary = self.transport.download_binary(
            f"/cpa/v1/call/{call_id}",
            context=_cpa_context("cpa.archive.get_record"),
        )
        return CpaAudioRecord(binary)

    def get_balance_info(self) -> CpaBalanceInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/balanceInfo",
            context=_cpa_context("cpa.archive.get_balance_info", allow_retry=True),
            mapper=map_balance,
            json_body={},
        )

    def get_call_by_id(self, *, call_id: int) -> CpaCallInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/callById",
            context=_cpa_context("cpa.archive.get_call_by_id", allow_retry=True),
            mapper=map_call_item,
            json_body=CpaCallByIdRequest(call_id=call_id).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class CallTrackingClient:
    """Выполняет HTTP-операции CallTracking."""

    transport: Transport

    def get_call_by_id(self, *, call_id: int) -> CallTrackingCallResponse:
        return request_public_model(
            self.transport,
            "POST",
            "/calltracking/v1/getCallById/",
            context=RequestContext("cpa.calltracking.get_call_by_id", allow_retry=True),
            mapper=map_call_tracking_call_item,
            json_body=CallTrackingGetCallByIdRequest(call_id=call_id).to_payload(),
        )

    def get_calls(
        self,
        *,
        date_time_from: str,
        date_time_to: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> CallTrackingCallsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/calltracking/v1/getCalls/",
            context=RequestContext("cpa.calltracking.get_calls", allow_retry=True),
            mapper=map_call_tracking_calls,
            json_body=CallTrackingCallsRequest(
                date_time_from=date_time_from,
                date_time_to=date_time_to,
                limit=limit,
                offset=offset,
            ).to_payload(),
        )

    def get_record_by_call_id(self, *, call_id: int | str) -> CallTrackingRecord:
        binary = self.transport.download_binary(
            "/calltracking/v1/getRecordByCallId/",
            context=RequestContext("cpa.calltracking.get_record_by_call_id"),
            params={"callId": call_id},
        )
        return CallTrackingRecord(binary)
