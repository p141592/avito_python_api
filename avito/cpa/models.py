"""Типизированные модели раздела cpa."""

from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from typing import Any

from avito.core import BinaryResponse
from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class CpaChatsByTimeRequest:
    """Запрос списка CPA-чатов по времени."""

    created_at_from: str
    limit: int | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"createdAtFrom": self.created_at_from}
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(slots=True, frozen=True)
class CpaPhonesFromChatsRequest:
    """Запрос телефонов из целевых чатов."""

    action_ids: list[str]

    def to_payload(self) -> dict[str, object]:
        return {"actionIds": list(self.action_ids)}


@dataclass(slots=True, frozen=True)
class CpaCallsByTimeRequest:
    """Запрос списка CPA-звонков по времени."""

    date_time_from: str
    date_time_to: str

    def to_payload(self) -> dict[str, object]:
        return {
            "dateTimeFrom": self.date_time_from,
            "dateTimeTo": self.date_time_to,
        }


@dataclass(slots=True, frozen=True)
class CpaCallComplaintRequest:
    """Запрос жалобы на CPA-звонок."""

    call_id: int
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {"callId": self.call_id, "reason": self.reason}


@dataclass(slots=True, frozen=True)
class CpaLeadComplaintRequest:
    """Запрос жалобы по action id."""

    action_id: str
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {"actionId": self.action_id, "reason": self.reason}


@dataclass(slots=True, frozen=True)
class CpaCallByIdRequest:
    """Запрос получения CPA-звонка по идентификатору."""

    call_id: int

    def to_payload(self) -> dict[str, int]:
        return {"callId": self.call_id}


@dataclass(slots=True, frozen=True)
class CallTrackingCallsRequest:
    """Запрос списка звонков CallTracking."""

    date_time_from: str
    date_time_to: str
    limit: int | None = None
    offset: int | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "dateTimeFrom": self.date_time_from,
            "dateTimeTo": self.date_time_to,
        }
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.offset is not None:
            payload["offset"] = self.offset
        return payload


@dataclass(slots=True, frozen=True)
class CpaErrorInfo(SerializableModel):
    """Информация об ошибке CPA API."""

    code: int | None
    message: str | None


@dataclass(slots=True, frozen=True)
class CpaActionResult(SerializableModel):
    """Результат mutation-операции CPA."""

    success: bool
    error: CpaErrorInfo | None = None


@dataclass(slots=True, frozen=True)
class CpaBalanceInfo(SerializableModel):
    """Информация о CPA-балансе пользователя."""

    balance: int | None
    advance: int | None = None
    debt: int | None = None
    error: CpaErrorInfo | None = None


@dataclass(slots=True, frozen=True)
class CpaCallInfo(SerializableModel):
    """Информация о звонке CPA."""

    call_id: str | None
    item_id: str | None
    buyer_phone: str | None
    seller_phone: str | None
    virtual_phone: str | None
    status_id: int | None
    price: int | None
    duration: int | None
    waiting_duration: float | None
    created_at: str | None
    started_at: str | None
    group_title: str | None
    record_url: str | None
    is_arbitrage_available: bool | None


@dataclass(slots=True, frozen=True)
class CpaCallsResult(SerializableModel):
    """Список звонков CPA."""

    items: list[CpaCallInfo]
    error: CpaErrorInfo | None = None


@dataclass(slots=True, frozen=True)
class CpaChatInfo(SerializableModel):
    """Информация о CPA-чате."""

    chat_id: str | None
    action_id: str | None
    item_id: str | None
    item_title: str | None
    buyer_user_id: str | None
    buyer_name: str | None
    created_at: str | None
    updated_at: str | None
    is_arbitrage_available: bool | None


@dataclass(slots=True, frozen=True)
class CpaChatsResult(SerializableModel):
    """Список чатов CPA."""

    items: list[CpaChatInfo]


@dataclass(slots=True, frozen=True)
class CpaPhoneInfo(SerializableModel):
    """Информация по телефону, найденному в целевом чате."""

    action_id: str | None
    phone_number: str | None
    created_at: str | None
    price: int | None
    group: str | None
    preview_url: str | None


@dataclass(slots=True, frozen=True)
class CpaPhonesResult(SerializableModel):
    """Список телефонных номеров из целевых чатов."""

    items: list[CpaPhoneInfo]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class CpaAudioRecord:
    """Бинарная запись звонка CPA."""

    binary: BinaryResponse

    @property
    def filename(self) -> str | None:
        """Имя файла записи звонка."""

        return self.binary.filename

    def to_dict(self) -> dict[str, Any]:
        """Сериализует бинарную запись без transport-объекта."""

        return {
            "filename": self.binary.filename,
            "content_type": self.binary.content_type,
            "content_base64": b64encode(self.binary.content).decode("ascii"),
        }

    def model_dump(self) -> dict[str, Any]:
        return self.to_dict()


@dataclass(slots=True, frozen=True)
class CallTrackingCallInfo(SerializableModel):
    """Информация о звонке CallTracking."""

    call_id: str | None
    item_id: str | None
    buyer_phone: str | None
    seller_phone: str | None
    virtual_phone: str | None
    call_time: str | None
    talk_duration: int | None
    waiting_duration: float | None


@dataclass(slots=True, frozen=True)
class CallTrackingCallsResult(SerializableModel):
    """Список звонков CallTracking."""

    items: list[CallTrackingCallInfo]
    error: CpaErrorInfo | None = None


@dataclass(slots=True, frozen=True)
class CallTrackingGetCallByIdRequest:
    """Запрос получения звонка CallTracking по идентификатору."""

    call_id: int

    def to_payload(self) -> dict[str, int]:
        """Сериализует запрос звонка CallTracking."""

        return {"callId": self.call_id}


@dataclass(slots=True, frozen=True)
class CallTrackingCallResponse(SerializableModel):
    """Ответ CallTracking get_call_by_id с объектом звонка и ошибкой."""

    call: CallTrackingCallInfo
    error: CpaErrorInfo


@dataclass(slots=True, frozen=True)
class CallTrackingRecord:
    """Бинарная запись звонка CallTracking."""

    binary: BinaryResponse

    @property
    def filename(self) -> str | None:
        """Имя файла записи звонка."""

        return self.binary.filename

    def to_dict(self) -> dict[str, Any]:
        """Сериализует бинарную запись без transport-объекта."""

        return {
            "filename": self.binary.filename,
            "content_type": self.binary.content_type,
            "content_base64": b64encode(self.binary.content).decode("ascii"),
        }

    def model_dump(self) -> dict[str, Any]:
        return self.to_dict()


