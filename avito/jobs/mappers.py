"""Мапперы JSON -> dataclass для пакета jobs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.enums import map_enum_or_unknown
from avito.core.exceptions import ResponseMappingError
from avito.jobs.enums import (
    ApplicationStatus,
    JobActionStatus,
    VacancyModerationStatus,
    VacancyStatus,
)
from avito.jobs.models import (
    ApplicationIdItem,
    ApplicationIdsResult,
    ApplicationInfo,
    ApplicationsResult,
    ApplicationState,
    ApplicationStatesResult,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryInfo,
    JobDictionaryValue,
    JobDictionaryValuesResult,
    JobWebhookInfo,
    JobWebhooksResult,
    ResumeContactInfo,
    ResumeInfo,
    ResumesResult,
    VacanciesResult,
    VacancyInfo,
    VacancyStatusesResult,
    VacancyStatusInfo,
)

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _expect_list(payload: object) -> list[Payload]:
    if not isinstance(payload, list):
        raise ResponseMappingError("Ожидался JSON-массив.", payload=payload)
    return [item for item in payload if isinstance(item, Mapping)]


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def map_job_action(payload: object) -> JobActionResult:
    """Преобразует результат mutation-операции Jobs API."""

    data = _expect_mapping(payload)
    result = _mapping(data, "result")
    source = result or data
    identifier = _str(source, "id", "uuid", "vacancy_uuid", "vacancyUuid", "apply_id")
    numeric_id = _int(source, "id", "vacancy_id", "vacancyId")
    return JobActionResult(
        success=bool(source.get("ok", source.get("success", True))),
        id=identifier or (str(numeric_id) if numeric_id is not None else None),
        status=map_enum_or_unknown(
            _str(source, "status", "state"),
            JobActionStatus,
            enum_name="jobs.action_status",
        ),
        message=_str(source, "message"),
    )


def map_application(payload: Payload) -> ApplicationInfo:
    return ApplicationInfo(
        id=_str(payload, "id"),
        vacancy_id=_int(payload, "vacancy_id", "vacancyId"),
        resume_id=_str(payload, "resume_id", "resumeId"),
        state=map_enum_or_unknown(
            _str(payload, "state", "status"),
            ApplicationStatus,
            enum_name="jobs.application_status",
        ),
        is_viewed=_bool(payload, "is_viewed", "isViewed"),
        applicant_name=_str(_mapping(payload, "applicant"), "name", "fullName"),
    )


def map_applications(payload: object) -> ApplicationsResult:
    """Преобразует список откликов."""

    data = _expect_mapping(payload)
    return ApplicationsResult(
        items=[
            map_application(item)
            for item in _list(data, "applies", "applications", "items", "result")
        ],
    )


def map_application_ids(payload: object) -> ApplicationIdsResult:
    """Преобразует список идентификаторов откликов."""

    data = _expect_mapping(payload)
    return ApplicationIdsResult(
        items=[
            ApplicationIdItem(
                id=_str(item, "id"),
                updated_at=_str(item, "updatedAt", "updated_at"),
            )
            for item in _list(data, "items", "applies", "result")
        ],
        cursor=_str(_mapping(data, "meta"), "cursor") or _str(data, "cursor"),
    )


def map_application_states(payload: object) -> ApplicationStatesResult:
    """Преобразует список статусов откликов."""

    data = _expect_mapping(payload)
    return ApplicationStatesResult(
        items=[
            ApplicationState(
                slug=_str(item, "slug", "id"),
                description=_str(item, "description", "name"),
            )
            for item in _list(data, "states", "items", "result")
        ],
    )


def map_resume(payload: Payload) -> ResumeInfo:
    salary_payload = _mapping(payload, "salary")
    return ResumeInfo(
        id=_str(payload, "id", "resume_id", "resumeId"),
        title=_str(payload, "title"),
        candidate_name=_str(payload, "name", "full_name", "fullName"),
        location=_str(payload, "location")
        or _str(_mapping(payload, "address_details"), "location"),
        salary=_int(payload, "salary") or _int(salary_payload, "value", "from"),
    )


def map_resumes(payload: object) -> ResumesResult:
    """Преобразует поиск резюме."""

    data = _expect_mapping(payload)
    meta = _mapping(data, "meta")
    return ResumesResult(
        items=[map_resume(item) for item in _list(data, "resumes", "items", "result")],
        cursor=_str(meta, "cursor"),
        total=_int(meta, "total"),
    )


def map_resume_item(payload: object) -> ResumeInfo:
    """Преобразует резюме в полную модель."""

    data = _expect_mapping(payload)
    return map_resume(data)


def map_resume_contacts(payload: object) -> ResumeContactInfo:
    """Преобразует контакты резюме."""

    data = _expect_mapping(payload)
    return ResumeContactInfo(
        name=_str(data, "name", "fullName"),
        phone=_str(data, "phone", "phoneNumber"),
        email=_str(data, "email"),
    )


def map_vacancy(payload: Payload) -> VacancyInfo:
    return VacancyInfo(
        id=_str(payload, "id", "vacancy_id", "vacancyId")
        or (
            str(_int(payload, "id", "vacancy_id", "vacancyId"))
            if _int(payload, "id", "vacancy_id", "vacancyId") is not None
            else None
        ),
        uuid=_str(payload, "uuid", "vacancy_uuid", "vacancyUuid"),
        title=_str(payload, "title", "name"),
        status=map_enum_or_unknown(
            _str(payload, "status", "state"),
            VacancyStatus,
            enum_name="jobs.vacancy_status",
        ),
        url=_str(payload, "url"),
    )


def map_vacancy_item(payload: object) -> VacancyInfo:
    """Преобразует одну вакансию."""

    data = _expect_mapping(payload)
    return map_vacancy(data)


def map_vacancies(payload: object) -> VacanciesResult:
    """Преобразует список вакансий."""

    data = _expect_mapping(payload)
    items = _list(data, "vacancies", "items", "result")
    if not items and isinstance(payload, list):
        items = _expect_list(payload)
    meta = _mapping(data, "meta")
    return VacanciesResult(
        items=[map_vacancy(item) for item in items],
        total=_int(meta, "total") or _int(data, "total"),
    )


def map_vacancy_statuses(payload: object) -> VacancyStatusesResult:
    """Преобразует статусы вакансий."""

    data = _expect_mapping(payload)
    return VacancyStatusesResult(
        items=[
            VacancyStatusInfo(
                id=_str(_mapping(item, "vacancy") or item, "id", "vacancy_id")
                or (
                    str(_int(_mapping(item, "vacancy") or item, "id", "vacancy_id"))
                    if _int(_mapping(item, "vacancy") or item, "id", "vacancy_id") is not None
                    else None
                ),
                uuid=_str(_mapping(item, "vacancy") or item, "uuid", "vacancy_uuid"),
                status=map_enum_or_unknown(
                    _str(_mapping(item, "vacancy") or item, "status", "state"),
                    VacancyStatus,
                    enum_name="jobs.vacancy_status",
                ),
                moderation_status=map_enum_or_unknown(
                    _str(_mapping(item, "vacancy") or item, "moderation_status", "moderationStatus"),
                    VacancyModerationStatus,
                    enum_name="jobs.vacancy_moderation_status",
                ),
            )
            for item in _list(data, "items", "statuses", "vacancies", "result")
        ],
    )


def map_job_webhook(payload: object) -> JobWebhookInfo:
    """Преобразует одну webhook-подписку."""

    data = _expect_mapping(payload)
    return JobWebhookInfo(
        url=_str(data, "url"),
        is_active=_bool(data, "is_active", "isActive", "active"),
        version=_str(data, "version"),
    )


def map_job_webhooks(payload: object) -> JobWebhooksResult:
    """Преобразует список webhook-подписок."""

    if isinstance(payload, list):
        items_payload = _expect_list(payload)
        return JobWebhooksResult(items=[map_job_webhook(item) for item in items_payload])

    data = _expect_mapping(payload)
    return JobWebhooksResult(
        items=[map_job_webhook(item) for item in _list(data, "items", "webhooks", "result")],
    )


def map_job_dictionaries(payload: object) -> JobDictionariesResult:
    """Преобразует список доступных словарей."""

    items_payload = (
        _expect_list(payload)
        if isinstance(payload, list)
        else _list(_expect_mapping(payload), "items", "result")
    )
    return JobDictionariesResult(
        items=[
            JobDictionaryInfo(
                id=_str(item, "id"),
                description=_str(item, "description"),
            )
            for item in items_payload
        ],
    )


def map_job_dictionary_values(payload: object) -> JobDictionaryValuesResult:
    """Преобразует значения словаря вакансий."""

    items_payload = (
        _expect_list(payload)
        if isinstance(payload, list)
        else _list(_expect_mapping(payload), "items", "result")
    )
    return JobDictionaryValuesResult(
        items=[
            JobDictionaryValue(
                id=_int(item, "id") if _int(item, "id") is not None else _str(item, "id"),
                name=_str(item, "name", "description"),
                deprecated=_bool(item, "deprecated"),
            )
            for item in items_payload
        ],
    )
