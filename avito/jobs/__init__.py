"""Пакет jobs."""

from avito.jobs.domain import Application, DomainObject, JobDictionary, JobWebhook, Resume, Vacancy
from avito.jobs.models import (
    ApplicationIdsResult,
    ApplicationsResult,
    ApplicationStatesResult,
    JobActionResult,
    JobDictionariesResult,
    JobDictionaryValuesResult,
    JobWebhookInfo,
    JobWebhooksResult,
    ResumeContactInfo,
    ResumeInfo,
    ResumesResult,
    VacanciesResult,
    VacancyInfo,
    VacancyStatusesResult,
)

__all__ = (
    "Application",
    "ApplicationIdsResult",
    "ApplicationsResult",
    "ApplicationStatesResult",
    "DomainObject",
    "JobActionResult",
    "JobDictionariesResult",
    "JobDictionary",
    "JobDictionaryValuesResult",
    "JobWebhook",
    "JobWebhookInfo",
    "JobWebhooksResult",
    "Resume",
    "ResumeContactInfo",
    "ResumeInfo",
    "ResumesResult",
    "VacanciesResult",
    "Vacancy",
    "VacancyInfo",
    "VacancyStatusesResult",
)
