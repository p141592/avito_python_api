"""Доменные объекты пакета jobs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.jobs.client import (
    ApplicationsClient,
    DictionariesClient,
    ResumeClient,
    VacanciesClient,
    WebhookClient,
)
from avito.jobs.models import (
    ApplicationIdsQuery,
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    ApplicationViewedItem,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryValuesResult,
    JobWebhookInfo,
    JobWebhooksResult,
    ResumeContactInfo,
    ResumeInfo,
    ResumeSearchQuery,
    ResumesResult,
    VacanciesQuery,
    VacanciesResult,
    VacancyInfo,
    VacancyStatusesResult,
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
    @swagger_operation(
        "POST",
        "/job/v1/vacancies",
        spec="АвитоРабота.json",
        operation_id="vacancyCreate",
        method_args={"title": "body.title"},
    )
    def create(
        self,
        *,
        title: str,
        version: int = 2,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        """Выполняет публичную операцию `Vacancy.create` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        client = VacanciesClient(self.transport)
        if version == 1:
            return client.create_classic(title=title, idempotency_key=idempotency_key)
        return client.create(title=title, idempotency_key=idempotency_key)

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/update/{vacancy_uuid}",
        spec="АвитоРабота.json",
        operation_id="vacancyUpdateV2",
        method_args={"title": "body.title"},
    )
    @swagger_operation(
        "PUT",
        "/job/v1/vacancies/{vacancy_id}",
        spec="АвитоРабота.json",
        operation_id="vacancyUpdate",
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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Vacancy.update` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        client = VacanciesClient(self.transport)
        if version == 1:
            return client.update_classic(
                vacancy_id=vacancy_id or self._require_vacancy_id(),
                title=title,
                idempotency_key=idempotency_key,
            )
        return client.update(
            vacancy_uuid=vacancy_uuid or self._require_vacancy_id(),
            title=title,
            idempotency_key=idempotency_key,
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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Vacancy.delete` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).archive(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            employee_id=employee_id,
            idempotency_key=idempotency_key,
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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Vacancy.prolongate` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).prolongate(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            billing_type=billing_type,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/job/v2/vacancies",
        spec="АвитоРабота.json",
        operation_id="searchVacancy",
    )
    def list(self, *, query: VacanciesQuery | None = None) -> VacanciesResult:
        """Выполняет публичную операцию `Vacancy.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).list(query=query)

    @swagger_operation(
        "GET",
        "/job/v2/vacancies/{vacancy_id}",
        spec="АвитоРабота.json",
        operation_id="vacancyGetItem",
    )
    def get(
        self, *, vacancy_id: int | str | None = None, query: VacanciesQuery | None = None
    ) -> VacancyInfo:
        """Выполняет публичную операцию `Vacancy.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).get_item(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            query=query,
        )

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/batch",
        spec="АвитоРабота.json",
        operation_id="vacanciesGetByIds",
        method_args={"ids": "body.ids"},
    )
    def get_by_ids(self, *, ids: Sequence[int]) -> VacanciesResult:
        """Выполняет публичную операцию `Vacancy.get_by_ids` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).get_by_ids(ids=list(ids))

    @swagger_operation(
        "POST",
        "/job/v2/vacancies/statuses",
        spec="АвитоРабота.json",
        operation_id="vacancyGetStatuses",
        method_args={"ids": "body.ids"},
    )
    def get_statuses(self, *, ids: Sequence[int]) -> VacancyStatusesResult:
        """Выполняет публичную операцию `Vacancy.get_statuses` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).get_statuses(ids=list(ids))

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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Vacancy.update_auto_renewal` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return VacanciesClient(self.transport).update_auto_renewal(
            vacancy_uuid=vacancy_uuid or self._require_vacancy_id(),
            auto_renewal=auto_renewal,
            idempotency_key=idempotency_key,
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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Application.apply` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ApplicationsClient(self.transport).apply_actions(
            ids=list(ids),
            action=action,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/job/v1/applications/get_ids",
        spec="АвитоРабота.json",
        operation_id="applicationsGetIds",
    )
    @swagger_operation(
        "POST",
        "/job/v1/applications/get_by_ids",
        spec="АвитоРабота.json",
        operation_id="applicationsGetByIds",
    )
    def list(
        self,
        *,
        ids: Sequence[str] | None = None,
        query: ApplicationIdsQuery | None = None,
    ) -> ApplicationsResult | ApplicationIdsResult:
        """Выполняет публичную операцию `Application.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        client = ApplicationsClient(self.transport)
        if ids is not None:
            return client.get_by_ids(ids=list(ids))
        if query is None:
            raise ValidationError("Для операции требуется `query` или `ids`.")
        return client.get_ids(query=query)

    @swagger_operation(
        "GET",
        "/job/v1/applications/get_states",
        spec="АвитоРабота.json",
        operation_id="applicationsGetStates",
    )
    def get_states(self) -> ApplicationStatesResult:
        """Выполняет публичную операцию `Application.get_states` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ApplicationsClient(self.transport).get_states()

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
    ) -> JobActionResult:
        """Выполняет публичную операцию `Application.update` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ApplicationsClient(self.transport).set_is_viewed(
            applies=list(applies),
            idempotency_key=idempotency_key,
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
    def list(self, *, query: ResumeSearchQuery | None = None) -> ResumesResult:
        """Выполняет публичную операцию `Resume.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ResumeClient(self.transport).search(query=query)

    @swagger_operation(
        "GET",
        "/job/v2/resumes/{resume_id}",
        spec="АвитоРабота.json",
        operation_id="resumeGetItem",
    )
    def get(self, *, resume_id: int | str | None = None) -> ResumeInfo:
        """Выполняет публичную операцию `Resume.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ResumeClient(self.transport).get_item(
            resume_id=str(resume_id or self._require_resume_id())
        )

    @swagger_operation(
        "GET",
        "/job/v1/resumes/{resume_id}/contacts",
        spec="АвитоРабота.json",
        operation_id="resumeGetContacts",
    )
    def get_contacts(self, *, resume_id: int | str | None = None) -> ResumeContactInfo:
        """Выполняет публичную операцию `Resume.get_contacts` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ResumeClient(self.transport).get_contacts(
            resume_id=str(resume_id or self._require_resume_id())
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
    def get(self) -> JobWebhookInfo:
        """Выполняет публичную операцию `JobWebhook.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).get_webhook()

    @swagger_operation(
        "GET",
        "/job/v1/applications/webhooks",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhooksGet",
    )
    def list(self) -> JobWebhooksResult:
        """Выполняет публичную операцию `JobWebhook.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).list_webhooks()

    @swagger_operation(
        "PUT",
        "/job/v1/applications/webhook",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhookPut",
        method_args={"url": "body.url"},
    )
    def update(self, *, url: str, idempotency_key: str | None = None) -> JobWebhookInfo:
        """Выполняет публичную операцию `JobWebhook.update` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).put_webhook(
            url=url,
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "DELETE",
        "/job/v1/applications/webhook",
        spec="АвитоРабота.json",
        operation_id="applicationsWebhookDelete",
    )
    def delete(
        self, *, url: str | None = None, idempotency_key: str | None = None
    ) -> JobActionResult:
        """Выполняет публичную операцию `JobWebhook.delete` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return WebhookClient(self.transport).delete_webhook(
            url=url,
            idempotency_key=idempotency_key,
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
    def list(self) -> JobDictionariesResult:
        """Выполняет публичную операцию `JobDictionary.list` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DictionariesClient(self.transport).list_dicts()

    @swagger_operation(
        "GET",
        "/job/v2/vacancy/dict/{dictionary_id}",
        spec="АвитоРабота.json",
        operation_id="getDictByID",
    )
    def get(self, *, dictionary_id: str | None = None) -> JobDictionaryValuesResult:
        """Выполняет публичную операцию `JobDictionary.get` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return DictionariesClient(self.transport).get_dict_by_id(
            dictionary_id=dictionary_id or self._require_dictionary_id()
        )

    def _require_dictionary_id(self) -> str:
        if self.dictionary_id is None:
            raise ValidationError("Для операции требуется `dictionary_id`.")
        return str(self.dictionary_id)


__all__ = ("Application", "JobDictionary", "JobWebhook", "Resume", "Vacancy")
