from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.cpa import CallTrackingCall, CallTrackingCallResponse


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


def test_calltracking_get_call_by_id_maps_call_and_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/calltracking/v1/getCallById/"
        assert json.loads(request.content.decode()) == {"callId": 7001}
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

    result = CallTrackingCall(
        make_transport(httpx.MockTransport(handler)),
        resource_id="7001",
    ).get()

    assert isinstance(result, CallTrackingCallResponse)
    assert result.call.call_id == "7001"
    assert result.call.item_id == "9901"
    assert result.error.code == 0
    assert result.to_dict() == {
        "call": {
            "call_id": "7001",
            "item_id": "9901",
            "buyer_phone": "+79990000100",
            "seller_phone": "+79990000101",
            "virtual_phone": "+79990000102",
            "call_time": "2026-04-18T09:00:00Z",
            "talk_duration": 67,
            "waiting_duration": 1.25,
        },
        "error": {"code": 0, "message": ""},
    }


def test_calltracking_get_call_by_id_preserves_error_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "call": {
                    "callId": 7002,
                    "itemId": 9902,
                    "buyerPhone": "+79990000200",
                    "sellerPhone": "+79990000201",
                    "virtualPhone": "+79990000202",
                    "callTime": "2026-04-18T10:00:00Z",
                    "talkDuration": 33,
                    "waitingDuration": 0.75,
                },
                "error": {"code": 409, "message": "call is archived"},
            },
        )

    result = CallTrackingCall(
        make_transport(httpx.MockTransport(handler)),
        resource_id="7002",
    ).get()

    assert result.error.code == 409
    assert result.error.message == "call is archived"
