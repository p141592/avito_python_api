"""Типизированные модели раздела jobs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class JobsRequest:
    """Унифицированный typed request для Jobs API."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует JSON payload запроса."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class JobsQuery:
    """Унифицированный typed query для Jobs API."""

    params: Mapping[str, object]

    def to_params(self) -> dict[str, object]:
        """Сериализует query-параметры запроса."""

        return dict(self.params)


@dataclass(slots=True, frozen=True)
class JobActionResult:
    """Результат mutation-операции Jobs API."""

    success: bool
    id: str | None = None
    status: str | None = None
    message: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationInfo:
    """Информация об отклике."""

    id: str | None
    vacancy_id: int | None
    resume_id: str | None
    state: str | None
    is_viewed: bool | None
    applicant_name: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationsResult:
    """Список откликов."""

    items: list[ApplicationInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationIdItem:
    """Идентификатор отклика."""

    id: str | None
    updated_at: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationIdsResult:
    """Постраничный список идентификаторов откликов."""

    items: list[ApplicationIdItem]
    cursor: str | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationState:
    """Статус отклика."""

    slug: str | None
    description: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplicationStatesResult:
    """Список возможных статусов откликов."""

    items: list[ApplicationState]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumeInfo:
    """Краткая или полная информация о резюме."""

    id: str | None
    title: str | None
    candidate_name: str | None
    location: str | None
    salary: int | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumesResult:
    """Результат поиска резюме."""

    items: list[ResumeInfo]
    cursor: str | None = None
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ResumeContactInfo:
    """Контакты соискателя."""

    name: str | None
    phone: str | None
    email: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyInfo:
    """Информация о вакансии."""

    id: str | None
    uuid: str | None
    title: str | None
    status: str | None
    url: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacanciesResult:
    """Список вакансий."""

    items: list[VacancyInfo]
    total: int | None = None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyStatusInfo:
    """Статус публикации вакансии v2."""

    id: str | None
    uuid: str | None
    status: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VacancyStatusesResult:
    """Список статусов вакансий."""

    items: list[VacancyStatusInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobWebhookInfo:
    """Подписка webhook раздела Работа."""

    url: str | None
    is_active: bool | None
    version: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobWebhooksResult:
    """Список webhook-подписок."""

    items: list[JobWebhookInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryInfo:
    """Справочник вакансий."""

    id: str | None
    description: str | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionariesResult:
    """Список доступных словарей."""

    items: list[JobDictionaryInfo]
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryValue:
    """Значение словаря вакансий."""

    id: int | str | None
    name: str | None
    deprecated: bool | None
    _payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class JobDictionaryValuesResult:
    """Список значений словаря."""

    items: list[JobDictionaryValue]
    _payload: Mapping[str, object] = field(default_factory=dict)


enable_module_serialization(globals())
