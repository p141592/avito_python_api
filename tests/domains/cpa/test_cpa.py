from __future__ import annotations

import json

import httpx

from avito.cpa import CallTrackingCall, CpaArchive, CpaCall, CpaChat, CpaLead
from avito.cpa.models import (
    CallTrackingCallsRequest,
    CpaCallByIdRequest,
    CpaCallComplaintRequest,
    CpaCallsByTimeRequest,
    CpaChatsByTimeRequest,
    CpaLeadComplaintRequest,
    CpaPhonesFromChatsRequest,
)
from tests.helpers.transport import make_transport


def test_cpa_chat_and_phone_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/cpa/v1/chatByActionId/act-1":
            return httpx.Response(200, json={"chat": {"chat": {"id": "chat-1", "actionId": "act-1"}, "buyer": {"userId": 501, "name": "Иван"}, "item": {"id": 9001, "title": "Велосипед"}, "isArbitrageAvailable": True}})
        if path == "/cpa/v1/chatsByTime":
            assert payload == {"createdAtFrom": "2026-04-18T00:00:00+03:00"}
            return httpx.Response(200, json={"chats": [{"chat": {"id": "chat-v1", "actionId": "legacy-1"}, "buyer": {"userId": 502, "name": "Петр"}, "item": {"id": 9002, "title": "Самокат"}, "isArbitrageAvailable": False}]})
        if path == "/cpa/v2/chatsByTime":
            return httpx.Response(200, json={"chats": [{"chat": {"id": "chat-v2", "actionId": "act-2"}, "buyer": {"userId": 503, "name": "Мария"}, "item": {"id": 9003, "title": "Ноутбук"}, "isArbitrageAvailable": True}]})
        return httpx.Response(200, json={"total": 2, "results": [{"id": 101, "date": "2026-04-18T12:00:00+03:00", "phone_number": "+79990000001"}, {"id": 102, "date": "2026-04-18T12:05:00+03:00", "phone_number": "+79990000002"}]})

    chat = CpaChat(make_transport(httpx.MockTransport(handler)), action_id="act-1")
    assert chat.get().item_title == "Велосипед"
    assert chat.list(request=CpaChatsByTimeRequest(created_at_from="2026-04-18T00:00:00+03:00"), version=1).items[0].buyer_name == "Петр"
    assert chat.list(request=CpaChatsByTimeRequest(created_at_from="2026-04-18T00:00:00+03:00", limit=10)).items[0].is_arbitrage_available is True
    assert chat.get_phones_info_from_chats(request=CpaPhonesFromChatsRequest(action_ids=["act-1", "act-2"])).items[1].phone_number == "+79990000002"


def test_cpa_calls_archive_and_balance_flows() -> None:
    audio_bytes = b"ID3 fake audio"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/cpa/v2/callsByTime":
            return httpx.Response(200, json={"calls": [{"id": 2001, "itemId": 3001, "buyerPhone": "+79990000010", "sellerPhone": "+79990000011", "virtualPhone": "+79990000012", "statusId": 2, "price": 171600, "duration": 119, "waitingDuration": 0.5, "createTime": "2026-04-18T11:00:00+03:00", "recordUrl": "https://example.com/record-2001.mp3"}]})
        if path == "/cpa/v1/createComplaint":
            return httpx.Response(200, json={"success": True})
        if path == "/cpa/v1/createComplaintByActionId":
            return httpx.Response(200, json={"success": True})
        if path == "/cpa/v3/balanceInfo":
            return httpx.Response(200, json={"balance": -5000})
        if path == "/cpa/v2/balanceInfo":
            return httpx.Response(200, json={"balance": -5000, "advance": 1000, "debt": 0})
        if path == "/cpa/v2/callById":
            return httpx.Response(200, json={"calls": {"id": 2001, "itemId": 3001, "buyerPhone": "+79990000010", "sellerPhone": "+79990000011", "virtualPhone": "+79990000012", "statusId": 2, "price": 171600, "duration": 119, "waitingDuration": 0.5, "createTime": "2026-04-18T11:00:00+03:00"}})
        return httpx.Response(200, content=audio_bytes, headers={"content-type": "audio/mpeg", "content-disposition": 'attachment; filename="call-2001.mp3"'})

    transport = make_transport(httpx.MockTransport(handler))
    cpa_call = CpaCall(transport)
    cpa_lead = CpaLead(transport)
    archive = CpaArchive(transport, call_id="2001")

    assert cpa_call.list(request=CpaCallsByTimeRequest(date_time_from="2026-04-18T00:00:00+03:00", date_time_to="2026-04-18T23:59:59+03:00")).items[0].record_url == "https://example.com/record-2001.mp3"
    assert cpa_call.create_complaint(request=CpaCallComplaintRequest(call_id=2001, reason="spam")).success is True
    assert cpa_lead.create_complaint_by_action_id(request=CpaLeadComplaintRequest(action_id="act-1", reason="duplicate")).success is True
    assert cpa_lead.get_balance_info().balance == -5000
    assert archive.get_balance_info().advance == 1000
    assert archive.get_call_by_id(request=CpaCallByIdRequest(call_id=2001)).call_id == "2001"
    assert archive.get_call().binary.content == audio_bytes


def test_calltracking_flows() -> None:
    audio_bytes = b"RIFF fake wave"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/calltracking/v1/getCallById/":
            return httpx.Response(200, json={"call": {"callId": 7001, "itemId": 9901, "buyerPhone": "+79990000100", "sellerPhone": "+79990000101", "virtualPhone": "+79990000102", "callTime": "2026-04-18T09:00:00Z", "talkDuration": 67, "waitingDuration": 1.25}, "error": {"code": 0, "message": ""}})
        if request.url.path == "/calltracking/v1/getCalls/":
            return httpx.Response(200, json={"calls": [{"callId": 7001, "itemId": 9901, "buyerPhone": "+79990000100", "sellerPhone": "+79990000101", "virtualPhone": "+79990000102", "callTime": "2026-04-18T09:00:00Z", "talkDuration": 67, "waitingDuration": 1.25}], "error": {"code": 0, "message": ""}})
        return httpx.Response(200, content=audio_bytes, headers={"content-type": "audio/wav", "content-disposition": 'attachment; filename="record-7001.wav"'})

    call = CallTrackingCall(make_transport(httpx.MockTransport(handler)), call_id="7001")
    assert call.get().call.call_id == "7001"
    assert call.list(request=CallTrackingCallsRequest(date_time_from="2026-04-01T00:00:00Z", date_time_to="2026-04-18T23:59:59Z", limit=100, offset=0)).items[0].buyer_phone == "+79990000100"
    assert call.download().binary.content == audio_bytes
