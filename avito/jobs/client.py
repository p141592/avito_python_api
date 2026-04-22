"""Внутренние section clients для пакета jobs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.core.mapping import request_public_model
from avito.jobs.mappers import (
    map_application_ids,
    map_application_states,
    map_applications,
    map_job_action,
    map_job_dictionaries,
    map_job_dictionary_values,
    map_job_webhook,
    map_job_webhooks,
    map_resume_contacts,
    map_resume_item,
    map_resumes,
    map_vacancies,
    map_vacancy_item,
    map_vacancy_statuses,
)
from avito.jobs.models import (
    ApplicationActionRequest,
    ApplicationIdsQuery,
    ApplicationIdsRequest,
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    ApplicationViewedItem,
    ApplicationViewedRequest,
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


@dataclass(slots=True, frozen=True)
class ApplicationsClient:
    """Выполняет HTTP-операции откликов."""

    transport: Transport

    def apply_actions(
        self,
        *,
        ids: list[str],
        action: str,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/apply_actions",
            "jobs.applications.apply_actions",
            ApplicationActionRequest(ids=ids, action=action),
            idempotency_key=idempotency_key,
        )

    def get_by_ids(self, *, ids: list[str]) -> ApplicationsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v1/applications/get_by_ids",
            context=RequestContext("jobs.applications.get_by_ids", allow_retry=True),
            mapper=map_applications,
            json_body=ApplicationIdsRequest(ids=ids).to_payload(),
        )

    def get_ids(self, *, query: ApplicationIdsQuery) -> ApplicationIdsResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/applications/get_ids",
            context=RequestContext("jobs.applications.get_ids"),
            mapper=map_application_ids,
            params=query.to_params(),
        )

    def get_states(self) -> ApplicationStatesResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/applications/get_states",
            context=RequestContext("jobs.applications.get_states"),
            mapper=map_application_states,
        )

    def set_is_viewed(
        self,
        *,
        applies: list[ApplicationViewedItem],
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/set_is_viewed",
            "jobs.applications.set_is_viewed",
            ApplicationViewedRequest(applies=applies),
            idempotency_key=idempotency_key,
        )

    def _post_action(
        self,
        path: str,
        operation: str,
        request: ApplicationActionRequest | ApplicationViewedRequest,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            path,
            context=RequestContext(operation, allow_retry=idempotency_key is not None),
            mapper=map_job_action,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class WebhookClient:
    """Выполняет HTTP-операции webhook откликов."""

    transport: Transport

    def get_webhook(self) -> JobWebhookInfo:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.get"),
            mapper=map_job_webhook,
        )

    def put_webhook(self, *, url: str, idempotency_key: str | None = None) -> JobWebhookInfo:
        return request_public_model(
            self.transport,
            "PUT",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.put", allow_retry=idempotency_key is not None),
            mapper=map_job_webhook,
            json_body=JobWebhookUpdateRequest(url=url).to_payload(),
            idempotency_key=idempotency_key,
        )

    def delete_webhook(
        self, *, url: str | None = None, idempotency_key: str | None = None
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "DELETE",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.delete", allow_retry=idempotency_key is not None),
            mapper=map_job_action,
            params={"url": url},
            idempotency_key=idempotency_key,
        )

    def list_webhooks(self) -> JobWebhooksResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/applications/webhooks",
            context=RequestContext("jobs.webhook.list"),
            mapper=map_job_webhooks,
        )


@dataclass(slots=True, frozen=True)
class ResumeClient:
    """Выполняет HTTP-операции резюме."""

    transport: Transport

    def search(self, *, query: ResumeSearchQuery | None = None) -> ResumesResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/resumes/",
            context=RequestContext("jobs.resumes.search"),
            mapper=map_resumes,
            params=query.to_params() if query is not None else None,
        )

    def get_contacts(self, *, resume_id: str) -> ResumeContactInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/job/v1/resumes/{resume_id}/contacts/",
            context=RequestContext("jobs.resumes.get_contacts"),
            mapper=map_resume_contacts,
        )

    def get_item(self, *, resume_id: str) -> ResumeInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/job/v2/resumes/{resume_id}",
            context=RequestContext("jobs.resumes.get_item"),
            mapper=map_resume_item,
        )


@dataclass(slots=True, frozen=True)
class VacanciesClient:
    """Выполняет HTTP-операции вакансий."""

    transport: Transport

    def create_classic(self, *, title: str, idempotency_key: str | None = None) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v1/vacancies",
            context=RequestContext(
                "jobs.vacancies.create_classic",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_job_action,
            json_body=VacancyCreateRequest(title=title).to_payload(),
            idempotency_key=idempotency_key,
        )

    def archive(
        self,
        *,
        vacancy_id: int | str,
        employee_id: int,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v1/vacancies/archived/{vacancy_id}",
            context=RequestContext("jobs.vacancies.archive", allow_retry=idempotency_key is not None),
            mapper=map_job_action,
            json_body=VacancyArchiveRequest(employee_id=employee_id).to_payload(),
            idempotency_key=idempotency_key,
        )

    def update_classic(
        self,
        *,
        vacancy_id: int | str,
        title: str,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v1/vacancies/{vacancy_id}",
            context=RequestContext(
                "jobs.vacancies.update_classic",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_job_action,
            json_body=VacancyUpdateRequest(title=title).to_payload(),
            idempotency_key=idempotency_key,
        )

    def prolongate(
        self,
        *,
        vacancy_id: int | str,
        billing_type: str,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            f"/job/v1/vacancies/{vacancy_id}/prolongate",
            context=RequestContext(
                "jobs.vacancies.prolongate",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_job_action,
            json_body=VacancyProlongateRequest(billing_type=billing_type).to_payload(),
            idempotency_key=idempotency_key,
        )

    def list(self, *, query: VacanciesQuery | None = None) -> VacanciesResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.list"),
            mapper=map_vacancies,
            params=query.to_params() if query is not None else None,
        )

    def create(self, *, title: str, idempotency_key: str | None = None) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.create", allow_retry=idempotency_key is not None),
            mapper=map_job_action,
            json_body=VacancyCreateRequest(title=title).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_by_ids(self, *, ids: Sequence[int]) -> VacanciesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies/batch",
            context=RequestContext("jobs.vacancies.get_by_ids", allow_retry=True),
            mapper=map_vacancies,
            json_body=VacancyIdsRequest(ids=list(ids)).to_payload(),
        )

    def get_statuses(self, *, ids: Sequence[int]) -> VacancyStatusesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies/statuses",
            context=RequestContext("jobs.vacancies.get_statuses", allow_retry=True),
            mapper=map_vacancy_statuses,
            json_body=VacancyIdsRequest(ids=list(ids)).to_payload(),
        )

    def update(
        self,
        *,
        vacancy_uuid: str,
        title: str,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            f"/job/v2/vacancies/update/{vacancy_uuid}",
            context=RequestContext("jobs.vacancies.update", allow_retry=idempotency_key is not None),
            mapper=map_job_action,
            json_body=VacancyUpdateRequest(title=title).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_item(
        self, *, vacancy_id: int | str, query: VacanciesQuery | None = None
    ) -> VacancyInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/job/v2/vacancies/{vacancy_id}",
            context=RequestContext("jobs.vacancies.get_item"),
            mapper=map_vacancy_item,
            params=query.to_params() if query is not None else None,
        )

    def update_auto_renewal(
        self,
        *,
        vacancy_uuid: str,
        auto_renewal: bool,
        idempotency_key: str | None = None,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v2/vacancies/{vacancy_uuid}/auto_renewal",
            context=RequestContext(
                "jobs.vacancies.update_auto_renewal",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_job_action,
            json_body=VacancyAutoRenewalRequest(auto_renewal=auto_renewal).to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class DictionariesClient:
    """Выполняет HTTP-операции словарей вакансий."""

    transport: Transport

    def list_dicts(self) -> JobDictionariesResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v2/vacancy/dict",
            context=RequestContext("jobs.dictionaries.list_dicts"),
            mapper=map_job_dictionaries,
        )

    def get_dict_by_id(self, *, dictionary_id: str) -> JobDictionaryValuesResult:
        return request_public_model(
            self.transport,
            "GET",
            f"/job/v2/vacancy/dict/{dictionary_id}",
            context=RequestContext("jobs.dictionaries.get_dict_by_id"),
            mapper=map_job_dictionary_values,
        )


__all__ = (
    "ApplicationsClient",
    "DictionariesClient",
    "ResumeClient",
    "VacanciesClient",
    "WebhookClient",
)
