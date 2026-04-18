"""Типизированные модели раздела jobs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from avito.core.serialization import enable_module_serialization


@dataclass(slots=True, frozen=True)
class ApplicationIdsQuery:
    """Query списка идентификаторов откликов."""

    updated_at_from: str

    def to_params(self) -> dict[str, str]:
        """Сериализует query-параметры идентификаторов откликов."""

        return {"updatedAtFrom": self.updated_at_from}


@dataclass(slots=True, frozen=True)
class ApplicationIdsRequest:
    """Запрос получения откликов по идентификаторам."""

    ids: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует идентификаторы откликов."""

        return {"ids": list(self.ids)}


@dataclass(slots=True, frozen=True)
class ApplicationActionRequest:
    """Запрос действия над откликами."""

    ids: list[str]
    action: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует действие над откликами."""

        return {"ids": list(self.ids), "action": self.action}


@dataclass(slots=True, frozen=True)
class ApplicationViewedItem:
    """Флаг просмотра для отклика."""

    id: str
    is_viewed: bool

    def to_payload(self) -> dict[str, object]:
        """Сериализует флаг просмотра отклика."""

        return {"id": self.id, "is_viewed": self.is_viewed}


@dataclass(slots=True, frozen=True)
class ApplicationViewedRequest:
    """Запрос обновления флага просмотра откликов."""

    applies: list[ApplicationViewedItem]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос обновления просмотра откликов."""

        return {"applies": [item.to_payload() for item in self.applies]}


@dataclass(slots=True, frozen=True)
class JobWebhookUpdateRequest:
    """Запрос обновления webhook откликов."""

    url: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует webhook откликов."""

        return {"url": self.url}


@dataclass(slots=True, frozen=True)
class ResumeSearchQuery:
    """Query поиска резюме."""

    query: str

    def to_params(self) -> dict[str, str]:
        """Сериализует query поиска резюме."""

        return {"query": self.query}


@dataclass(slots=True, frozen=True)
class VacanciesQuery:
    """Query списка или карточки вакансий."""

    query: str | None = None

    def to_params(self) -> dict[str, str]:
        """Сериализует query вакансий."""

        params: dict[str, str] = {}
        if self.query is not None:
            params["query"] = self.query
        return params


@dataclass(slots=True, frozen=True)
class VacancyCreateRequest:
    """Запрос создания вакансии."""

    title: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует создание вакансии."""

        return {"title": self.title}


@dataclass(slots=True, frozen=True)
class VacancyUpdateRequest:
    """Запрос обновления вакансии."""

    title: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует обновление вакансии."""

        return {"title": self.title}


@dataclass(slots=True, frozen=True)
class VacancyArchiveRequest:
    """Запрос архивации вакансии v1."""

    employee_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует архивацию вакансии."""

        return {"employee_id": self.employee_id}


@dataclass(slots=True, frozen=True)
class VacancyProlongateRequest:
    """Запрос продления вакансии v1."""

    billing_type: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует продление вакансии."""

        return {"billing_type": self.billing_type}


@dataclass(slots=True, frozen=True)
class VacancyIdsRequest:
    """Запрос списка вакансий по идентификаторам."""

    ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует идентификаторы вакансий."""

        return {"ids": list(self.ids)}


@dataclass(slots=True, frozen=True)
class VacancyAutoRenewalRequest:
    """Запрос обновления автообновления вакансии."""

    auto_renewal: bool

    def to_payload(self) -> dict[str, object]:
        """Сериализует флаг автообновления."""

        return {"auto_renewal": self.auto_renewal}


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
