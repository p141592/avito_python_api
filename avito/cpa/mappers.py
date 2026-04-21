"""Мапперы JSON -> dataclass для пакета cpa."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.cpa.models import (
    CallTrackingCallInfo,
    CallTrackingCallResponse,
    CallTrackingCallsResult,
    CpaActionResult,
    CpaBalanceInfo,
    CpaCallInfo,
    CpaCallsResult,
    CpaChatInfo,
    CpaChatsResult,
    CpaErrorInfo,
    CpaPhoneInfo,
    CpaPhonesResult,
)

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_cpa_error(payload: object | None) -> CpaErrorInfo | None:
    """Преобразует payload ошибки CPA API."""

    if payload is None:
        return None
    data = _expect_mapping(payload)
    if not data:
        return None
    return CpaErrorInfo(
        code=_int(data, "code"),
        message=_str(data, "message", "error"),
    )


def map_cpa_action(payload: object) -> CpaActionResult:
    """Преобразует результат mutation-операции CPA."""

    data = _expect_mapping(payload)
    return CpaActionResult(
        success=bool(data.get("success", False)),
        error=map_cpa_error(data.get("error")),
    )


def map_balance(payload: object) -> CpaBalanceInfo:
    """Преобразует ответ баланса CPA."""

    data = _expect_mapping(payload)
    return CpaBalanceInfo(
        balance=_int(data, "balance"),
        advance=_int(data, "advance"),
        debt=_int(data, "debt"),
        error=map_cpa_error(data.get("error")),
    )


def _map_cpa_call(item: Payload) -> CpaCallInfo:
    return CpaCallInfo(
        call_id=_str(item, "id", "callId"),
        item_id=_str(item, "itemId", "item_id"),
        buyer_phone=_str(item, "buyerPhone"),
        seller_phone=_str(item, "sellerPhone"),
        virtual_phone=_str(item, "virtualPhone"),
        status_id=_int(item, "statusId"),
        price=_int(item, "price"),
        duration=_int(item, "duration", "talkDuration"),
        waiting_duration=_float(item, "waitingDuration"),
        created_at=_str(item, "createTime", "createdAt", "callTime"),
        started_at=_str(item, "startTime"),
        group_title=_str(item, "groupTitle"),
        record_url=_str(item, "recordUrl"),
        is_arbitrage_available=_bool(item, "isArbitrageAvailable"),
    )


def map_call_item(payload: object) -> CpaCallInfo:
    """Преобразует один звонок CPA."""

    data = _expect_mapping(payload)
    call = _mapping(data, "calls", "call")
    source = call or data
    return _map_cpa_call(source)


def map_calls(payload: object) -> CpaCallsResult:
    """Преобразует список звонков CPA."""

    data = _expect_mapping(payload)
    return CpaCallsResult(
        items=[_map_cpa_call(item) for item in _list(data, "calls", "items", "results")],
        error=map_cpa_error(data.get("error")),
    )


def _map_cpa_chat(item: Payload) -> CpaChatInfo:
    chat = _mapping(item, "chat")
    buyer = _mapping(item, "buyer")
    listing = _mapping(item, "item")
    source = chat or item
    return CpaChatInfo(
        chat_id=_str(source, "id", "chatId"),
        action_id=_str(source, "actionId", "action_id"),
        item_id=_str(listing, "id", "itemId"),
        item_title=_str(listing, "title", "subject"),
        buyer_user_id=_str(buyer, "userId", "id"),
        buyer_name=_str(buyer, "name"),
        created_at=_str(source, "createdAt", "created_at"),
        updated_at=_str(source, "updatedAt", "updated_at"),
        is_arbitrage_available=_bool(item, "isArbitrageAvailable"),
    )


def map_chat_item(payload: object) -> CpaChatInfo:
    """Преобразует один чат CPA."""

    data = _expect_mapping(payload)
    chat = _mapping(data, "chat")
    if chat:
        return _map_cpa_chat(chat)
    return _map_cpa_chat(data)


def map_chats(payload: object) -> CpaChatsResult:
    """Преобразует список чатов CPA."""

    data = _expect_mapping(payload)
    return CpaChatsResult(
        items=[_map_cpa_chat(item) for item in _list(data, "chats", "items", "results")],
    )


def map_phones(payload: object) -> CpaPhonesResult:
    """Преобразует список телефонов из целевых чатов."""

    data = _expect_mapping(payload)
    return CpaPhonesResult(
        items=[
            CpaPhoneInfo(
                action_id=_str(item, "id", "actionId"),
                phone_number=_str(item, "phone_number", "phoneNumber"),
                created_at=_str(item, "date", "createdAt"),
                price=_int(item, "pricePenny", "price"),
                group=_str(item, "group"),
                preview_url=_str(item, "url", "previewUrl"),
            )
            for item in _list(data, "results", "items")
        ],
        total=_int(data, "total"),
    )


def _map_call_tracking_call(item: Payload) -> CallTrackingCallInfo:
    return CallTrackingCallInfo(
        call_id=_str(item, "callId", "id"),
        item_id=_str(item, "itemId"),
        buyer_phone=_str(item, "buyerPhone"),
        seller_phone=_str(item, "sellerPhone"),
        virtual_phone=_str(item, "virtualPhone"),
        call_time=_str(item, "callTime", "createTime"),
        talk_duration=_int(item, "talkDuration", "duration"),
        waiting_duration=_float(item, "waitingDuration"),
    )


def map_call_tracking_call_item(payload: object) -> CallTrackingCallResponse:
    """Преобразует один звонок CallTracking."""

    data = _expect_mapping(payload)
    call = _mapping(data, "call")
    error = map_cpa_error(data.get("error"))
    if not call or error is None:
        raise ResponseMappingError(
            "Ответ CallTracking getCallById должен содержать `call` и `error`.",
            payload=payload,
        )
    return CallTrackingCallResponse(call=_map_call_tracking_call(call), error=error)


def map_call_tracking_calls(payload: object) -> CallTrackingCallsResult:
    """Преобразует список звонков CallTracking."""

    data = _expect_mapping(payload)
    return CallTrackingCallsResult(
        items=[_map_call_tracking_call(item) for item in _list(data, "calls", "items", "results")],
        error=map_cpa_error(data.get("error")),
    )
