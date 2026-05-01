"""Доменные объекты пакета jobs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ApiTimeouts, RetryOverride, ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.jobs.models import (
    ApplicationActionRequest,
    ApplicationIdsQuery,
    ApplicationIdsRequest,
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    ApplicationViewedItem,
    ApplicationViewedRequest,
    ApplicationViewedRequestItem,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryValuesResult,
    JobWebhookInfo,
    JobWebhooksResult,
    JobWebhookUpdateRequest,
    ResumeContactInfo,
    ResumeInfo,
    ResumeSearchQuery,
    ResumesResult,
    VacanciesQuery,
    VacanciesResult,
    VacancyArchiveRequest,
    VacancyAutoRenewalRequest,
    VacancyCreateRequest,
    VacancyIdsRequest,
    VacancyInfo,
    VacancyProlongateRequest,
    VacancyStatusesResult,
    VacancyUpdateRequest,
)
from avito.jobs.operations import (
    APPLY_APPLICATION_ACTIONS,
    ARCHIVE_VACANCY,
    CREATE_VACANCY,
    CREATE_VACANCY_CLASSIC,
    DELETE_JOB_WEBHOOK,
    GET_APPLICATION_IDS,
    GET_APPLICATION_STATES,
    GET_APPLICATIONS_BY_IDS,
    GET_JOB_DICTIONARY,
    GET_JOB_WEBHOOK,
    GET_RESUME,
    GET_RESUME_CONTACTS,
    GET_VACANCIES_BY_IDS,
    GET_VACANCY,
    GET_VACANCY_STATUSES,
    LIST_JOB_DICTIONARIES,
    LIST_JOB_WEBHOOKS,
    LIST_VACANCIES,
    PROLONGATE_VACANCY,
    SEARCH_RESUMES,
    SET_APPLICATIONS_IS_VIEWED,
    UPDATE_JOB_WEBHOOK,
    UPDATE_VACANCY,
    UPDATE_VACANCY_AUTO_RENEWAL,
    UPDATE_VACANCY_CLASSIC,
)


@dataclass(slots=True, frozen=True)
class Vacancy(DomainObject):
    """Доменный объект вакансий."""

    __swagger_domain__ = "jobs"
    __sdk_factory__ = "vacancy"
    __sdk_factory_args__ = {"vacancy_id": "path.vacancy_id"}

    vacancy_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/job/v2/vacancies",
        spec="АвитоРабота.json",
        operation_id="vacancyCreateV2",
        method_args={"title": "body.title"},
    )
    def create(
        self,
        *,
        title: str,
        version: int = 2,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Создает вакансию.

        Аргументы:
            title: передает название вакансии.
            version: задает версию upstream-контракта, если операция ее поддерживает.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        if version == 1:
            return self.create_classic(title=title, idempotency_key=idempotency_key)
        return self._execute(
            CREATE_VACANCY,
            request=VacancyCreateRequest(title=title),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v1/vacancies",
        spec="АвитоРабота.json",
        operation_id="vacancyCreate",
        method_args={"title": "body.name"},
    )
    def create_classic(
        self,
        *,
        title: str,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Создаёт вакансию через legacy v1 operation и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_VACANCY_CLASSIC,
            request=VacancyCreateRequest(title=title),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/update/{vacancy_uuid}",
        spec="АвитоРабота.json",
        operation_id="vacancyUpdateV2",
        method_args={"title": "body.title"},
    )
    def update(
        self,
        *,
        title: str,
        vacancy_id: int | str | None = None,
        vacancy_uuid: str | None = None,
        version: int = 2,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Обновляет вакансию.

        Аргументы:
            title: передает название вакансии.
            vacancy_id: идентифицирует вакансию.
            vacancy_uuid: идентифицирует вакансию по UUID.
            version: задает версию upstream-контракта, если операция ее поддерживает.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        if version == 1:
            return self.update_classic(
                vacancy_id=vacancy_id or self._require_vacancy_id(),
                title=title,
                idempotency_key=idempotency_key,
            )
        return self._execute(
            UPDATE_VACANCY,
            path_params={"vacancy_uuid": vacancy_uuid or self._require_vacancy_id()},
            request=VacancyUpdateRequest(title=title),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "PUT",
        "/job/v1/vacancies/{vacancy_id}",
        spec="АвитоРабота.json",
        operation_id="vacancyUpdate",
        method_args={"title": "body.name"},
    )
    def update_classic(
        self,
        *,
        title: str,
        vacancy_id: int | str | None = None,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Обновляет вакансию через legacy v1 operation и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            UPDATE_VACANCY_CLASSIC,
            path_params={"vacancy_id": vacancy_id or self._require_vacancy_id()},
            request=VacancyUpdateRequest(title=title),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "PUT",
        "/job/v1/vacancies/archived/{vacancy_id}",
        spec="АвитоРабота.json",
        operation_id="vacancyArchive",
        method_args={"employee_id": "body.employee_id"},
    )
    def delete(
        self,
        *,
        employee_id: int,
        vacancy_id: int | str | None = None,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Удаляет вакансию.

        Аргументы:
            employee_id: идентифицирует сотрудника аккаунта.
            vacancy_id: идентифицирует вакансию.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            ARCHIVE_VACANCY,
            path_params={"vacancy_id": vacancy_id or self._require_vacancy_id()},
            request=VacancyArchiveRequest(employee_id=employee_id),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v1/vacancies/{vacancy_id}/prolongate",
        spec="АвитоРабота.json",
        operation_id="vacancyProlongate",
        method_args={"billing_type": "body.billing_type"},
    )
    def prolongate(
        self,
        *,
        billing_type: str,
        vacancy_id: int | str | None = None,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Продлевает вакансий.

        Аргументы:
            billing_type: задает тип биллинга для продления вакансии.
            vacancy_id: идентифицирует вакансию.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            PROLONGATE_VACANCY,
            path_params={"vacancy_id": vacancy_id or self._require_vacancy_id()},
            request=VacancyProlongateRequest(billing_type=billing_type),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v2/vacancies",
        spec="АвитоРабота.json",
        operation_id="searchVacancy",
    )
    def list(
        self,
        *,
        query: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> VacanciesResult:
        """Возвращает список вакансий.

        Аргументы:
            query: передает поисковую строку или фильтр upstream API.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `VacanciesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            LIST_VACANCIES,
            query=VacanciesQuery(query=query),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v2/vacancies/{vacancy_id}",
        spec="АвитоРабота.json",
        operation_id="vacancyGetItem",
    )
    def get(
        self,
        *,
        vacancy_id: int | str | None = None,
        query: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> VacancyInfo:
        """Возвращает вакансий.

        Аргументы:
            vacancy_id: идентифицирует вакансию.
            query: передает поисковую строку или фильтр upstream API.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `VacancyInfo` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_VACANCY,
            path_params={"vacancy_id": vacancy_id or self._require_vacancy_id()},
            query=VacanciesQuery(query=query),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/batch",
        spec="АвитоРабота.json",
        operation_id="vacanciesGetByIds",
        method_args={"ids": "body.ids"},
    )
    def get_by_ids(
        self,
        *,
        ids: Sequence[int],
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> VacanciesResult:
        """Возвращает вакансий.

        Аргументы:
            ids: передает идентификаторы объектов для пакетной операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `VacanciesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_VACANCIES_BY_IDS,
            request=VacancyIdsRequest(ids=list(ids)),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/statuses",
        spec="АвитоРабота.json",
        operation_id="vacancyGetStatuses",
        method_args={"ids": "body.ids"},
    )
    def get_statuses(
        self,
        *,
        ids: Sequence[int],
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> VacancyStatusesResult:
        """Возвращает statuses для вакансий.

        Аргументы:
            ids: передает идентификаторы объектов для пакетной операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `VacancyStatusesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_VACANCY_STATUSES,
            request=VacancyIdsRequest(ids=list(ids)),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "PUT",
        "/job/v2/vacancies/{vacancy_uuid}/auto_renewal",
        spec="АвитоРабота.json",
        operation_id="vacancyAutoRenewal",
        method_args={"auto_renewal": "body.auto_renewal"},
    )
    def update_auto_renewal(
        self,
        *,
        auto_renewal: bool,
        vacancy_uuid: str | None = None,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Обновляет настройку автопродления вакансии.

        Аргументы:
            auto_renewal: включает или отключает автопродление вакансии.
            vacancy_uuid: идентифицирует вакансию по UUID.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            UPDATE_VACANCY_AUTO_RENEWAL,
            path_params={"vacancy_uuid": vacancy_uuid or self._require_vacancy_id()},
            request=VacancyAutoRenewalRequest(auto_renewal=auto_renewal),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    def _require_vacancy_id(self) -> str:
        if self.vacancy_id is None:
            raise ValidationError("Для операции требуется идентификатор вакансии.")
        return str(self.vacancy_id)


@dataclass(slots=True, frozen=True)
class Application(DomainObject):
    """Доменный объект откликов."""

    __swagger_domain__ = "jobs"
    __sdk_factory__ = "application"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/job/v1/applications/apply_actions",
        spec="АвитоРабота.json",
        operation_id="applicationsApplyActions",
        method_args={"ids": "body.ids", "action": "body.action"},
    )
    def apply(
        self,
        *,
        ids: Sequence[str],
        action: str,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Применяет действие к откликов на вакансии.

        Аргументы:
            ids: передает идентификаторы объектов для пакетной операции.
            action: задает действие над откликами.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            APPLY_APPLICATION_ACTIONS,
            request=ApplicationActionRequest(ids=list(ids), action=action),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "POST",
        "/job/v1/applications/get_by_ids",
        spec="АвитоРабота.json",
        operation_id="applicationsGetByIds",
        method_args={"ids": "body.ids"},
    )
    def get_by_ids(
        self,
        *,
        ids: Sequence[str],
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> ApplicationsResult:
        """Возвращает отклики по идентификаторам и возвращает типизированную SDK-модель.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_APPLICATIONS_BY_IDS,
            request=ApplicationIdsRequest(ids=list(ids)),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v1/applications/get_ids",
        spec="АвитоРабота.json",
        operation_id="applicationsGetIds",
        method_args={"updated_at_from": "query.updatedAtFrom"},
    )
    def get_ids(
        self,
        *,
        updated_at_from: str,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> ApplicationIdsResult:
        """Возвращает идентификаторы откликов по фильтру и возвращает типизированную SDK-модель.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_APPLICATION_IDS,
            query=ApplicationIdsQuery(updated_at_from=updated_at_from),
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v1/applications/get_states",
        spec="АвитоРабота.json",
        operation_id="applicationsGetStates",
    )
    def get_states(
        self, *, timeout: ApiTimeouts | None = None, retry: RetryOverride | None = None
    ) -> ApplicationStatesResult:
        """Возвращает states для откликов на вакансии.

        Аргументы:
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `ApplicationStatesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_APPLICATION_STATES, timeout=timeout, retry=retry)

    @swagger_operation(
        "POST",
        "/job/v1/applications/set_is_viewed",
        spec="АвитоРабота.json",
        operation_id="applicationsSetIsViewed",
        method_args={"applies": "body.applies"},
    )
    def update(
        self,
        *,
        applies: Sequence[ApplicationViewedItem],
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Обновляет отметки просмотра откликов на вакансии.

        Аргументы:
            applies: передает список отметок просмотра откликов.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SET_APPLICATIONS_IS_VIEWED,
            request=ApplicationViewedRequest(
                applies=[
                    ApplicationViewedRequestItem(id=item.id, is_viewed=item.is_viewed)
                    for item in applies
                ]
            ),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )


@dataclass(slots=True, frozen=True)
class Resume(DomainObject):
    """Доменный объект резюме."""

    __swagger_domain__ = "jobs"
    __sdk_factory__ = "resume"
    __sdk_factory_args__ = {"resume_id": "path.resume_id"}

    resume_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/job/v1/resumes",
        spec="АвитоРабота.json",
        operation_id="resumesGet",
    )
    def list(
        self,
        *,
        query: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> ResumesResult:
        """Возвращает список резюме.

        Аргументы:
            query: передает поисковую строку или фильтр upstream API.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `ResumesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SEARCH_RESUMES,
            query=ResumeSearchQuery(query=query) if query is not None else None,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v2/resumes/{resume_id}",
        spec="АвитоРабота.json",
        operation_id="resumeGetItem",
    )
    def get(
        self,
        *,
        resume_id: int | str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> ResumeInfo:
        """Возвращает резюме.

        Аргументы:
            resume_id: идентифицирует резюме.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `ResumeInfo` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_RESUME,
            path_params={"resume_id": str(resume_id or self._require_resume_id())},
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "GET",
        "/job/v1/resumes/{resume_id}/contacts",
        spec="АвитоРабота.json",
        operation_id="resumeGetContacts",
    )
    def get_contacts(
        self,
        *,
        resume_id: int | str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> ResumeContactInfo:
        """Возвращает contacts для резюме.

        Аргументы:
            resume_id: идентифицирует резюме.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `ResumeContactInfo` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_RESUME_CONTACTS,
            path_params={"resume_id": str(resume_id or self._require_resume_id())},
            timeout=timeout,
            retry=retry,
        )

    def _require_resume_id(self) -> str:
        if self.resume_id is None:
            raise ValidationError("Для операции требуется `resume_id`.")
        return str(self.resume_id)


@dataclass(slots=True, frozen=True)
class JobWebhook(DomainObject):
    """Доменный объект webhook откликов."""

    __swagger_domain__ = "jobs"
    __sdk_factory__ = "job_webhook"

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/job/v1/applications/webhook",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhookGet",
    )
    def get(
        self, *, timeout: ApiTimeouts | None = None, retry: RetryOverride | None = None
    ) -> JobWebhookInfo:
        """Возвращает webhook-уведомлений Авито Работы.

        Аргументы:
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobWebhookInfo` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_JOB_WEBHOOK, timeout=timeout, retry=retry)

    @swagger_operation(
        "GET",
        "/job/v1/applications/webhooks",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhooksGet",
    )
    def list(
        self, *, timeout: ApiTimeouts | None = None, retry: RetryOverride | None = None
    ) -> JobWebhooksResult:
        """Возвращает список webhook-уведомлений Авито Работы.

        Аргументы:
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobWebhooksResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(LIST_JOB_WEBHOOKS, timeout=timeout, retry=retry)

    @swagger_operation(
        "PUT",
        "/job/v1/applications/webhook",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhookPut",
        method_args={"url": "body.url"},
    )
    def update(
        self,
        *,
        url: str,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobWebhookInfo:
        """Обновляет webhook-уведомление Авито Работы.

        Аргументы:
            url: задает URL webhook-подписки.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobWebhookInfo` с типизированными данными ответа API.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            UPDATE_JOB_WEBHOOK,
            request=JobWebhookUpdateRequest(url=url),
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )

    @swagger_operation(
        "DELETE",
        "/job/v1/applications/webhook",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhookDelete",
    )
    def delete(
        self,
        *,
        url: str | None = None,
        idempotency_key: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobActionResult:
        """Удаляет webhook-уведомление Авито Работы.

        Аргументы:
            url: задает URL webhook-подписки.
            idempotency_key: задает ключ идемпотентности для безопасного повтора write-операции.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobActionResult` со статусом выполнения операции.

        Поведение:
            `idempotency_key` следует передавать для write-операций, которые могут безопасно повторяться.
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELETE_JOB_WEBHOOK,
            query={"url": url} if url is not None else None,
            idempotency_key=idempotency_key,
            timeout=timeout,
            retry=retry,
        )


@dataclass(slots=True, frozen=True)
class JobDictionary(DomainObject):
    """Доменный объект словарей вакансий."""

    __swagger_domain__ = "jobs"
    __sdk_factory__ = "job_dictionary"
    __sdk_factory_args__ = {"dictionary_id": "path.dictionary_id"}

    dictionary_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/job/v2/vacancy/dict",
        spec="АвитоРабота.json",
        operation_id="getDicts",
    )
    def list(
        self, *, timeout: ApiTimeouts | None = None, retry: RetryOverride | None = None
    ) -> JobDictionariesResult:
        """Возвращает список справочников Авито Работы.

        Аргументы:
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobDictionariesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(LIST_JOB_DICTIONARIES, timeout=timeout, retry=retry)

    @swagger_operation(
        "GET",
        "/job/v2/vacancy/dict/{dictionary_id}",
        spec="АвитоРабота.json",
        operation_id="getDictByID",
    )
    def get(
        self,
        *,
        dictionary_id: str | None = None,
        timeout: ApiTimeouts | None = None,
        retry: RetryOverride | None = None,
    ) -> JobDictionaryValuesResult:
        """Возвращает справочников Авито Работы.

        Аргументы:
            dictionary_id: идентифицирует справочник.
            timeout: переопределяет таймауты HTTP-запроса для этого вызова.
            retry: переопределяет retry-политику операции: default, enabled или disabled.

        Возвращает:
            `JobDictionaryValuesResult` с типизированными данными ответа API.

        Поведение:
            `timeout` и `retry` действуют только на этот вызов и не меняют настройки клиента.

        Исключения:
            AvitoError: ошибка SDK с контекстом operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_JOB_DICTIONARY,
            path_params={"dictionary_id": dictionary_id or self._require_dictionary_id()},
            timeout=timeout,
            retry=retry,
        )

    def _require_dictionary_id(self) -> str:
        if self.dictionary_id is None:
            raise ValidationError("Для операции требуется `dictionary_id`.")
        return str(self.dictionary_id)


__all__ = ("Application", "JobDictionary", "JobWebhook", "Resume", "Vacancy")
