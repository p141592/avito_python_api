"""Внутренние section clients для пакета jobs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import RequestContext, Transport
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
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryValuesResult,
    JobWebhookInfo,
    JobWebhooksResult,
    JsonRequest,
    ResumeContactInfo,
    ResumeInfo,
    ResumesResult,
    VacanciesResult,
    VacancyInfo,
    VacancyStatusesResult,
)


@dataclass(slots=True)
class ApplicationsClient:
    """Выполняет HTTP-операции откликов."""

    transport: Transport

    def apply_actions(self, request: JsonRequest) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/apply_actions", "jobs.applications.apply_actions", request
        )

    def get_by_ids(self, request: JsonRequest) -> ApplicationsResult:
        payload = self.transport.request_json(
            "POST",
            "/job/v1/applications/get_by_ids",
            context=RequestContext("jobs.applications.get_by_ids", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_applications(payload)

    def get_ids(self, *, params: Mapping[str, object]) -> ApplicationIdsResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v1/applications/get_ids",
            context=RequestContext("jobs.applications.get_ids"),
            params=params,
        )
        return map_application_ids(payload)

    def get_states(self) -> ApplicationStatesResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v1/applications/get_states",
            context=RequestContext("jobs.applications.get_states"),
        )
        return map_application_states(payload)

    def set_is_viewed(self, request: JsonRequest) -> JobActionResult:
        return self._post_action(
            "/job/v1/applications/set_is_viewed", "jobs.applications.set_is_viewed", request
        )

    def _post_action(self, path: str, operation: str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=RequestContext(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)


@dataclass(slots=True)
class WebhookClient:
    """Выполняет HTTP-операции webhook откликов."""

    transport: Transport

    def get_webhook(self) -> JobWebhookInfo:
        payload = self.transport.request_json(
            "GET",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.get"),
        )
        return map_job_webhook(payload)

    def put_webhook(self, request: JsonRequest) -> JobWebhookInfo:
        payload = self.transport.request_json(
            "PUT",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.put", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_webhook(payload)

    def delete_webhook(self, *, url: str | None = None) -> JobActionResult:
        payload = self.transport.request_json(
            "DELETE",
            "/job/v1/applications/webhook",
            context=RequestContext("jobs.webhook.delete", allow_retry=True),
            params={"url": url},
        )
        return map_job_action(payload)

    def list_webhooks(self) -> JobWebhooksResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v1/applications/webhooks",
            context=RequestContext("jobs.webhook.list"),
        )
        return map_job_webhooks(payload)


@dataclass(slots=True)
class ResumeClient:
    """Выполняет HTTP-операции резюме."""

    transport: Transport

    def search(self, *, params: Mapping[str, object] | None = None) -> ResumesResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v1/resumes/",
            context=RequestContext("jobs.resumes.search"),
            params=params,
        )
        return map_resumes(payload)

    def get_contacts(self, *, resume_id: str) -> ResumeContactInfo:
        payload = self.transport.request_json(
            "GET",
            f"/job/v1/resumes/{resume_id}/contacts/",
            context=RequestContext("jobs.resumes.get_contacts"),
        )
        return map_resume_contacts(payload)

    def get_item(self, *, resume_id: str) -> ResumeInfo:
        payload = self.transport.request_json(
            "GET",
            f"/job/v2/resumes/{resume_id}",
            context=RequestContext("jobs.resumes.get_item"),
        )
        return map_resume_item(payload)


@dataclass(slots=True)
class VacanciesClient:
    """Выполняет HTTP-операции вакансий."""

    transport: Transport

    def create_v1(self, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "POST",
            "/job/v1/vacancies",
            context=RequestContext("jobs.vacancies.create_v1", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def archive_v1(self, *, vacancy_id: int | str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "PUT",
            f"/job/v1/vacancies/archived/{vacancy_id}",
            context=RequestContext("jobs.vacancies.archive_v1", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def update_v1(self, *, vacancy_id: int | str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "PUT",
            f"/job/v1/vacancies/{vacancy_id}",
            context=RequestContext("jobs.vacancies.update_v1", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def prolongate_v1(self, *, vacancy_id: int | str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "POST",
            f"/job/v1/vacancies/{vacancy_id}/prolongate",
            context=RequestContext("jobs.vacancies.prolongate_v1", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def list_v2(self, *, params: Mapping[str, object] | None = None) -> VacanciesResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.list_v2"),
            params=params,
        )
        return map_vacancies(payload)

    def create_v2(self, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "POST",
            "/job/v2/vacancies",
            context=RequestContext("jobs.vacancies.create_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def get_by_ids_v2(self, request: JsonRequest) -> VacanciesResult:
        payload = self.transport.request_json(
            "POST",
            "/job/v2/vacancies/batch",
            context=RequestContext("jobs.vacancies.get_by_ids_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_vacancies(payload)

    def get_statuses_v2(self, request: JsonRequest) -> VacancyStatusesResult:
        payload = self.transport.request_json(
            "POST",
            "/job/v2/vacancies/statuses",
            context=RequestContext("jobs.vacancies.get_statuses_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_vacancy_statuses(payload)

    def update_v2(self, *, vacancy_uuid: str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "POST",
            f"/job/v2/vacancies/update/{vacancy_uuid}",
            context=RequestContext("jobs.vacancies.update_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)

    def get_item_v2(
        self, *, vacancy_id: int | str, params: Mapping[str, object] | None = None
    ) -> VacancyInfo:
        payload = self.transport.request_json(
            "GET",
            f"/job/v2/vacancies/{vacancy_id}",
            context=RequestContext("jobs.vacancies.get_item_v2"),
            params=params,
        )
        return map_vacancy_item(payload)

    def auto_renewal_v2(self, *, vacancy_uuid: str, request: JsonRequest) -> JobActionResult:
        payload = self.transport.request_json(
            "PUT",
            f"/job/v2/vacancies/{vacancy_uuid}/auto_renewal",
            context=RequestContext("jobs.vacancies.auto_renewal_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_job_action(payload)


@dataclass(slots=True)
class DictionariesClient:
    """Выполняет HTTP-операции словарей вакансий."""

    transport: Transport

    def list_dicts(self) -> JobDictionariesResult:
        payload = self.transport.request_json(
            "GET",
            "/job/v2/vacancy/dict",
            context=RequestContext("jobs.dictionaries.list_dicts"),
        )
        return map_job_dictionaries(payload)

    def get_dict_by_id(self, *, dictionary_id: str) -> JobDictionaryValuesResult:
        payload = self.transport.request_json(
            "GET",
            f"/job/v2/vacancy/dict/{dictionary_id}",
            context=RequestContext("jobs.dictionaries.get_dict_by_id"),
        )
        return map_job_dictionary_values(payload)


__all__ = (
    "ApplicationsClient",
    "DictionariesClient",
    "ResumeClient",
    "VacanciesClient",
    "WebhookClient",
)
