"""Доменные объекты пакета cpa."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.deprecation import deprecated_method, warn_deprecated_once
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
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
from avito.cpa.operations import (
    CPA_HEADERS,
    CREATE_CPA_CALL_COMPLAINT,
    CREATE_CPA_LEAD_COMPLAINT,
    GET_CALLTRACKING_CALL_BY_ID,
    GET_CALLTRACKING_CALLS,
    GET_CALLTRACKING_RECORD,
    GET_CPA_ARCHIVE_BALANCE,
    GET_CPA_ARCHIVE_CALL_BY_ID,
    GET_CPA_ARCHIVE_RECORD,
    GET_CPA_BALANCE,
    GET_CPA_CHAT_BY_ACTION_ID,
    GET_CPA_PHONES_INFO,
    LIST_CPA_CALLS,
    LIST_CPA_CHATS,
    LIST_CPA_CHATS_CLASSIC,
)


@dataclass(slots=True, frozen=True)
class CpaLead(DomainObject):
    """Доменный объект CPA-лида и связанных lead-операций."""

    __swagger_domain__ = "cpa"
    __sdk_factory__ = "cpa_lead"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/cpa/v1/createComplaintByActionId",
        spec="CPAАвито.json",
        operation_id="createComplaintByActionId",
        method_args={"action_id": "body.action_id", "reason": "body.message"},
    )
    def create_complaint_by_action_id(
        self,
        *,
        action_id: str,
        reason: str,
    ) -> CpaActionResult:
        """Выполняет публичную операцию `CpaLead.create_complaint_by_action_id` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                CREATE_CPA_LEAD_COMPLAINT,
                request=CpaLeadComplaintRequest(action_id=action_id, reason=reason),
                headers=CPA_HEADERS,
            )

    @swagger_operation(
        "POST",
        "/cpa/v3/balanceInfo",
        spec="CPAАвито.json",
        operation_id="balanceInfoV3",
    )
    def get_balance_info(self) -> CpaBalanceInfo:
        """Выполняет публичную операцию `CpaLead.get_balance_info` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_CPA_BALANCE, request={}, headers=CPA_HEADERS)


@dataclass(slots=True, frozen=True)
class CpaChat(DomainObject):
    """Доменный объект CPA-чата."""

    __swagger_domain__ = "cpa"
    __sdk_factory__ = "cpa_chat"
    __sdk_factory_args__ = {"chat_id": "path.chat_id"}

    action_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/cpa/v1/chatByActionId/{actionId}",
        spec="CPAАвито.json",
        operation_id="chatByActionId",
    )
    def get(self, *, action_id: int | str | None = None) -> CpaChatInfo:
        """Выполняет публичную операцию `CpaChat.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                GET_CPA_CHAT_BY_ACTION_ID,
                path_params={"actionId": action_id or self._require_action_id()},
                headers=CPA_HEADERS,
            )

    @swagger_operation(
        "POST",
        "/cpa/v2/chatsByTime",
        spec="CPAАвито.json",
        operation_id="chatsByTime",
        method_args={"created_at_from": "body.date_time_from"},
    )
    def list(
        self,
        *,
        created_at_from: str,
        limit: int | None = None,
        version: int = 2,
    ) -> CpaChatsResult:
        """Выполняет публичную операцию `CpaChat.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        if version == 1:
            return self.list_classic(created_at_from=created_at_from, limit=limit)
        return self._execute(
                LIST_CPA_CHATS,
                request=CpaChatsByTimeRequest(
                    created_at_from=created_at_from,
                    limit=limit,
                ),
                headers=CPA_HEADERS,
            )

    @swagger_operation(
        "POST",
        "/cpa/v1/chatsByTime",
        spec="CPAАвито.json",
        operation_id="chatsByTime",
        method_args={"created_at_from": "body.date_time_from"},
    )
    def list_classic(
        self,
        *,
        created_at_from: str,
        limit: int | None = None,
    ) -> CpaChatsResult:
        """Выполняет legacy-операцию списка CPA-чатов v1 и возвращает типизированную SDK-модель.

        Метод оставлен для явного покрытия отдельной Swagger operation.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        warn_deprecated_once(
            symbol="CpaChat.list(version=1)",
            replacement="cpa_chat().list(version=2)",
            removal_version="1.3.0",
            deprecated_since="1.1.0",
        )
        return self._execute(
                LIST_CPA_CHATS_CLASSIC,
                request=CpaChatsByTimeRequest(
                    created_at_from=created_at_from,
                    limit=limit,
                ),
                headers=CPA_HEADERS,
            )

    @swagger_operation(
        "POST",
        "/cpa/v1/phonesInfoFromChats",
        spec="CPAАвито.json",
        operation_id="phonesInfoFromChats",
        method_args={"action_ids": "body.date_time_from"},
    )
    def get_phones_info_from_chats(
        self,
        *,
        action_ids: Sequence[str],
    ) -> CpaPhonesResult:
        """Выполняет публичную операцию `CpaChat.get_phones_info_from_chats` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                GET_CPA_PHONES_INFO,
                request=CpaPhonesFromChatsRequest(action_ids=list(action_ids)),
                headers=CPA_HEADERS,
            )

    def _require_action_id(self) -> str:
        if self.action_id is None:
            raise ValidationError("Для операции требуется `action_id`.")
        return str(self.action_id)


@dataclass(slots=True, frozen=True)
class CpaCall(DomainObject):
    """Доменный объект CPA-звонка."""

    __swagger_domain__ = "cpa"
    __sdk_factory__ = "cpa_call"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/cpa/v2/callsByTime",
        spec="CPAАвито.json",
        operation_id="getCallsByTimeV2",
        method_args={"date_time_from": "body.date_time_from", "date_time_to": "body.date_time_from"},
    )
    def list(self, *, date_time_from: str, date_time_to: str) -> CpaCallsResult:
        """Выполняет публичную операцию `CpaCall.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                LIST_CPA_CALLS,
                request=CpaCallsByTimeRequest(
                    date_time_from=date_time_from,
                    date_time_to=date_time_to,
                ),
                headers=CPA_HEADERS,
            )

    @swagger_operation(
        "POST",
        "/cpa/v1/createComplaint",
        spec="CPAАвито.json",
        operation_id="postCreateComplaint",
        method_args={"call_id": "body.call_id", "reason": "body.message"},
    )
    def create_complaint(self, *, call_id: int, reason: str) -> CpaActionResult:
        """Выполняет публичную операцию `CpaCall.create_complaint` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                CREATE_CPA_CALL_COMPLAINT,
                request=CpaCallComplaintRequest(call_id=call_id, reason=reason),
                headers=CPA_HEADERS,
            )


@dataclass(slots=True, frozen=True)
class CpaArchive(DomainObject):
    """Доменный объект архивных операций CPA."""

    __swagger_domain__ = "cpa"
    __sdk_factory__ = "cpa_archive"
    __sdk_factory_args__ = {"call_id": "path.call_id"}

    call_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/cpa/v1/call/{call_id}",
        spec="CPAАвито.json",
        operation_id="getCall",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="CpaArchive.get_call",
        replacement="call_tracking_call().download",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_call(self, *, call_id: int | str | None = None) -> CpaAudioRecord:
        """Получает архивную запись звонка.

                Deprecated: используйте `call_tracking_call().download`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return CpaAudioRecord(
            self._execute(
                    GET_CPA_ARCHIVE_RECORD,
                    path_params={"call_id": call_id or self._require_call_id()},
                    headers=CPA_HEADERS,
                )
        )

    @swagger_operation(
        "POST",
        "/cpa/v2/balanceInfo",
        spec="CPAАвито.json",
        operation_id="balanceInfoV2",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="CpaArchive.get_balance_info",
        replacement="cpa_lead().get_balance_info",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_balance_info(self) -> CpaBalanceInfo:
        """Получает архивный баланс CPA.

                Deprecated: используйте `cpa_lead().get_balance_info`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_CPA_ARCHIVE_BALANCE, request={}, headers=CPA_HEADERS)

    @swagger_operation(
        "POST",
        "/cpa/v2/callById",
        spec="CPAАвито.json",
        operation_id="getCallByIdV2",
        method_args={"call_id": "body.call_id"},
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="CpaArchive.get_call_by_id",
        replacement="call_tracking_call().get",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_call_by_id(self, *, call_id: int) -> CpaCallInfo:
        """Получает архивные данные звонка.

                Deprecated: используйте `call_tracking_call().get`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                GET_CPA_ARCHIVE_CALL_BY_ID,
                request=CpaCallByIdRequest(call_id=call_id),
                headers=CPA_HEADERS,
            )

    def _require_call_id(self) -> str:
        if self.call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.call_id)


@dataclass(slots=True, frozen=True)
class CallTrackingCall(DomainObject):
    """Доменный объект CallTracking."""

    __swagger_domain__ = "cpa"
    __sdk_factory__ = "call_tracking_call"
    __sdk_factory_args__ = {"call_id": "path.call_id"}

    call_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/calltracking/v1/getCallById",
        spec="CallTracking[КТ].json",
        operation_id="get_call_by_id",
    )
    def get(self, *, call_id: int | None = None) -> CallTrackingCallResponse:
        """Выполняет публичную операцию `CallTrackingCall.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_call_id = call_id or (int(self.call_id) if self.call_id is not None else None)
        if resolved_call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return self._execute(
                GET_CALLTRACKING_CALL_BY_ID,
                request=CallTrackingGetCallByIdRequest(call_id=resolved_call_id),
            )

    @swagger_operation(
        "POST",
        "/calltracking/v1/getCalls",
        spec="CallTracking[КТ].json",
        operation_id="get_calls",
        method_args={"date_time_from": "body.date_time_from", "date_time_to": "body.date_time_to"},
    )
    def list(
        self,
        *,
        date_time_from: str,
        date_time_to: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> CallTrackingCallsResult:
        """Выполняет публичную операцию `CallTrackingCall.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
                GET_CALLTRACKING_CALLS,
                request=CallTrackingCallsRequest(
                    date_time_from=date_time_from,
                    date_time_to=date_time_to,
                    limit=limit,
                    offset=offset,
                ),
            )

    @swagger_operation(
        "GET",
        "/calltracking/v1/getRecordByCallId",
        spec="CallTracking[КТ].json",
        operation_id="get_record_by_call_id",
        method_args={"call_id": "query.callId"},
    )
    def download(self, *, call_id: int | str | None = None) -> CallTrackingRecord:
        """Выполняет публичную операцию `CallTrackingCall.download` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return CallTrackingRecord(
            self._execute(
                    GET_CALLTRACKING_RECORD,
                    query={"callId": call_id or self._require_call_id()},
                )
        )

    def _require_call_id(self) -> str:
        if self.call_id is None:
            raise ValidationError("Для операции требуется `call_id`.")
        return str(self.call_id)


__all__ = ("CallTrackingCall", "CpaArchive", "CpaCall", "CpaChat", "CpaLead")
