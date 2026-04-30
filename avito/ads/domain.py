"""Доменные объекты пакета ads."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import cast

from avito.ads.models import (
    AccountSpendings,
    AdsActionResult,
    AdsListResult,
    ApplyVasPackageRequest,
    ApplyVasRequest,
    AutoloadFeesResult,
    AutoloadFieldsResult,
    AutoloadProfileSettings,
    AutoloadProfileUpdateRequest,
    AutoloadReportDetails,
    AutoloadReportItemsResult,
    AutoloadReportsResult,
    AutoloadReportSummary,
    AutoloadTreeResult,
    CallsStatsRequest,
    CallsStatsResult,
    IdMappingResult,
    ItemAnalyticsResult,
    ItemStatsRequest,
    ItemStatsResult,
    LegacyAutoloadReport,
    Listing,
    ListingStatus,
    UpdatePriceRequest,
    UpdatePriceResult,
    UploadByUrlRequest,
    UploadResult,
    VasPricesRequest,
    VasPricesResult,
)
from avito.ads.operations import (
    APPLY_ITEM_VAS,
    APPLY_ITEM_VAS_PACKAGE,
    APPLY_VAS_DIRECT,
    GET_ACCOUNT_SPENDINGS,
    GET_AD_IDS_BY_AVITO_IDS,
    GET_ARCHIVE_LAST_COMPLETED_REPORT,
    GET_ARCHIVE_PROFILE,
    GET_ARCHIVE_REPORT,
    GET_AUTOLOAD_ITEMS_INFO,
    GET_AUTOLOAD_LAST_COMPLETED_REPORT,
    GET_AUTOLOAD_NODE_FIELDS,
    GET_AUTOLOAD_PROFILE,
    GET_AUTOLOAD_REPORT,
    GET_AUTOLOAD_REPORT_FEES,
    GET_AUTOLOAD_REPORT_ITEMS,
    GET_AUTOLOAD_TREE,
    GET_AVITO_IDS_BY_AD_IDS,
    GET_CALLS_STATS,
    GET_ITEM,
    GET_ITEM_ANALYTICS,
    GET_ITEM_STATS,
    GET_VAS_PRICES,
    LIST_AUTOLOAD_REPORTS,
    LIST_ITEMS,
    SAVE_ARCHIVE_PROFILE,
    SAVE_AUTOLOAD_PROFILE,
    UPDATE_PRICE,
    UPLOAD_BY_URL,
)
from avito.core import JsonPage, PaginatedList, Paginator, ValidationError
from avito.core.deprecation import deprecated_method
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.core.validation import (
    validate_non_empty_string,
    validate_string_items,
)
from avito.promotion.models import PromotionActionResult, PromotionStatus


def _preview_result(
    *,
    action: str,
    target: dict[str, object],
    request_payload: dict[str, object],
) -> PromotionActionResult:
    return PromotionActionResult(
        action=action,
        target=target,
        status=PromotionStatus.PREVIEW,
        applied=False,
        request_payload=request_payload,
        details={"validated": True},
    )


StatsDate = date | datetime | str


def _serialize_stats_date(value: StatsDate | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    normalized = value.strip()
    if not normalized:
        raise ValidationError("Дата статистики не должна быть пустой строкой.")
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        try:
            return date.fromisoformat(normalized).isoformat()
        except ValueError as exc:
            raise ValidationError("Дата статистики должна быть в ISO-формате.") from exc


def _bounded_total(total: int | None, max_items: int | None) -> int | None:
    if max_items is None:
        return total
    if total is None:
        return None
    return min(total, max_items)


def _has_next_ads_page(
    *,
    page_item_count: int,
    collected_count: int,
    page_size: int,
    total: int | None,
    max_items: int | None,
    already_collected: int,
) -> bool:
    if page_item_count == 0 or page_size <= 0:
        return False
    if max_items is not None and already_collected + collected_count >= max_items:
        return False
    if total is not None:
        return already_collected + collected_count < min(total, max_items or total)
    return page_item_count >= page_size


@dataclass(slots=True, frozen=True)
class Ad(DomainObject):
    """Доменный объект объявления."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "ad"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/core/v1/accounts/{user_id}/items/{item_id}",
        spec="Объявления.json",
        operation_id="getItemInfo",
    )
    def get(self) -> Listing:
        """Получает объявление по `item_id`.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        item_id, user_id = self._require_ids()
        return self._execute(
            GET_ITEM,
            path_params={"user_id": user_id, "item_id": item_id},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/core/v1/items",
        spec="Объявления.json",
        operation_id="getItemsInfo",
    )
    def list(
        self,
        *,
        status: ListingStatus | str | None = None,
        limit: int | None = None,
        page_size: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[Listing]:
        """Получает список объявлений.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._resolve_user_id(self.user_id)
        resolved_page_size = page_size or limit
        start_offset = offset or 0
        first_page_number = (
            start_offset // resolved_page_size + 1
            if resolved_page_size is not None and resolved_page_size > 0
            else 1
        )
        result = self._execute(
            LIST_ITEMS,
            query={
                "user_id": user_id,
                "status": status,
                "per_page": resolved_page_size,
                "page": first_page_number,
            },
        )
        list_result = cast(AdsListResult, result)
        page_size = (
            resolved_page_size
            if resolved_page_size and resolved_page_size > 0
            else len(list_result.items)
        )
        max_items = limit if limit is not None and limit >= 0 else None
        page_offset = start_offset % page_size if page_size > 0 else 0
        available_items = list_result.items[page_offset:]
        first_items = available_items[:max_items] if max_items is not None else available_items
        first_page = JsonPage(
            items=list(first_items),
            total=_bounded_total(list_result.total, max_items),
            source_total=list_result.total,
            page=first_page_number,
            per_page=page_size if page_size > 0 else None,
            has_next_page=_has_next_ads_page(
                page_item_count=len(list_result.items),
                collected_count=len(first_items),
                page_size=page_size,
                total=list_result.total,
                max_items=max_items,
                already_collected=0,
            ),
        )
        return Paginator(
            lambda page, cursor: self._fetch_ads_page(
                page=page,
                user_id=user_id,
                status=status,
                page_size=page_size,
                max_items=max_items,
                first_page_number=first_page_number,
            )
        ).as_list(start_page=first_page_number, first_page=first_page)

    @swagger_operation(
        "POST",
        "/core/v1/items/{item_id}/update_price",
        spec="Объявления.json",
        operation_id="updatePrice",
        method_args={"price": "body.price"},
    )
    def update_price(
        self,
        *,
        price: int | float,
        idempotency_key: str | None = None,
    ) -> UpdatePriceResult:
        """Обновляет цену текущего объявления.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        item_id = self._require_item_id()
        return self._execute(
            UPDATE_PRICE,
            path_params={"item_id": item_id},
            request=UpdatePriceRequest(price=price),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    def _fetch_ads_page(
        self,
        *,
        page: int | None,
        user_id: int | None,
        status: ListingStatus | str | None,
        page_size: int,
        max_items: int | None,
        first_page_number: int,
    ) -> JsonPage[Listing]:
        if page is None:
            raise ValidationError("Для операции требуется `page`.")

        already_collected = max(page - first_page_number, 0) * page_size
        remaining = max_items - already_collected if max_items is not None else None
        if remaining is not None and remaining <= 0:
            return JsonPage(items=[], total=max_items, page=page, per_page=page_size)
        result = self._execute(
            LIST_ITEMS,
            query={
                "user_id": user_id,
                "status": status,
                "per_page": min(page_size, remaining) if remaining is not None else page_size,
                "page": page,
            },
        )
        list_result = cast(AdsListResult, result)
        items = list_result.items[:remaining] if remaining is not None else list_result.items
        return JsonPage(
            items=list(items),
            total=_bounded_total(list_result.total, max_items),
            source_total=list_result.total,
            page=page,
            per_page=page_size,
            has_next_page=_has_next_ads_page(
                page_item_count=len(list_result.items),
                collected_count=len(items),
                page_size=page_size,
                total=list_result.total,
                max_items=max_items,
                already_collected=already_collected,
            ),
        )

    def _require_item_id(self) -> int:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id)

    def _require_ids(self) -> tuple[int, int]:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id), self._resolve_user_id(self.user_id)


@dataclass(slots=True, frozen=True)
class AdStats(DomainObject):
    """Доменный объект статистики объявлений."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "ad_stats"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/core/v1/accounts/{user_id}/calls/stats",
        spec="Объявления.json",
        operation_id="postCallsStats",
    )
    def get_calls_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: StatsDate | None = None,
        date_to: StatsDate | None = None,
    ) -> CallsStatsResult:
        """Получает статистику звонков.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or ([int(self.item_id)] if self.item_id is not None else [])
        return self._execute(
            GET_CALLS_STATS,
            path_params={"user_id": user_id},
            request=CallsStatsRequest(
                item_ids=resolved_item_ids,
                date_from=_serialize_stats_date(date_from),
                date_to=_serialize_stats_date(date_to),
            ),
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/stats/v1/accounts/{user_id}/items",
        spec="Объявления.json",
        operation_id="itemStatsShallow",
    )
    def get_item_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: StatsDate | None = None,
        date_to: StatsDate | None = None,
        fields: list[str] | None = None,
    ) -> ItemStatsResult:
        """Получает статистику по списку объявлений.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or ([int(self.item_id)] if self.item_id is not None else [])
        return self._execute(
            GET_ITEM_STATS,
            path_params={"user_id": user_id},
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=_serialize_stats_date(date_from),
                date_to=_serialize_stats_date(date_to),
                fields=fields or [],
            ),
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/stats/v2/accounts/{user_id}/items",
        spec="Объявления.json",
        operation_id="itemAnalytics",
    )
    def get_item_analytics(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: StatsDate | None = None,
        date_to: StatsDate | None = None,
        fields: list[str] | None = None,
    ) -> ItemAnalyticsResult:
        """Получает аналитику по профилю.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or ([int(self.item_id)] if self.item_id is not None else [])
        return self._execute(
            GET_ITEM_ANALYTICS,
            path_params={"user_id": user_id},
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=_serialize_stats_date(date_from),
                date_to=_serialize_stats_date(date_to),
                fields=fields or [],
            ),
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/stats/v2/accounts/{user_id}/spendings",
        spec="Объявления.json",
        operation_id="accountSpendings",
    )
    def get_account_spendings(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: StatsDate | None = None,
        date_to: StatsDate | None = None,
        fields: list[str] | None = None,
    ) -> AccountSpendings:
        """Получает статистику расходов профиля.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or ([int(self.item_id)] if self.item_id is not None else [])
        return self._execute(
            GET_ACCOUNT_SPENDINGS,
            path_params={"user_id": user_id},
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=_serialize_stats_date(date_from),
                date_to=_serialize_stats_date(date_to),
                fields=fields or [],
            ),
        )  # type: ignore[return-value]

    def _require_user_id(self) -> int:
        return self._resolve_user_id(self.user_id)


@dataclass(slots=True, frozen=True)
class AdPromotion(DomainObject):
    """Доменный объект продвижения объявления."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "ad_promotion"
    __sdk_factory_args__ = {"item_id": "path.item_id", "user_id": "path.user_id"}

    item_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/core/v1/accounts/{user_id}/vas/prices",
        spec="Объявления.json",
        operation_id="vasPrices",
        method_args={"item_ids": "body.item_ids"},
    )
    def get_vas_prices(
        self, *, item_ids: list[int], location_id: int | None = None
    ) -> VasPricesResult:
        """Получает цены продвижения и доступные услуги.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        user_id = self._require_user_id()
        return self._execute(
            GET_VAS_PRICES,
            path_params={"user_id": user_id},
            request=VasPricesRequest(item_ids=item_ids, location_id=location_id),
        )  # type: ignore[return-value]

    @swagger_operation(
        "PUT",
        "/core/v1/accounts/{user_id}/items/{item_id}/vas",
        spec="Объявления.json",
        operation_id="putItemVas",
        method_args={"codes": "body.vas_id"},
    )
    def apply_vas(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет дополнительные услуги к объявлению.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        item_id, user_id = self._require_ids()
        validate_string_items("codes", codes)
        request_payload = ApplyVasRequest(codes=codes).to_payload()
        target: dict[str, object] = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas",
                target=target,
                request_payload=request_payload,
            )
        payload = self._execute(
            APPLY_ITEM_VAS,
            path_params={"user_id": user_id, "item_id": item_id},
            request=ApplyVasRequest(codes=codes),
            idempotency_key=idempotency_key,
        )
        return PromotionActionResult.from_action_payload(
            payload,
            action="apply_vas",
            target=target,
            request_payload=request_payload,
        )

    @swagger_operation(
        "PUT",
        "/core/v2/accounts/{user_id}/items/{item_id}/vas_packages",
        spec="Объявления.json",
        operation_id="putItemVasPackageV2",
        method_args={"package_code": "body.package_id"},
    )
    def apply_vas_package(
        self,
        *,
        package_code: str,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет пакет дополнительных услуг.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        item_id, user_id = self._require_ids()
        validate_non_empty_string("package_code", package_code)
        request_payload = ApplyVasPackageRequest(package_code=package_code).to_payload()
        target: dict[str, object] = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_package",
                target=target,
                request_payload=request_payload,
            )
        payload = self._execute(
            APPLY_ITEM_VAS_PACKAGE,
            path_params={"user_id": user_id, "item_id": item_id},
            request=ApplyVasPackageRequest(package_code=package_code),
            idempotency_key=idempotency_key,
        )
        return PromotionActionResult.from_action_payload(
            payload,
            action="apply_vas_package",
            target=target,
            request_payload=request_payload,
        )

    @swagger_operation(
        "PUT",
        "/core/v2/items/{item_id}/vas",
        spec="Объявления.json",
        operation_id="applyVas",
        method_args={"codes": "body.slugs"},
    )
    def apply_vas_direct(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет услуги продвижения через прямой v2 endpoint.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.
        """

        item_id = self._require_item_id()
        validate_string_items("codes", codes)
        request_payload = ApplyVasRequest(codes=codes).to_payload()
        target: dict[str, object] = {"item_id": item_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_direct",
                target=target,
                request_payload=request_payload,
            )
        payload = self._execute(
            APPLY_VAS_DIRECT,
            path_params={"item_id": item_id},
            request=ApplyVasRequest(codes=codes),
            idempotency_key=idempotency_key,
        )
        return PromotionActionResult.from_action_payload(
            payload,
            action="apply_vas_direct",
            target=target,
            request_payload=request_payload,
        )

    def _require_item_id(self) -> int:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id)

    def _require_user_id(self) -> int:
        return self._resolve_user_id(self.user_id)

    def _require_ids(self) -> tuple[int, int]:
        return self._require_item_id(), self._require_user_id()


@dataclass(slots=True, frozen=True)
class AutoloadProfile(DomainObject):
    """Доменный объект профиля автозагрузки."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "autoload_profile"
    __sdk_factory_args__ = {"user_id": "path.user_id"}

    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/autoload/v2/profile",
        spec="Автозагрузка.json",
        operation_id="getProfileV2",
    )
    def get(self) -> AutoloadProfileSettings:
        """Получает профиль автозагрузки.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_AUTOLOAD_PROFILE)  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/autoload/v2/profile",
        spec="Автозагрузка.json",
        operation_id="createOrUpdateProfileV2",
    )
    def save(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Сохраняет профиль автозагрузки.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SAVE_AUTOLOAD_PROFILE,
            request=AutoloadProfileUpdateRequest(
                is_enabled=is_enabled,
                email=email,
                callback_url=callback_url,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/autoload/v1/upload",
        spec="Автозагрузка.json",
        operation_id="upload",
        method_args={"url": "constant.url"},
    )
    def upload_by_url(self, *, url: str, idempotency_key: str | None = None) -> UploadResult:
        """Загружает файл по ссылке.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            UPLOAD_BY_URL,
            request=UploadByUrlRequest(url=url),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v1/user-docs/tree",
        spec="Автозагрузка.json",
        operation_id="userDocsTree",
    )
    def get_tree(self) -> AutoloadTreeResult:
        """Получает дерево категорий.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_AUTOLOAD_TREE)  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v1/user-docs/node/{node_slug}/fields",
        spec="Автозагрузка.json",
        operation_id="userDocsNodeFields",
        method_args={"node_slug": "path.node_slug"},
    )
    def get_node_fields(self, *, node_slug: str) -> AutoloadFieldsResult:
        """Получает поля категории.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_AUTOLOAD_NODE_FIELDS,
            path_params={"node_slug": node_slug},
        )  # type: ignore[return-value]


@dataclass(slots=True, frozen=True)
class AutoloadReport(DomainObject):
    """Доменный объект отчета автозагрузки."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "autoload_report"
    __sdk_factory_args__ = {"report_id": "path.report_id"}

    report_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/autoload/v3/reports/{report_id}",
        spec="Автозагрузка.json",
        operation_id="getReportByIdV3",
    )
    def get(self) -> AutoloadReportDetails:
        """Получает конкретный отчет v3.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        report_id = self._require_report_id()
        return self._execute(
            GET_AUTOLOAD_REPORT,
            path_params={"report_id": report_id},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports",
        spec="Автозагрузка.json",
        operation_id="getReportsV2",
    )
    def list(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> PaginatedList[AutoloadReportSummary]:
        """Получает список отчетов автозагрузки.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        page_size = limit or 25
        base_offset = offset or 0

        def fetch_page(page: int | None, _cursor: str | None) -> JsonPage[AutoloadReportSummary]:
            current_page = page or 1
            current_offset = base_offset + (current_page - 1) * page_size
            result = self._execute(
                LIST_AUTOLOAD_REPORTS,
                query={"limit": page_size, "offset": current_offset},
            )
            reports = cast(AutoloadReportsResult, result)
            return JsonPage(
                items=reports.items,
                total=reports.total,
                page=current_page,
                per_page=page_size,
            )

        return Paginator(fetch_page).as_list(first_page=fetch_page(1, None))

    @swagger_operation(
        "GET",
        "/autoload/v3/reports/last_completed_report",
        spec="Автозагрузка.json",
        operation_id="getLastCompletedReportV3",
    )
    def get_last_completed(self) -> AutoloadReportDetails:
        """Получает последний завершенный отчет.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_AUTOLOAD_LAST_COMPLETED_REPORT)  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports/{report_id}/items",
        spec="Автозагрузка.json",
        operation_id="getReportItemsById",
    )
    def get_items(self) -> AutoloadReportItemsResult:
        """Получает объявления из отчета.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        report_id = self._require_report_id()
        return self._execute(
            GET_AUTOLOAD_REPORT_ITEMS,
            path_params={"report_id": report_id},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports/{report_id}/items/fees",
        spec="Автозагрузка.json",
        operation_id="getReportItemsFeesById",
    )
    def get_fees(self) -> AutoloadFeesResult:
        """Получает списания по объявлениям отчета.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        report_id = self._require_report_id()
        return self._execute(
            GET_AUTOLOAD_REPORT_FEES,
            path_params={"report_id": report_id},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/items/ad_ids",
        spec="Автозагрузка.json",
        operation_id="getAdIdsByAvitoIds",
        method_args={"avito_ids": "query.query"},
    )
    def get_ad_ids_by_avito_ids(self, *, avito_ids: Sequence[int]) -> IdMappingResult:
        """Получает ad ids по avito ids.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_AD_IDS_BY_AVITO_IDS,
            query={"query": ",".join(str(item) for item in avito_ids)},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/items/avito_ids",
        spec="Автозагрузка.json",
        operation_id="getAvitoIdsByAdIds",
        method_args={"ad_ids": "query.query"},
    )
    def get_avito_ids_by_ad_ids(self, *, ad_ids: Sequence[int]) -> IdMappingResult:
        """Получает avito ids по ad ids.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_AVITO_IDS_BY_AD_IDS,
            query={"query": ",".join(str(item) for item in ad_ids)},
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports/items",
        spec="Автозагрузка.json",
        operation_id="getAutoloadItemsInfoV2",
        method_args={"item_ids": "query.query"},
    )
    def get_items_info(self, *, item_ids: Sequence[int]) -> AutoloadReportItemsResult:
        """Получает информацию по объявлениям автозагрузки.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_AUTOLOAD_ITEMS_INFO,
            query={"query": ",".join(str(item) for item in item_ids)},
        )  # type: ignore[return-value]

    def _require_report_id(self) -> int:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.report_id)


@dataclass(slots=True, frozen=True)
class AutoloadArchive(DomainObject):
    """Доменный объект архивных операций автозагрузки."""

    __swagger_domain__ = "ads"
    __sdk_factory__ = "autoload_archive"
    __sdk_factory_args__ = {"report_id": "path.report_id"}

    report_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/autoload/v1/profile",
        spec="Автозагрузка.json",
        operation_id="getProfile",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="AutoloadArchive.get_profile",
        replacement="autoload_profile().get",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_profile(self) -> AutoloadProfileSettings:
        """Получает архивный профиль автозагрузки.

                Deprecated: используйте `autoload_profile().get`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_ARCHIVE_PROFILE)  # type: ignore[return-value]

    @swagger_operation(
        "POST",
        "/autoload/v1/profile",
        spec="Автозагрузка.json",
        operation_id="createOrUpdateProfile",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="AutoloadArchive.save_profile",
        replacement="autoload_profile().save",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def save_profile(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Сохраняет архивный профиль автозагрузки.

                Deprecated: используйте `autoload_profile().save`; удаление в версии 1.3.0.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            SAVE_ARCHIVE_PROFILE,
            request=AutoloadProfileUpdateRequest(
                is_enabled=is_enabled,
                email=email,
                callback_url=callback_url,
            ),
            idempotency_key=idempotency_key,
        )  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports/last_completed_report",
        spec="Автозагрузка.json",
        operation_id="getLastCompletedReport",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="AutoloadArchive.get_last_completed_report",
        replacement="autoload_report().get_last_completed",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_last_completed_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по последней выгрузке.

                Deprecated: используйте `autoload_report().get_last_completed`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(GET_ARCHIVE_LAST_COMPLETED_REPORT)  # type: ignore[return-value]

    @swagger_operation(
        "GET",
        "/autoload/v2/reports/{report_id}",
        spec="Автозагрузка.json",
        operation_id="getReportByIdV2",
        deprecated=True,
        legacy=True,
    )
    @deprecated_method(
        symbol="AutoloadArchive.get_report",
        replacement="autoload_report().get",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по конкретной выгрузке.

                Deprecated: используйте `autoload_report().get`; удаление в версии 1.3.0.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        report_id = self._require_report_id()
        return self._execute(
            GET_ARCHIVE_REPORT,
            path_params={"report_id": report_id},
        )  # type: ignore[return-value]

    def _require_report_id(self) -> int:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.report_id)


__all__ = (
    "Ad",
    "AdPromotion",
    "AdStats",
    "AutoloadArchive",
    "AutoloadProfile",
    "AutoloadReport",
)
