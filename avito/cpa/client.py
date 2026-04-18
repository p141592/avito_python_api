"""Внутренние section clients для пакета cpa."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
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


@dataclass(slots=True)
class CpaChatsClient:
    """Выполняет HTTP-операции CPA-чатов."""

    transport: Transport

    def get_by_action_id(self, *, action_id: int | str) -> CpaChatInfo:
        payload = self.transport.request_json(
            "GET",
            f"/cpa/v1/chatByActionId/{action_id}",
            context=RequestContext("cpa.chats.get_by_action_id"),
        )
        return map_chat_item(payload)

    def list_by_time_v1(self, request: JsonRequest) -> CpaChatsResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v1/chatsByTime",
            context=RequestContext("cpa.chats.list_by_time_v1", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_chats(payload)

    def list_by_time_v2(self, request: JsonRequest) -> CpaChatsResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v2/chatsByTime",
            context=RequestContext("cpa.chats.list_by_time_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_chats(payload)

    def get_phones_info(self, request: JsonRequest) -> CpaPhonesResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v1/phonesInfoFromChats",
            context=RequestContext("cpa.chats.get_phones_info", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_phones(payload)


@dataclass(slots=True)
class CpaCallsClient:
    """Выполняет HTTP-операции CPA-звонков."""

    transport: Transport

    def list_by_time_v2(self, request: JsonRequest) -> CpaCallsResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v2/callsByTime",
            context=RequestContext("cpa.calls.list_by_time_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_calls(payload)

    def create_complaint(self, request: JsonRequest) -> CpaActionResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v1/createComplaint",
            context=RequestContext("cpa.calls.create_complaint", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_cpa_action(payload)


@dataclass(slots=True)
class CpaLeadsClient:
    """Выполняет HTTP-операции CPA-лидов и связанных сущностей."""

    transport: Transport

    def create_complaint_by_action_id(self, request: JsonRequest) -> CpaActionResult:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v1/createComplaintByActionId",
            context=RequestContext("cpa.leads.create_complaint_by_action_id", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_cpa_action(payload)

    def get_balance_info_v3(self, request: JsonRequest) -> CpaBalanceInfo:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v3/balanceInfo",
            context=RequestContext("cpa.leads.get_balance_info_v3", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_balance(payload)


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

    def get_balance_info_v2(self, request: JsonRequest) -> CpaBalanceInfo:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v2/balanceInfo",
            context=RequestContext("cpa.legacy.get_balance_info_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_balance(payload)

    def get_call_by_id_v2(self, request: JsonRequest) -> CpaCallInfo:
        payload = self.transport.request_json(
            "POST",
            "/cpa/v2/callById",
            context=RequestContext("cpa.legacy.get_call_by_id_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_call_item(payload)


@dataclass(slots=True)
class CallTrackingClient:
    """Выполняет HTTP-операции CallTracking."""

    transport: Transport

    def get_call_by_id(self, request: JsonRequest) -> CallTrackingCallInfo:
        payload = self.transport.request_json(
            "POST",
            "/calltracking/v1/getCallById/",
            context=RequestContext("cpa.calltracking.get_call_by_id", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_call_tracking_call_item(payload)

    def get_calls(self, request: JsonRequest) -> CallTrackingCallsResult:
        payload = self.transport.request_json(
            "POST",
            "/calltracking/v1/getCalls/",
            context=RequestContext("cpa.calltracking.get_calls", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_call_tracking_calls(payload)

    def get_record_by_call_id(self, *, call_id: int | str) -> CallTrackingRecord:
        binary = self.transport.download_binary(
            "/calltracking/v1/getRecordByCallId/",
            context=RequestContext("cpa.calltracking.get_record_by_call_id"),
            params={"callId": call_id},
        )
        return CallTrackingRecord(binary)
