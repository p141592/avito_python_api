"""Типизированные модели раздела ads."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from avito.ads.enums import AdsActionStatus, AutoloadFieldType, AutoloadReportStatus, ListingStatus
from avito.core.serialization import SerializableModel


@dataclass(slots=True, frozen=True)
class Listing(SerializableModel):
    """Объявление пользователя."""

    item_id: int | None
    user_id: int | None
    title: str | None
    description: str | None
    status: ListingStatus | None
    price: float | None
    url: str | None
    category: str | None = None
    city: str | None = None
    published_at: datetime | None = None
    updated_at: datetime | None = None
    is_moderated: bool | None = None
    is_visible: bool | None = None


@dataclass(slots=True, frozen=True)
class AdsListResult(SerializableModel):
    """Результат списка объявлений."""

    items: list[Listing]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class UpdatePriceRequest:
    """Запрос изменения цены объявления."""

    price: int | float

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос смены цены."""

        return {"price": self.price}


@dataclass(slots=True, frozen=True)
class UpdatePriceResult(SerializableModel):
    """Результат обновления цены объявления."""

    item_id: int | None
    price: float | None
    status: AdsActionStatus | None


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
class CallStats(SerializableModel):
    """Статистика звонков по объявлению."""

    item_id: int | None
    calls: int | None
    answered_calls: int | None
    missed_calls: int | None


@dataclass(slots=True, frozen=True)
class CallsStatsResult(SerializableModel):
    """Статистика звонков по набору объявлений."""

    items: list[CallStats]


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
class ListingStats(SerializableModel):
    """Статистические показатели объявления."""

    item_id: int | None
    views: int | None
    contacts: int | None
    favorites: int | None


@dataclass(slots=True, frozen=True)
class ItemStatsResult(SerializableModel):
    """Статистика по списку объявлений."""

    items: list[ListingStats]


@dataclass(slots=True, frozen=True)
class ItemAnalyticsResult(SerializableModel):
    """Аналитика по профилю или объявлениям."""

    items: list[ListingStats]
    period: str | None = None


@dataclass(slots=True, frozen=True)
class SpendingRecord(SerializableModel):
    """Запись статистики расходов по объявлению."""

    item_id: int | None
    amount: float | None
    service: str | None


@dataclass(slots=True, frozen=True)
class AccountSpendings(SerializableModel):
    """Статистика расходов профиля."""

    items: list[SpendingRecord]
    total: float | None = None


@dataclass(slots=True, frozen=True)
class VasPrice(SerializableModel):
    """Цена и доступность услуги продвижения."""

    code: str | None
    title: str | None
    price: float | None
    is_available: bool | None


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
class VasPricesResult(SerializableModel):
    """Список цен и доступных услуг продвижения."""

    items: list[VasPrice]


@dataclass(slots=True, frozen=True)
class VasApplyResult(SerializableModel):
    """Результат применения услуг продвижения."""

    success: bool
    status: AdsActionStatus | None = None


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
class AutoloadProfileSettings(SerializableModel):
    """Профиль пользователя автозагрузки."""

    user_id: int | None
    is_enabled: bool | None
    upload_url: str | None


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
class UploadResult(SerializableModel):
    """Результат запуска загрузки файла."""

    success: bool
    report_id: int | None = None


@dataclass(slots=True, frozen=True)
class AutoloadField(SerializableModel):
    """Поле категории автозагрузки."""

    slug: str | None
    title: str | None
    type: AutoloadFieldType | None
    required: bool | None


@dataclass(slots=True, frozen=True)
class AutoloadFieldsResult(SerializableModel):
    """Список полей категории автозагрузки."""

    items: list[AutoloadField]


@dataclass(slots=True, frozen=True)
class AutoloadTreeNode(SerializableModel):
    """Узел дерева категорий автозагрузки."""

    slug: str | None
    title: str | None
    children: list[AutoloadTreeNode] = field(default_factory=list)


@dataclass(slots=True, frozen=True)
class AutoloadTreeResult(SerializableModel):
    """Дерево категорий автозагрузки."""

    items: list[AutoloadTreeNode]


@dataclass(slots=True, frozen=True)
class IdMappingResult(SerializableModel):
    """Сопоставление идентификаторов объявлений."""

    mappings: list[tuple[int | None, int | None]]


@dataclass(slots=True, frozen=True)
class AutoloadReportSummary(SerializableModel):
    """Краткая информация по отчету автозагрузки."""

    report_id: int | None
    status: AutoloadReportStatus | None
    created_at: datetime | None
    finished_at: datetime | None
    processed_items: int | None


@dataclass(slots=True, frozen=True)
class AutoloadReportsResult(SerializableModel):
    """Список отчетов автозагрузки."""

    items: list[AutoloadReportSummary]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class AutoloadReportItem(SerializableModel):
    """Объявление внутри отчета автозагрузки."""

    item_id: int | None
    avito_id: int | None
    status: AutoloadReportStatus | None
    title: str | None


@dataclass(slots=True, frozen=True)
class AutoloadReportItemsResult(SerializableModel):
    """Список объявлений из отчета автозагрузки."""

    items: list[AutoloadReportItem]
    total: int | None = None


@dataclass(slots=True, frozen=True)
class AutoloadFee(SerializableModel):
    """Списание по объявлению в отчете автозагрузки."""

    item_id: int | None
    amount: float | None
    service: str | None


@dataclass(slots=True, frozen=True)
class AutoloadFeesResult(SerializableModel):
    """Списания по объявлениям отчета."""

    items: list[AutoloadFee]
    total: float | None = None


@dataclass(slots=True, frozen=True)
class AutoloadReportDetails(SerializableModel):
    """Детальная информация по отчету автозагрузки."""

    report_id: int | None
    status: AutoloadReportStatus | None
    created_at: datetime | None
    finished_at: datetime | None
    errors_count: int | None
    warnings_count: int | None


@dataclass(slots=True, frozen=True)
class LegacyAutoloadReport(SerializableModel):
    """Legacy-ответ автозагрузки."""

    report_id: int | None
    status: AutoloadReportStatus | None


@dataclass(slots=True, frozen=True)
class AdsActionResult(SerializableModel):
    """Результат мутационной операции ads."""

    success: bool
    message: str | None = None


__all__ = (
    "AccountSpendings",
    "AdsActionResult",
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
    "CallStats",
    "CallsStatsRequest",
    "CallsStatsResult",
    "IdMappingResult",
    "ItemAnalyticsResult",
    "ItemStatsRequest",
    "ItemStatsResult",
    "LegacyAutoloadReport",
    "Listing",
    "ListingStats",
    "SpendingRecord",
    "UpdatePriceRequest",
    "UpdatePriceResult",
    "UploadByUrlRequest",
    "UploadResult",
    "VasApplyResult",
    "VasPrice",
    "VasPricesRequest",
    "VasPricesResult",
)
