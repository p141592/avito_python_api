"""Мапперы JSON -> dataclass для пакета ads."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

from avito.ads.enums import AdsActionStatus, AutoloadFieldType, AutoloadReportStatus, ListingStatus
from avito.ads.models import (
    AccountSpendings,
    AdsActionResult,
    AdsListResult,
    AutoloadFee,
    AutoloadFeesResult,
    AutoloadField,
    AutoloadFieldsResult,
    AutoloadProfileSettings,
    AutoloadReportDetails,
    AutoloadReportItem,
    AutoloadReportItemsResult,
    AutoloadReportsResult,
    AutoloadReportSummary,
    AutoloadTreeNode,
    AutoloadTreeResult,
    CallsStatsResult,
    CallStats,
    IdMappingResult,
    ItemAnalyticsResult,
    ItemStatsResult,
    LegacyAutoloadReport,
    Listing,
    ListingStats,
    SpendingRecord,
    UpdatePriceResult,
    UploadResult,
    VasApplyResult,
    VasPrice,
    VasPricesResult,
)
from avito.core.enums import map_enum_or_unknown
from avito.core.exceptions import ResponseMappingError

Payload = Mapping[str, object]


def _expect_mapping(payload: object) -> Payload:
    if not isinstance(payload, Mapping):
        raise ResponseMappingError("Ожидался JSON-объект.", payload=payload)
    return cast(Payload, payload)


def _list(payload: Payload, *keys: str) -> list[Payload]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _mapping(payload: Payload, *keys: str) -> Payload | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return None


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _nested_str(payload: Payload, *keys: str) -> str | None:
    value = _str(payload, *keys)
    if value is not None:
        return value
    for key in keys:
        nested = _mapping(payload, key)
        if nested is None:
            continue
        nested_value = _str(nested, "value", "name", "title", "slug", "status")
        if nested_value is not None:
            return nested_value
    return None


def _datetime(payload: Payload, *keys: str) -> datetime | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            normalized = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(normalized)
            except ValueError:
                continue
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _float(payload: Payload, *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, Mapping):
            nested = cast(Payload, value)
            nested_value = _float(nested, "value", "amount", "current", "price")
            if nested_value is not None:
                return nested_value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def _visibility(payload: Payload) -> bool | None:
    visible = _bool(payload, "is_visible", "isVisible", "visible")
    if visible is not None:
        return visible
    status = _nested_str(payload, "status")
    if status is None:
        return None
    return status in {"active", "published", "visible"}


def map_ad_item(payload: object) -> Listing:
    """Преобразует объявление в dataclass."""

    data = _expect_mapping(payload)
    source = _mapping(data, "item", "resource", "listing", "ad") or data
    return Listing(
        item_id=_int(source, "id", "item_id", "itemId", "itemID"),
        user_id=_int(source, "user_id", "userId"),
        title=_str(source, "title", "name"),
        description=_str(source, "description", "descriptionHtml"),
        status=map_enum_or_unknown(
            _nested_str(source, "status", "state"),
            ListingStatus,
            enum_name="ads.listing_status",
        ),
        price=_float(source, "price"),
        url=_str(source, "url", "link", "uri"),
        category=_nested_str(source, "category", "categoryName"),
        city=_nested_str(source, "city", "location"),
        published_at=_datetime(source, "published_at", "publishedAt", "created_at", "createdAt"),
        updated_at=_datetime(source, "updated_at", "updatedAt"),
        is_moderated=_bool(source, "is_moderated", "isModerated", "moderated"),
        is_visible=_visibility(source),
    )


def map_ads_list(payload: object) -> AdsListResult:
    """Преобразует список объявлений в dataclass."""

    data = _expect_mapping(payload)
    items = [map_ad_item(item) for item in _list(data, "items", "result", "resources")]
    meta = _mapping(data, "meta")
    total = _int(data, "total", "count")
    if total is None and meta is not None:
        total = _int(meta, "total", "count")
    return AdsListResult(items=items, total=total)


def map_update_price_result(payload: object) -> UpdatePriceResult:
    """Преобразует результат обновления цены."""

    data = _expect_mapping(payload)
    return UpdatePriceResult(
        item_id=_int(data, "item_id", "itemId", "id"),
        price=_float(data, "price"),
        status=map_enum_or_unknown(
            _str(data, "status", "result"),
            AdsActionStatus,
            enum_name="ads.action_status",
        ),
    )


def map_calls_stats(payload: object) -> CallsStatsResult:
    """Преобразует статистику звонков."""

    data = _expect_mapping(payload)
    items = [
        CallStats(
            item_id=_int(item, "item_id", "itemId", "id"),
            calls=_int(item, "calls", "total"),
            answered_calls=_int(item, "answered_calls", "answeredCalls"),
            missed_calls=_int(item, "missed_calls", "missedCalls"),
        )
        for item in _list(data, "items", "result", "stats")
    ]
    return CallsStatsResult(items=items)


def _map_item_stat(item: Payload) -> ListingStats:
    return ListingStats(
        item_id=_int(item, "item_id", "itemId", "id"),
        views=_int(item, "views", "impressions"),
        contacts=_int(item, "contacts", "contacts_total", "contactsTotal"),
        favorites=_int(item, "favorites", "favorites_total", "favoritesTotal"),
    )


def map_item_stats(payload: object) -> ItemStatsResult:
    """Преобразует статистику по списку объявлений."""

    data = _expect_mapping(payload)
    return ItemStatsResult(
        items=[_map_item_stat(item) for item in _list(data, "items", "result", "stats")],
    )


def map_item_analytics(payload: object) -> ItemAnalyticsResult:
    """Преобразует расширенную аналитику по объявлениям."""

    data = _expect_mapping(payload)
    return ItemAnalyticsResult(
        items=[_map_item_stat(item) for item in _list(data, "items", "result", "stats")],
        period=_str(data, "period"),
    )


def map_spendings(payload: object) -> AccountSpendings:
    """Преобразует статистику расходов."""

    data = _expect_mapping(payload)
    items = [
        SpendingRecord(
            item_id=_int(item, "item_id", "itemId", "id"),
            amount=_float(item, "amount", "price", "cost"),
            service=_str(item, "service", "serviceType", "type"),
        )
        for item in _list(data, "items", "result", "spendings")
    ]
    total = _float(data, "total")
    if total is None:
        total = sum(item.amount for item in items if item.amount is not None) or None
    return AccountSpendings(items=items, total=total)


def map_vas_prices(payload: object) -> VasPricesResult:
    """Преобразует список доступных услуг продвижения."""

    data = _expect_mapping(payload)
    items = [
        VasPrice(
            code=_str(item, "code", "slug", "type"),
            title=_str(item, "title", "name"),
            price=_float(item, "price", "amount"),
            is_available=_bool(item, "is_available", "isAvailable", "available"),
        )
        for item in _list(data, "items", "services", "result")
    ]
    return VasPricesResult(items=items)


def map_vas_apply_result(payload: object) -> VasApplyResult:
    """Преобразует результат применения продвижения."""

    data = _expect_mapping(payload)
    return VasApplyResult(
        success=bool(data.get("success", True)),
        status=map_enum_or_unknown(
            _str(data, "status", "result", "message"),
            AdsActionStatus,
            enum_name="ads.action_status",
        ),
    )


def map_autoload_profile(payload: object) -> AutoloadProfileSettings:
    """Преобразует профиль автозагрузки."""

    data = _expect_mapping(payload)
    return AutoloadProfileSettings(
        user_id=_int(data, "user_id", "userId", "id"),
        is_enabled=_bool(data, "is_enabled", "isEnabled", "enabled"),
        upload_url=_str(data, "upload_url", "uploadUrl", "url"),
    )


def map_upload_result(payload: object) -> UploadResult:
    """Преобразует результат загрузки файла."""

    data = _expect_mapping(payload)
    return UploadResult(
        success=bool(data.get("success", True)),
        report_id=_int(data, "report_id", "reportId", "id"),
    )


def map_autoload_fields(payload: object) -> AutoloadFieldsResult:
    """Преобразует список полей категории."""

    data = _expect_mapping(payload)
    items = [
        AutoloadField(
            slug=_str(item, "slug", "code", "id"),
            title=_str(item, "title", "name"),
            type=map_enum_or_unknown(
                _str(item, "type"),
                AutoloadFieldType,
                enum_name="ads.autoload_field_type",
            ),
            required=_bool(item, "required", "is_required", "isRequired"),
        )
        for item in _list(data, "fields", "items", "result")
    ]
    return AutoloadFieldsResult(items=items)


def _map_tree_node(payload: Payload) -> AutoloadTreeNode:
    return AutoloadTreeNode(
        slug=_str(payload, "slug", "code", "id"),
        title=_str(payload, "title", "name"),
        children=[_map_tree_node(item) for item in _list(payload, "children", "items")],
    )


def map_autoload_tree(payload: object) -> AutoloadTreeResult:
    """Преобразует дерево категорий."""

    data = _expect_mapping(payload)
    items = [_map_tree_node(item) for item in _list(data, "tree", "items", "result")]
    return AutoloadTreeResult(items=items)


def map_id_mapping(payload: object) -> IdMappingResult:
    """Преобразует ответ с сопоставлением идентификаторов."""

    data = _expect_mapping(payload)
    mappings: list[tuple[int | None, int | None]] = []
    for item in _list(data, "items", "result", "mappings"):
        mappings.append((_int(item, "ad_id", "adId"), _int(item, "avito_id", "avitoId")))
    return IdMappingResult(mappings=mappings)


def _map_report_summary(item: Payload) -> AutoloadReportSummary:
    return AutoloadReportSummary(
        report_id=_int(item, "report_id", "reportId", "id"),
        status=map_enum_or_unknown(
            _str(item, "status"),
            AutoloadReportStatus,
            enum_name="ads.autoload_report_status",
        ),
        created_at=_datetime(item, "created_at", "createdAt"),
        finished_at=_datetime(item, "finished_at", "finishedAt"),
        processed_items=_int(item, "processed_items", "processedItems", "items"),
    )


def map_autoload_reports(payload: object) -> AutoloadReportsResult:
    """Преобразует список отчетов автозагрузки."""

    data = _expect_mapping(payload)
    return AutoloadReportsResult(
        items=[_map_report_summary(item) for item in _list(data, "reports", "items", "result")],
        total=_int(data, "total", "count"),
    )


def map_autoload_report_details(payload: object) -> AutoloadReportDetails:
    """Преобразует детализацию отчета автозагрузки."""

    data = _expect_mapping(payload)
    return AutoloadReportDetails(
        report_id=_int(data, "report_id", "reportId", "id"),
        status=map_enum_or_unknown(
            _str(data, "status"),
            AutoloadReportStatus,
            enum_name="ads.autoload_report_status",
        ),
        created_at=_datetime(data, "created_at", "createdAt"),
        finished_at=_datetime(data, "finished_at", "finishedAt"),
        errors_count=_int(data, "errors_count", "errorsCount"),
        warnings_count=_int(data, "warnings_count", "warningsCount"),
    )


def map_legacy_autoload_report(payload: object) -> LegacyAutoloadReport:
    """Преобразует legacy-ответ отчета автозагрузки."""

    data = _expect_mapping(payload)
    return LegacyAutoloadReport(
        report_id=_int(data, "report_id", "reportId", "id"),
        status=map_enum_or_unknown(
            _str(data, "status"),
            AutoloadReportStatus,
            enum_name="ads.autoload_report_status",
        ),
    )


def map_autoload_report_items(payload: object) -> AutoloadReportItemsResult:
    """Преобразует список объявлений отчета."""

    data = _expect_mapping(payload)
    items = [
        AutoloadReportItem(
            item_id=_int(item, "item_id", "itemId", "id"),
            avito_id=_int(item, "avito_id", "avitoId"),
            status=map_enum_or_unknown(
                _str(item, "status"),
                AutoloadReportStatus,
                enum_name="ads.autoload_report_status",
            ),
            title=_str(item, "title"),
        )
        for item in _list(data, "items", "result")
    ]
    return AutoloadReportItemsResult(items=items, total=_int(data, "total", "count"))


def map_autoload_fees(payload: object) -> AutoloadFeesResult:
    """Преобразует списания по объявлениям отчета."""

    data = _expect_mapping(payload)
    items = [
        AutoloadFee(
            item_id=_int(item, "item_id", "itemId", "id"),
            amount=_float(item, "amount", "price", "cost"),
            service=_str(item, "service", "serviceType", "type"),
        )
        for item in _list(data, "items", "result", "fees")
    ]
    total = _float(data, "total")
    if total is None:
        total = sum(item.amount for item in items if item.amount is not None) or None
    return AutoloadFeesResult(items=items, total=total)


def map_action_result(payload: object) -> AdsActionResult:
    """Преобразует ответ мутационной операции ads."""

    if isinstance(payload, Mapping):
        data = cast(Payload, payload)
        return AdsActionResult(
            success=bool(data.get("success", True)),
            message=_str(data, "message"),
        )
    return AdsActionResult(success=True)


__all__ = (
    "map_action_result",
    "map_ad_item",
    "map_ads_list",
    "map_autoload_fees",
    "map_autoload_fields",
    "map_autoload_profile",
    "map_autoload_report_details",
    "map_autoload_report_items",
    "map_autoload_reports",
    "map_autoload_tree",
    "map_calls_stats",
    "map_id_mapping",
    "map_item_analytics",
    "map_item_stats",
    "map_legacy_autoload_report",
    "map_spendings",
    "map_update_price_result",
    "map_upload_result",
    "map_vas_apply_result",
    "map_vas_prices",
)
