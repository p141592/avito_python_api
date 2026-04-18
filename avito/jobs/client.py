"""Внутренние section clients для пакета jobs."""

from __future__ import annotations

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


@dataclass(slots=True)
class ApplicationsClient:
    """Выполняет HTTP-операции откликов."""

    transport: Transport

    def apply_actions(self, request: ApplicationActionRequest) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/apply_actions", "jobs.applications.apply_actions", request
        )

    def get_by_ids(self, request: ApplicationIdsRequest) -> ApplicationsResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v1/applications/get_by_ids",
            context=RequestContext("jobs.applications.get_by_ids", allow_retry=True),
            mapper=map_applications,
            json_body=request.to_payload(),
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

    def set_is_viewed(self, request: ApplicationViewedRequest) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/set_is_viewed", "jobs.applications.set_is_viewed", request
        )

    def _post_action(
        self,
        path: str,
        operation: str,
        request: ApplicationActionRequest | ApplicationViewedRequest,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
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

    def put_webhook(self, request: JobWebhookUpdateRequest) -> JobWebhookInfo:
        return request_public_model(
            self.transport,
            "PUT",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.put", allow_retry=True),
            mapper=map_job_webhook,
            json_body=request.to_payload(),
        )

    def delete_webhook(self, *, url: str | None = None) -> JobActionResult:
        return request_public_model(
            self.transport,
            "DELETE",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.delete", allow_retry=True),
            mapper=map_job_action,
            params={"url": url},
        )

    def list_webhooks(self) -> JobWebhooksResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v1/applications/webhooks",
            context=RequestContext("jobs.webhook.list"),
            mapper=map_job_webhooks,
        )


@dataclass(slots=True)
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


@dataclass(slots=True)
class VacanciesClient:
    """Выполняет HTTP-операции вакансий."""

    transport: Transport

    def create_v1(self, request: VacancyCreateRequest) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v1/vacancies",
            context=RequestContext("jobs.vacancies.create_v1", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def archive_v1(
        self,
        *,
        vacancy_id: int | str,
        request: VacancyArchiveRequest,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v1/vacancies/archived/{vacancy_id}",
            context=RequestContext("jobs.vacancies.archive_v1", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def update_v1(
        self,
        *,
        vacancy_id: int | str,
        request: VacancyUpdateRequest,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v1/vacancies/{vacancy_id}",
            context=RequestContext("jobs.vacancies.update_v1", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def prolongate_v1(
        self,
        *,
        vacancy_id: int | str,
        request: VacancyProlongateRequest,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            f"/job/v1/vacancies/{vacancy_id}/prolongate",
            context=RequestContext("jobs.vacancies.prolongate_v1", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def list_v2(self, *, query: VacanciesQuery | None = None) -> VacanciesResult:
        return request_public_model(
            self.transport,
            "GET",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.list_v2"),
            mapper=map_vacancies,
            params=query.to_params() if query is not None else None,
        )

    def create_v2(self, request: VacancyCreateRequest) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.create_v2", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def get_by_ids_v2(self, request: VacancyIdsRequest) -> VacanciesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies/batch",
            context=RequestContext("jobs.vacancies.get_by_ids_v2", allow_retry=True),
            mapper=map_vacancies,
            json_body=request.to_payload(),
        )

    def get_statuses_v2(self, request: VacancyIdsRequest) -> VacancyStatusesResult:
        return request_public_model(
            self.transport,
            "POST",
            "/job/v2/vacancies/statuses",
            context=RequestContext("jobs.vacancies.get_statuses_v2", allow_retry=True),
            mapper=map_vacancy_statuses,
            json_body=request.to_payload(),
        )

    def update_v2(self, *, vacancy_uuid: str, request: VacancyUpdateRequest) -> JobActionResult:
        return request_public_model(
            self.transport,
            "POST",
            f"/job/v2/vacancies/update/{vacancy_uuid}",
            context=RequestContext("jobs.vacancies.update_v2", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )

    def get_item_v2(
        self, *, vacancy_id: int | str, query: VacanciesQuery | None = None
    ) -> VacancyInfo:
        return request_public_model(
            self.transport,
            "GET",
            f"/job/v2/vacancies/{vacancy_id}",
            context=RequestContext("jobs.vacancies.get_item_v2"),
            mapper=map_vacancy_item,
            params=query.to_params() if query is not None else None,
        )

    def auto_renewal_v2(
        self,
        *,
        vacancy_uuid: str,
        request: VacancyAutoRenewalRequest,
    ) -> JobActionResult:
        return request_public_model(
            self.transport,
            "PUT",
            f"/job/v2/vacancies/{vacancy_uuid}/auto_renewal",
            context=RequestContext("jobs.vacancies.auto_renewal_v2", allow_retry=True),
            mapper=map_job_action,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
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
