"""Типизированные модели раздела jobs."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core.serialization import SerializableModel


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
class JobActionResult(SerializableModel):
    """Результат mutation-операции Jobs API."""

    success: bool
    id: str | None = None
    status: str | None = None
    message: str | None = None


@dataclass(slots=True, frozen=True)
class ApplicationInfo(SerializableModel):
    """Информация об отклике."""

    id: str | None
    vacancy_id: int | None
    resume_id: str | None
    state: str | None
    is_viewed: bool | None
    applicant_name: str | None


@dataclass(slots=True, frozen=True)
class ApplicationsResult(SerializableModel):
    """Список откликов."""

    items: list[ApplicationInfo]


@dataclass(slots=True, frozen=True)
class ApplicationIdItem(SerializableModel):
    """Идентификатор отклика."""

    id: str | None
    updated_at: str | None


@dataclass(slots=True, frozen=True)
class ApplicationIdsResult(SerializableModel):
    """Постраничный список идентификаторов откликов."""

    items: list[ApplicationIdItem]
    cursor: str | None = None


@dataclass(slots=True, frozen=True)
class ApplicationState(SerializableModel):
    """Статус отклика."""

    slug: str | None
    description: str | None


@dataclass(slots=True, frozen=True)
class ApplicationStatesResult(SerializableModel):
    """Список возможных статусов откликов."""

    items: list[ApplicationState]


@dataclass(slots=True, frozen=True)
class ResumeInfo(SerializableModel):
    """Краткая или полная информация о резюме."""

    id: str | None
    title: str | None
    candidate_name: str | None
    location: str | None
    salary: int | None


@dataclass(slots=True, frozen=True)
class ResumesResult(SerializableModel):
    """Результат поиска резюме."""

    items: list[ResumeInfo]
    cursor: str | None = None
    total: int | None = None


@dataclass(slots=True, frozen=True)
class ResumeContactInfo(SerializableModel):
    """Контакты соискателя."""

    name: str | None
    phone: str | None
    email: str | None


@dataclass(slots=True, frozen=True)
class VacancyInfo(SerializableModel):
    """Информация о вакансии."""

    id: str | None
    uuid: str | None
    title: str | None
    status: str | None
    url: str | None


@dataclass(slots=True, frozen=True)
class VacanciesResult(SerializableModel):
    """Список вакансий."""

    items: list[VacancyInfo]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class VacancyStatusInfo(SerializableModel):
    """Статус публикации вакансии v2."""

    id: str | None
    uuid: str | None
    status: str | None


@dataclass(slots=True, frozen=True)
class VacancyStatusesResult(SerializableModel):
    """Список статусов вакансий."""

    items: list[VacancyStatusInfo]


@dataclass(slots=True, frozen=True)
class JobWebhookInfo(SerializableModel):
    """Подписка webhook раздела Работа."""

    url: str | None
    is_active: bool | None
    version: str | None


@dataclass(slots=True, frozen=True)
class JobWebhooksResult(SerializableModel):
    """Список webhook-подписок."""

    items: list[JobWebhookInfo]


@dataclass(slots=True, frozen=True)
class JobDictionaryInfo(SerializableModel):
    """Справочник вакансий."""

    id: str | None
    description: str | None


@dataclass(slots=True, frozen=True)
class JobDictionariesResult(SerializableModel):
    """Список доступных словарей."""

    items: list[JobDictionaryInfo]


@dataclass(slots=True, frozen=True)
class JobDictionaryValue(SerializableModel):
    """Значение словаря вакансий."""

    id: int | str | None
    name: str | None
    deprecated: bool | None


@dataclass(slots=True, frozen=True)
class JobDictionaryValuesResult(SerializableModel):
    """Список значений словаря."""

    items: list[JobDictionaryValue]
