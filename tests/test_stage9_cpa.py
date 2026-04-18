from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.cpa import CallTrackingCall, CpaCall, CpaChat, CpaLead, CpaLegacy


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(),
        retry_policy=RetryPolicy(),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )


def test_cpa_chat_and_phone_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/cpa/v1/chatByActionId/act-1":
            return httpx.Response(
                200,
                json={
                    "chat": {
                        "chat": {
                            "id": "chat-1",
                            "actionId": "act-1",
                            "createdAt": "2026-04-18T10:00:00+03:00",
                            "updatedAt": "2026-04-18T10:05:00+03:00",
                        },
                        "buyer": {"userId": 501, "name": "Иван"},
                        "item": {"id": 9001, "title": "Велосипед"},
                        "isArbitrageAvailable": True,
                    }
                },
            )
        if path == "/cpa/v1/chatsByTime":
            assert payload == {"createdAtFrom": "2026-04-18T00:00:00+03:00"}
            return httpx.Response(
                200,
                json={
                    "chats": [
                        {
                            "chat": {"id": "chat-v1", "actionId": "legacy-1"},
                            "buyer": {"userId": 502, "name": "Петр"},
                            "item": {"id": 9002, "title": "Самокат"},
                            "isArbitrageAvailable": False,
                        }
                    ]
                },
            )
        if path == "/cpa/v2/chatsByTime":
            assert payload == {"createdAtFrom": "2026-04-18T00:00:00+03:00", "limit": 10}
            return httpx.Response(
                200,
                json={
                    "chats": [
                        {
                            "chat": {"id": "chat-v2", "actionId": "act-2"},
                            "buyer": {"userId": 503, "name": "Мария"},
                            "item": {"id": 9003, "title": "Ноутбук"},
                            "isArbitrageAvailable": True,
                        }
                    ]
                },
            )
        assert path == "/cpa/v1/phonesInfoFromChats"
        assert payload == {"actionIds": ["act-1", "act-2"]}
        return httpx.Response(
            200,
            json={
                "total": 2,
                "results": [
                    {
                        "id": 101,
                        "date": "2026-04-18T12:00:00+03:00",
                        "phone_number": "+79990000001",
                        "pricePenny": 1500,
                        "group": "Транспорт",
                        "url": "https://example.com/preview-1.jpg",
                    },
                    {
                        "id": 102,
                        "date": "2026-04-18T12:05:00+03:00",
                        "phone_number": "+79990000002",
                        "pricePenny": 1700,
                        "group": "Электроника",
                        "url": "https://example.com/preview-2.jpg",
                    },
                ],
            },
        )

    chat = CpaChat(make_transport(httpx.MockTransport(handler)), resource_id="act-1")

    item = chat.get()
    chats_v1 = chat.list(payload={"createdAtFrom": "2026-04-18T00:00:00+03:00"}, version=1)
    chats_v2 = chat.list(payload={"createdAtFrom": "2026-04-18T00:00:00+03:00", "limit": 10})
    phones = chat.get_phones_info_from_chats(payload={"actionIds": ["act-1", "act-2"]})

    assert item.chat_id == "chat-1"
    assert item.item_title == "Велосипед"
    assert chats_v1.items[0].buyer_name == "Петр"
    assert chats_v2.items[0].is_arbitrage_available is True
    assert phones.total == 2
    assert phones.items[1].phone_number == "+79990000002"


def test_cpa_calls_balance_and_legacy_flows() -> None:
    audio_bytes = b"ID3 fake audio"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/cpa/v2/callsByTime":
            assert payload == {"dateTimeFrom": "2026-04-18T00:00:00+03:00", "dateTimeTo": "2026-04-18T23:59:59+03:00"}
            return httpx.Response(
                200,
                json={
                    "calls": [
                        {
                            "id": 2001,
                            "itemId": 3001,
                            "buyerPhone": "+79990000010",
                            "sellerPhone": "+79990000011",
                            "virtualPhone": "+79990000012",
                            "statusId": 2,
                            "price": 171600,
                            "duration": 119,
                            "waitingDuration": 0.5,
                            "createTime": "2026-04-18T11:00:00+03:00",
                            "startTime": "2026-04-18T10:59:30+03:00",
                            "groupTitle": "Автомобили",
                            "recordUrl": "https://example.com/record-2001.mp3",
                            "isArbitrageAvailable": True,
                        }
                    ]
                },
            )
        if path == "/cpa/v1/createComplaint":
            assert payload == {"callId": 2001, "reason": "spam"}
            return httpx.Response(200, json={"success": True})
        if path == "/cpa/v1/createComplaintByActionId":
            assert payload == {"actionId": "act-1", "reason": "duplicate"}
            return httpx.Response(200, json={"success": True})
        if path == "/cpa/v3/balanceInfo":
            assert payload == {}
            return httpx.Response(200, json={"balance": -5000})
        if path == "/cpa/v2/balanceInfo":
            assert payload == {}
            return httpx.Response(200, json={"balance": -5000, "advance": 1000, "debt": 0})
        if path == "/cpa/v2/callById":
            assert payload == {"callId": 2001}
            return httpx.Response(
                200,
                json={
                    "calls": {
                        "id": 2001,
                        "itemId": 3001,
                        "buyerPhone": "+79990000010",
                        "sellerPhone": "+79990000011",
                        "virtualPhone": "+79990000012",
                        "statusId": 2,
                        "price": 171600,
                        "duration": 119,
                        "waitingDuration": 0.5,
                        "createTime": "2026-04-18T11:00:00+03:00",
                    }
                },
            )
        assert path == "/cpa/v1/call/2001"
        return httpx.Response(
            200,
            content=audio_bytes,
            headers={
                "content-type": "audio/mpeg",
                "content-disposition": 'attachment; filename="call-2001.mp3"',
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    cpa_call = CpaCall(transport, resource_id="2001")
    cpa_lead = CpaLead(transport, resource_id="act-1")
    legacy = CpaLegacy(transport, resource_id="2001")

    calls = cpa_call.list(payload={"dateTimeFrom": "2026-04-18T00:00:00+03:00", "dateTimeTo": "2026-04-18T23:59:59+03:00"})
    complaint = cpa_call.create_create_complaint(payload={"callId": 2001, "reason": "spam"})
    complaint_by_action = cpa_lead.create_complaint_by_action_id(payload={"actionId": "act-1", "reason": "duplicate"})
    balance_v3 = cpa_lead.create_balance_info_v3()
    balance_v2 = legacy.legacy_create_balance_info_v2()
    call_v2 = legacy.legacy_create_call_by_id_v2(payload={"callId": 2001})
    record = legacy.legacy_get_call()

    assert calls.items[0].record_url == "https://example.com/record-2001.mp3"
    assert complaint.success is True
    assert complaint_by_action.success is True
    assert balance_v3.balance == -5000
    assert balance_v2.advance == 1000
    assert call_v2.call_id == "2001"
    assert record.filename == "call-2001.mp3"
    assert record.binary.content == audio_bytes


def test_calltracking_flows() -> None:
    audio_bytes = b"RIFF fake wave"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/calltracking/v1/getCallById/":
            assert json.loads(request.content.decode()) == {"callId": "7001"}
            return httpx.Response(
                200,
                json={
                    "call": {
                        "callId": 7001,
                        "itemId": 9901,
                        "buyerPhone": "+79990000100",
                        "sellerPhone": "+79990000101",
                        "virtualPhone": "+79990000102",
                        "callTime": "2026-04-18T09:00:00Z",
                        "talkDuration": 67,
                        "waitingDuration": 1.25,
                    },
                    "error": {"code": 0, "message": ""},
                },
            )
        if path == "/calltracking/v1/getCalls/":
            assert json.loads(request.content.decode()) == {
                "dateTimeFrom": "2026-04-01T00:00:00Z",
                "dateTimeTo": "2026-04-18T23:59:59Z",
                "limit": 100,
                "offset": 0,
            }
            return httpx.Response(
                200,
                json={
                    "calls": [
                        {
                            "callId": 7001,
                            "itemId": 9901,
                            "buyerPhone": "+79990000100",
                            "sellerPhone": "+79990000101",
                            "virtualPhone": "+79990000102",
                            "callTime": "2026-04-18T09:00:00Z",
                            "talkDuration": 67,
                            "waitingDuration": 1.25,
                        }
                    ],
                    "error": {"code": 0, "message": ""},
                },
            )
        assert path == "/calltracking/v1/getRecordByCallId/"
        assert request.url.params["callId"] == "7001"
        return httpx.Response(
            200,
            content=audio_bytes,
            headers={
                "content-type": "audio/wav",
                "content-disposition": 'attachment; filename="record-7001.wav"',
            },
        )

    call = CallTrackingCall(make_transport(httpx.MockTransport(handler)), resource_id="7001")

    item = call.get()
    items = call.list(
        payload={
            "dateTimeFrom": "2026-04-01T00:00:00Z",
            "dateTimeTo": "2026-04-18T23:59:59Z",
            "limit": 100,
            "offset": 0,
        }
    )
    record = call.download()

    assert item.call_id == "7001"
    assert item.talk_duration == 67
    assert items.items[0].buyer_phone == "+79990000100"
    assert record.filename == "record-7001.wav"
    assert record.binary.content == audio_bytes
