"""Доменные объекты пакета jobs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import Transport, ValidationError
from avito.jobs.client import (
    ApplicationsClient,
    DictionariesClient,
    ResumeClient,
    VacanciesClient,
    WebhookClient,
)
from avito.jobs.models import (
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryValuesResult,
    JobsQuery,
    JobsRequest,
    JobWebhookInfo,
    JobWebhooksResult,
    ResumeContactInfo,
    ResumeInfo,
    ResumesResult,
    VacanciesResult,
    VacancyInfo,
    VacancyStatusesResult,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела jobs."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class Vacancy(DomainObject):
    """Доменный объект вакансий."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create(self, *, request: JobsRequest, version: int = 2) -> JobActionResult:
        client = VacanciesClient(self.transport)
        if version == 1:
            return client.create_v1(request)
        return client.create_v2(request)

    def update(
        self,
        *,
        request: JobsRequest,
        vacancy_id: int | str | None = None,
        vacancy_uuid: str | None = None,
        version: int = 2,
    ) -> JobActionResult:
        client = VacanciesClient(self.transport)
        if version == 1:
            return client.update_v1(
                vacancy_id=vacancy_id or self._require_resource_id(), request=request
            )
        return client.update_v2(
            vacancy_uuid=vacancy_uuid or self._require_resource_id(), request=request
        )

    def delete(
        self, *, request: JobsRequest, vacancy_id: int | str | None = None
    ) -> JobActionResult:
        return VacanciesClient(self.transport).archive_v1(
            vacancy_id=vacancy_id or self._require_resource_id(),
            request=request,
        )

    def prolongate(
        self, *, request: JobsRequest, vacancy_id: int | str | None = None
    ) -> JobActionResult:
        return VacanciesClient(self.transport).prolongate_v1(
            vacancy_id=vacancy_id or self._require_resource_id(),
            request=request,
        )

    def list(self, *, query: JobsQuery | None = None) -> VacanciesResult:
        return VacanciesClient(self.transport).list_v2(query=query)

    def get(
        self, *, vacancy_id: int | str | None = None, query: JobsQuery | None = None
    ) -> VacancyInfo:
        return VacanciesClient(self.transport).get_item_v2(
            vacancy_id=vacancy_id or self._require_resource_id(),
            query=query,
        )

    def get_by_ids(self, *, request: JobsRequest) -> VacanciesResult:
        return VacanciesClient(self.transport).get_by_ids_v2(request)

    def get_statuses(self, *, request: JobsRequest) -> VacancyStatusesResult:
        return VacanciesClient(self.transport).get_statuses_v2(request)

    def update_auto_renewal(
        self, *, request: JobsRequest, vacancy_uuid: str | None = None
    ) -> JobActionResult:
        return VacanciesClient(self.transport).auto_renewal_v2(
            vacancy_uuid=vacancy_uuid or self._require_resource_id(),
            request=request,
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется идентификатор вакансии.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class Application(DomainObject):
    """Доменный объект откликов."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def apply(self, *, request: JobsRequest) -> JobActionResult:
        return ApplicationsClient(self.transport).apply_actions(request)

    def list(
        self,
        *,
        request: JobsRequest | None = None,
        query: JobsQuery | None = None,
    ) -> ApplicationsResult | ApplicationIdsResult:
        client = ApplicationsClient(self.transport)
        if request is not None:
            return client.get_by_ids(request)
        return client.get_ids(query=query or JobsQuery(params={}))

    def get_states(self) -> ApplicationStatesResult:
        return ApplicationsClient(self.transport).get_states()

    def update(self, *, request: JobsRequest) -> JobActionResult:
        return ApplicationsClient(self.transport).set_is_viewed(request)


@dataclass(slots=True, frozen=True)
class Resume(DomainObject):
    """Доменный объект резюме."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list(self, *, query: JobsQuery | None = None) -> ResumesResult:
        return ResumeClient(self.transport).search(query=query)

    def get(self, *, resume_id: int | str | None = None) -> ResumeInfo:
        return ResumeClient(self.transport).get_item(
            resume_id=str(resume_id or self._require_resource_id())
        )

    def get_contacts(self, *, resume_id: int | str | None = None) -> ResumeContactInfo:
        return ResumeClient(self.transport).get_contacts(
            resume_id=str(resume_id or self._require_resource_id())
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `resume_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class JobWebhook(DomainObject):
    """Доменный объект webhook откликов."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> JobWebhookInfo:
        return WebhookClient(self.transport).get_webhook()

    def list(self) -> JobWebhooksResult:
        return WebhookClient(self.transport).list_webhooks()

    def update(self, *, request: JobsRequest) -> JobWebhookInfo:
        return WebhookClient(self.transport).put_webhook(request)

    def delete(self, *, url: str | None = None) -> JobActionResult:
        return WebhookClient(self.transport).delete_webhook(url=url)


@dataclass(slots=True, frozen=True)
class JobDictionary(DomainObject):
    """Доменный объект словарей вакансий."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def list(self) -> JobDictionariesResult:
        return DictionariesClient(self.transport).list_dicts()

    def get(self, *, dictionary_id: str | None = None) -> JobDictionaryValuesResult:
        return DictionariesClient(self.transport).get_dict_by_id(
            dictionary_id=dictionary_id or self._require_resource_id()
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `dictionary_id`.")
        return str(self.resource_id)


__all__ = ("Application", "DomainObject", "JobDictionary", "JobWebhook", "Resume", "Vacancy")
