"""Типизированные модели раздела jobs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class JsonRequest:
    """Типизированная обертка над JSON payload запроса."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class JobActionResult:
    """Результат mutation-операции Jobs API."""

    success: bool
    id: str | None = None
    status: str | None = None
    message: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationInfo:
    """Информация об отклике."""

    id: str | None
    vacancy_id: int | None
    resume_id: str | None
    state: str | None
    is_viewed: bool | None
    applicant_name: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationsResult:
    """Список откликов."""

    items: list[ApplicationInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationIdItem:
    """Идентификатор отклика."""

    id: str | None
    updated_at: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationIdsResult:
    """Постраничный список идентификаторов откликов."""

    items: list[ApplicationIdItem]
    cursor: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationState:
    """Статус отклика."""

    slug: str | None
    description: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationStatesResult:
    """Список возможных статусов откликов."""

    items: list[ApplicationState]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumeInfo:
    """Краткая или полная информация о резюме."""

    id: str | None
    title: str | None
    candidate_name: str | None
    location: str | None
    salary: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumesResult:
    """Результат поиска резюме."""

    items: list[ResumeInfo]
    cursor: str | None = None
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumeContactInfo:
    """Контакты соискателя."""

    name: str | None
    phone: str | None
    email: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyInfo:
    """Информация о вакансии."""

    id: str | None
    uuid: str | None
    title: str | None
    status: str | None
    url: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacanciesResult:
    """Список вакансий."""

    items: list[VacancyInfo]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyStatusInfo:
    """Статус публикации вакансии v2."""

    id: str | None
    uuid: str | None
    status: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyStatusesResult:
    """Список статусов вакансий."""

    items: list[VacancyStatusInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobWebhookInfo:
    """Подписка webhook раздела Работа."""

    url: str | None
    is_active: bool | None
    version: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobWebhooksResult:
    """Список webhook-подписок."""

    items: list[JobWebhookInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryInfo:
    """Справочник вакансий."""

    id: str | None
    description: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionariesResult:
    """Список доступных словарей."""

    items: list[JobDictionaryInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryValue:
    """Значение словаря вакансий."""

    id: int | str | None
    name: str | None
    deprecated: bool | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryValuesResult:
    """Список значений словаря."""

    items: list[JobDictionaryValue]
    raw_payload: Mapping[str, object] = field(default_factory=dict)
