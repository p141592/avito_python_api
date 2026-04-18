"""Типизированные модели раздела cpa."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core import BinaryResponse


@dataclass(slots=True, frozen=True)
class JsonRequest:
    """Типизированная обертка над JSON payload запроса."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class CpaErrorInfo:
    """Информация об ошибке CPA API."""

    code: int | None
    message: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaActionResult:
    """Результат mutation-операции CPA."""

    success: bool
    error: CpaErrorInfo | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaBalanceInfo:
    """Информация о CPA-балансе пользователя."""

    balance: int | None
    advance: int | None = None
    debt: int | None = None
    error: CpaErrorInfo | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaCallInfo:
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
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaCallsResult:
    """Список звонков CPA."""

    items: list[CpaCallInfo]
    error: CpaErrorInfo | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaChatInfo:
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
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaChatsResult:
    """Список чатов CPA."""

    items: list[CpaChatInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaPhoneInfo:
    """Информация по телефону, найденному в целевом чате."""

    action_id: str | None
    phone_number: str | None
    created_at: str | None
    price: int | None
    group: str | None
    preview_url: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaPhonesResult:
    """Список телефонных номеров из целевых чатов."""

    items: list[CpaPhoneInfo]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaAudioRecord:
    """Бинарная запись звонка CPA."""

    binary: BinaryResponse

    @property
    def filename(self) -> str | None:
        """Имя файла записи звонка."""

        return self.binary.filename


@dataclass(slots=True, frozen=True)
class CallTrackingCallInfo:
    """Информация о звонке CallTracking."""

    call_id: str | None
    item_id: str | None
    buyer_phone: str | None
    seller_phone: str | None
    virtual_phone: str | None
    call_time: str | None
    talk_duration: int | None
    waiting_duration: float | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CallTrackingCallsResult:
    """Список звонков CallTracking."""

    items: list[CallTrackingCallInfo]
    error: CpaErrorInfo | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CallTrackingRecord:
    """Бинарная запись звонка CallTracking."""

    binary: BinaryResponse

    @property
    def filename(self) -> str | None:
        """Имя файла записи звонка."""

        return self.binary.filename
