"""Типизированные модели раздела ads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AdItem:
    """Объявление пользователя."""

    id: int | None
    user_id: int | None
    title: str | None
    description: str | None
    status: str | None
    price: float | None
    url: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AdsListResult:
    """Результат списка объявлений."""

    items: list[AdItem]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class UpdatePriceRequest:
    """Запрос изменения цены объявления."""

    price: int | float

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос смены цены."""

        return {"price": self.price}


@dataclass(slots=True, frozen=True)
class UpdatePriceResult:
    """Результат обновления цены объявления."""

    item_id: int | None
    price: float | None
    status: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CallsStatsRequest:
    """Запрос статистики звонков."""

    item_ids: list[int] = field(default_factory=list)
    date_from: str | None = None
    date_to: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует фильтр статистики звонков."""

        return {
            key: value
            for key, value in {
                "itemIds": self.item_ids or None,
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class CallStat:
    """Статистика звонков по объявлению."""

    item_id: int | None
    calls: int | None
    answered_calls: int | None
    missed_calls: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CallsStatsResult:
    """Статистика звонков по набору объявлений."""

    items: list[CallStat]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ItemStatsRequest:
    """Запрос статистики по объявлениям."""

    item_ids: list[int]
    date_from: str | None = None
    date_to: str | None = None
    fields: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статистики."""

        return {
            key: value
            for key, value in {
                "itemIds": self.item_ids,
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
                "fields": self.fields or None,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class ItemStatsRecord:
    """Статистические показатели объявления."""

    item_id: int | None
    views: int | None
    contacts: int | None
    favorites: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ItemStatsResult:
    """Статистика по списку объявлений."""

    items: list[ItemStatsRecord]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ItemAnalyticsResult:
    """Аналитика по профилю или объявлениям."""

    items: list[ItemStatsRecord]
    period: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class SpendingRecord:
    """Запись статистики расходов."""

    item_id: int | None
    amount: float | None
    service: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class SpendingsResult:
    """Статистика расходов профиля."""

    items: list[SpendingRecord]
    total: float | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VasPrice:
    """Цена и доступность услуги продвижения."""

    code: str | None
    title: str | None
    price: float | None
    is_available: bool | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VasPricesRequest:
    """Запрос цен продвижения."""

    item_ids: list[int]
    location_id: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос цен VAS."""

        return {
            key: value
            for key, value in {
                "itemIds": self.item_ids,
                "locationId": self.location_id,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class VasPricesResult:
    """Список цен и доступных услуг продвижения."""

    items: list[VasPrice]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class VasApplyResult:
    """Результат применения услуг продвижения."""

    success: bool
    status: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApplyVasRequest:
    """Запрос применения услуг продвижения."""

    codes: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос применения VAS."""

        return {"codes": self.codes}


@dataclass(slots=True, frozen=True)
class ApplyVasPackageRequest:
    """Запрос применения пакета услуг продвижения."""

    package_code: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос применения пакета VAS."""

        return {"packageCode": self.package_code}


@dataclass(slots=True, frozen=True)
class AutoloadProfileSettings:
    """Профиль пользователя автозагрузки."""

    user_id: int | None
    is_enabled: bool | None
    upload_url: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadProfileUpdateRequest:
    """Запрос сохранения профиля автозагрузки."""

    is_enabled: bool | None = None
    email: str | None = None
    callback_url: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует изменения профиля."""

        return {
            key: value
            for key, value in {
                "isEnabled": self.is_enabled,
                "email": self.email,
                "callbackUrl": self.callback_url,
            }.items()
            if value is not None
        }


@dataclass(slots=True, frozen=True)
class UploadByUrlRequest:
    """Запрос загрузки файла по ссылке."""

    url: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует ссылку на файл автозагрузки."""

        return {"url": self.url}


@dataclass(slots=True, frozen=True)
class UploadResult:
    """Результат запуска загрузки файла."""

    success: bool
    report_id: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadField:
    """Поле категории автозагрузки."""

    slug: str | None
    title: str | None
    type: str | None
    required: bool | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadFieldsResult:
    """Список полей категории автозагрузки."""

    items: list[AutoloadField]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadTreeNode:
    """Узел дерева категорий автозагрузки."""

    slug: str | None
    title: str | None
    children: list[AutoloadTreeNode] = field(default_factory=list)
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadTreeResult:
    """Дерево категорий автозагрузки."""

    items: list[AutoloadTreeNode]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class IdMappingResult:
    """Сопоставление идентификаторов объявлений."""

    mappings: list[tuple[int | None, int | None]]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadReportSummary:
    """Краткая информация по отчету автозагрузки."""

    report_id: int | None
    status: str | None
    created_at: str | None
    finished_at: str | None
    processed_items: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadReportsResult:
    """Список отчетов автозагрузки."""

    items: list[AutoloadReportSummary]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadReportItem:
    """Объявление внутри отчета автозагрузки."""

    item_id: int | None
    avito_id: int | None
    status: str | None
    title: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadReportItemsResult:
    """Список объявлений из отчета автозагрузки."""

    items: list[AutoloadReportItem]
    total: int | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadFee:
    """Списание по объявлению в отчете автозагрузки."""

    item_id: int | None
    amount: float | None
    service: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadFeesResult:
    """Списания по объявлениям отчета."""

    items: list[AutoloadFee]
    total: float | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutoloadReportDetails:
    """Детальная информация по отчету автозагрузки."""

    report_id: int | None
    status: str | None
    created_at: str | None
    finished_at: str | None
    errors_count: int | None
    warnings_count: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LegacyAutoloadReport:
    """Legacy-ответ автозагрузки."""

    report_id: int | None
    status: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ActionResult:
    """Универсальный результат мутационной операции ads."""

    success: bool
    message: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


__all__ = (
    "ActionResult",
    "AdItem",
    "AdsListResult",
    "ApplyVasPackageRequest",
    "ApplyVasRequest",
    "AutoloadFee",
    "AutoloadFeesResult",
    "AutoloadField",
    "AutoloadFieldsResult",
    "AutoloadProfileSettings",
    "AutoloadProfileUpdateRequest",
    "AutoloadReportDetails",
    "AutoloadReportItem",
    "AutoloadReportItemsResult",
    "AutoloadReportSummary",
    "AutoloadReportsResult",
    "AutoloadTreeNode",
    "AutoloadTreeResult",
    "CallStat",
    "CallsStatsRequest",
    "CallsStatsResult",
    "IdMappingResult",
    "ItemAnalyticsResult",
    "ItemStatsRecord",
    "ItemStatsRequest",
    "ItemStatsResult",
    "LegacyAutoloadReport",
    "SpendingRecord",
    "SpendingsResult",
    "UpdatePriceRequest",
    "UpdatePriceResult",
    "UploadByUrlRequest",
    "UploadResult",
    "VasApplyResult",
    "VasPrice",
    "VasPricesRequest",
    "VasPricesResult",
)
