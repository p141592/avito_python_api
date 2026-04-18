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


@dataclass(slots=True)
class CpaChatsClient:
    """Выполняет HTTP-операции CPA-чатов."""

    transport: Transport

    def get_by_action_id(self, *, action_id: int | str) -> CpaChatInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/cpa/v1/chatByActionId/{action_id}",
            context=RequestContext("cpa.chats.get_by_action_id"),
            mapper=map_chat_item,
        )

    def list_by_time_v1(self, request: CpaChatsByTimeRequest) -> CpaChatsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/chatsByTime",
            context=RequestContext("cpa.chats.list_by_time_v1", allow_retry=True),
            mapper=map_chats,
            json_body=request.to_payload(),
        )

    def list_by_time_v2(self, request: CpaChatsByTimeRequest) -> CpaChatsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/chatsByTime",
            context=RequestContext("cpa.chats.list_by_time_v2", allow_retry=True),
            mapper=map_chats,
            json_body=request.to_payload(),
        )

    def get_phones_info(self, request: CpaPhonesFromChatsRequest) -> CpaPhonesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/phonesInfoFromChats",
            context=RequestContext("cpa.chats.get_phones_info", allow_retry=True),
            mapper=map_phones,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class CpaCallsClient:
    """Выполняет HTTP-операции CPA-звонков."""

    transport: Transport

    def list_by_time_v2(self, request: CpaCallsByTimeRequest) -> CpaCallsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/callsByTime",
            context=RequestContext("cpa.calls.list_by_time_v2", allow_retry=True),
            mapper=map_calls,
            json_body=request.to_payload(),
        )

    def create_complaint(self, request: CpaCallComplaintRequest) -> CpaActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/createComplaint",
            context=RequestContext("cpa.calls.create_complaint", allow_retry=True),
            mapper=map_cpa_action,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class CpaLeadsClient:
    """Выполняет HTTP-операции CPA-лидов и связанных сущностей."""

    transport: Transport

    def create_complaint_by_action_id(self, request: CpaLeadComplaintRequest) -> CpaActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v1/createComplaintByActionId",
            context=RequestContext("cpa.leads.create_complaint_by_action_id", allow_retry=True),
            mapper=map_cpa_action,
            json_body=request.to_payload(),
        )

    def get_balance_info_v3(self) -> CpaBalanceInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v3/balanceInfo",
            context=RequestContext("cpa.leads.get_balance_info_v3", allow_retry=True),
            mapper=map_balance,
            json_body={},
        )


@dataclass(slots=True)
class CpaLegacyClient:
    """Выполняет legacy HTTP-операции CPA."""

    transport: Transport

    def get_record(self, *, call_id: int | str) -> CpaAudioRecord:
        binary = self.transport.download_binary(
            f"/cpa/v1/call/{call_id}",
            context=RequestContext("cpa.legacy.get_record"),
        )
        return CpaAudioRecord(binary)

    def get_balance_info_v2(self) -> CpaBalanceInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/balanceInfo",
            context=RequestContext("cpa.legacy.get_balance_info_v2", allow_retry=True),
            mapper=map_balance,
            json_body={},
        )

    def get_call_by_id_v2(self, request: CpaCallByIdRequest) -> CpaCallInfo:
        return request_public_model(
            self.transport,
            "POST",
            "/cpa/v2/callById",
            context=RequestContext("cpa.legacy.get_call_by_id_v2", allow_retry=True),
            mapper=map_call_item,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class CallTrackingClient:
    """Выполняет HTTP-операции CallTracking."""

    transport: Transport

    def get_call_by_id(self, request: CallTrackingGetCallByIdRequest) -> CallTrackingCallResponse:
        return request_public_model(
            self.transport,
            "POST",
            "/calltracking/v1/getCallById/",
            context=RequestContext("cpa.calltracking.get_call_by_id", allow_retry=True),
            mapper=map_call_tracking_call_item,
            json_body=request.to_payload(),
        )

    def get_calls(self, request: CallTrackingCallsRequest) -> CallTrackingCallsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/calltracking/v1/getCalls/",
            context=RequestContext("cpa.calltracking.get_calls", allow_retry=True),
            mapper=map_call_tracking_calls,
            json_body=request.to_payload(),
        )

    def get_record_by_call_id(self, *, call_id: int | str) -> CallTrackingRecord:
        binary = self.transport.download_binary(
            "/calltracking/v1/getRecordByCallId/",
            context=RequestContext("cpa.calltracking.get_record_by_call_id"),
            params={"callId": call_id},
        )
        return CallTrackingRecord(binary)
