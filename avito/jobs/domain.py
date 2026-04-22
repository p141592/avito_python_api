"""Доменные объекты пакета jobs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import ValidationError
from avito.core.domain import DomainObject
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

    vacancy_id: int | str | None = None
    user_id: int | str | None = None

    def create(
        self,
        *,
        title: str,
        version: int = 2,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        client = VacanciesClient(self.transport)
        if version == 1:
            return client.create_classic(title=title, idempotency_key=idempotency_key)
        return client.create(title=title, idempotency_key=idempotency_key)

    def update(
        self,
        *,
        title: str,
        vacancy_id: int | str | None = None,
        vacancy_uuid: str | None = None,
        version: int = 2,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
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

    def delete(
        self,
        *,
        employee_id: int,
        vacancy_id: int | str | None = None,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return VacanciesClient(self.transport).archive(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            employee_id=employee_id,
            idempotency_key=idempotency_key,
        )

    def prolongate(
        self,
        *,
        billing_type: str,
        vacancy_id: int | str | None = None,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return VacanciesClient(self.transport).prolongate(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            billing_type=billing_type,
            idempotency_key=idempotency_key,
        )

    def list(self, *, query: VacanciesQuery | None = None) -> VacanciesResult:
        return VacanciesClient(self.transport).list(query=query)

    def get(
        self, *, vacancy_id: int | str | None = None, query: VacanciesQuery | None = None
    ) -> VacancyInfo:
        return VacanciesClient(self.transport).get_item(
            vacancy_id=vacancy_id or self._require_vacancy_id(),
            query=query,
        )

    def get_by_ids(self, *, ids: Sequence[int]) -> VacanciesResult:
        return VacanciesClient(self.transport).get_by_ids(ids=list(ids))

    def get_statuses(self, *, ids: Sequence[int]) -> VacancyStatusesResult:
        return VacanciesClient(self.transport).get_statuses(ids=list(ids))

    def update_auto_renewal(
        self,
        *,
        auto_renewal: bool,
        vacancy_uuid: str | None = None,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
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

    user_id: int | str | None = None

    def apply(
        self,
        *,
        ids: Sequence[str],
        action: str,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return ApplicationsClient(self.transport).apply_actions(
            ids=list(ids),
            action=action,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        ids: Sequence[str] | None = None,
        query: ApplicationIdsQuery | None = None,
    ) -> ApplicationsResult | ApplicationIdsResult:
        client = ApplicationsClient(self.transport)
        if ids is not None:
            return client.get_by_ids(ids=list(ids))
        if query is None:
            raise ValidationError("Для операции требуется `query` или `ids`.")
        return client.get_ids(query=query)

    def get_states(self) -> ApplicationStatesResult:
        return ApplicationsClient(self.transport).get_states()

    def update(
        self,
        *,
        applies: Sequence[ApplicationViewedItem],
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return ApplicationsClient(self.transport).set_is_viewed(
            applies=list(applies),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class Resume(DomainObject):
    """Доменный объект резюме."""

    resume_id: int | str | None = None
    user_id: int | str | None = None

    def list(self, *, query: ResumeSearchQuery | None = None) -> ResumesResult:
        return ResumeClient(self.transport).search(query=query)

    def get(self, *, resume_id: int | str | None = None) -> ResumeInfo:
        return ResumeClient(self.transport).get_item(
            resume_id=str(resume_id or self._require_resume_id())
        )

    def get_contacts(self, *, resume_id: int | str | None = None) -> ResumeContactInfo:
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

    user_id: int | str | None = None

    def get(self) -> JobWebhookInfo:
        return WebhookClient(self.transport).get_webhook()

    def list(self) -> JobWebhooksResult:
        return WebhookClient(self.transport).list_webhooks()

    def update(
        self, *, url: str, idempotency_key: str | None = None
    ) -> JobWebhookInfo:
        return WebhookClient(self.transport).put_webhook(
            url=url,
            idempotency_key=idempotency_key,
        )

    def delete(
        self, *, url: str | None = None, idempotency_key: str | None = None
    ) -> JobActionResult:
        return WebhookClient(self.transport).delete_webhook(
            url=url,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class JobDictionary(DomainObject):
    """Доменный объект словарей вакансий."""

    dictionary_id: int | str | None = None
    user_id: int | str | None = None

    def list(self) -> JobDictionariesResult:
        return DictionariesClient(self.transport).list_dicts()

    def get(self, *, dictionary_id: str | None = None) -> JobDictionaryValuesResult:
        return DictionariesClient(self.transport).get_dict_by_id(
            dictionary_id=dictionary_id or self._require_dictionary_id()
        )

    def _require_dictionary_id(self) -> str:
        if self.dictionary_id is None:
            raise ValidationError("Для операции требуется `dictionary_id`.")
        return str(self.dictionary_id)


__all__ = ("Application", "JobDictionary", "JobWebhook", "Resume", "Vacancy")
