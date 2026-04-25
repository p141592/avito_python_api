"""Внутренние section clients для раздела ads."""

from __future__ import annotations

from dataclasses import dataclass

from avito.ads.enums import ListingStatus
from avito.ads.mappers import (
    map_action_result,
    map_ad_item,
    map_ads_list,
    map_autoload_fees,
    map_autoload_fields,
    map_autoload_profile,
    map_autoload_report_details,
    map_autoload_report_items,
    map_autoload_reports,
    map_autoload_tree,
    map_calls_stats,
    map_id_mapping,
    map_item_analytics,
    map_item_stats,
    map_legacy_autoload_report,
    map_spendings,
    map_update_price_result,
    map_upload_result,
    map_vas_prices,
)
from avito.ads.models import (
    AccountSpendings,
    AdsActionResult,
    ApplyVasPackageRequest,
    ApplyVasRequest,
    AutoloadFeesResult,
    AutoloadFieldsResult,
    AutoloadProfileSettings,
    AutoloadProfileUpdateRequest,
    AutoloadReportDetails,
    AutoloadReportItemsResult,
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
    UpdatePriceRequest,
    UpdatePriceResult,
    UploadByUrlRequest,
    UploadResult,
    VasPricesRequest,
    VasPricesResult,
)
from avito.core import (
    JsonPage,
    PaginatedList,
    Paginator,
    RequestContext,
    Transport,
    ValidationError,
)
from avito.core.mapping import request_public_model
from avito.promotion.mappers import map_promotion_action
from avito.promotion.models import PromotionActionResult


def _bounded_total(total: int | None, max_items: int | None) -> int | None:
    if max_items is None:
        return total
    if total is None:
        return max_items
    return min(total, max_items)


@dataclass(slots=True, frozen=True)
class AdsClient:
    """Выполняет HTTP-операции по разделу объявлений."""

    transport: Transport

    def get_item(self, *, user_id: int, item_id: int) -> Listing:
        """Получает одно объявление."""

        return request_public_model(
            self.transport,
            "GET",
            f"/core/v1/accounts/{user_id}/items/{item_id}/",
            context=RequestContext("ads.get_item"),
            mapper=map_ad_item,
        )

    def list_items(
        self,
        *,
        user_id: int | None = None,
        status: ListingStatus | str | None = None,
        limit: int | None = None,
        page_size: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[Listing]:
        """Получает список объявлений пользователя."""

        resolved_page_size = page_size or limit
        start_offset = offset if offset is not None else 0 if resolved_page_size is not None else None
        result = request_public_model(
            self.transport,
            "GET",
            "/core/v1/items",
            context=RequestContext("ads.list_items"),
            mapper=map_ads_list,
            params={
                "user_id": user_id,
                "status": status,
                "limit": resolved_page_size,
                "offset": start_offset,
            },
        )
        page_size = resolved_page_size if resolved_page_size and resolved_page_size > 0 else len(result.items)
        max_items = limit if limit is not None and limit >= 0 else None
        first_items = result.items[:max_items] if max_items is not None else result.items
        total = _bounded_total(result.total, max_items)
        resolved_offset = start_offset or 0
        start_page = resolved_offset // page_size + 1 if page_size > 0 else 1
        first_page = JsonPage(
            items=list(first_items),
            total=total,
            page=start_page,
            per_page=page_size if page_size > 0 else None,
        )
        return Paginator(
            lambda page, cursor: self._fetch_ads_page(
                page=page,
                user_id=user_id,
                status=status,
                page_size=page_size,
                max_items=max_items,
                base_offset=resolved_offset,
            )
        ).as_list(start_page=start_page, first_page=first_page)

    def _fetch_ads_page(
        self,
        *,
        page: int | None,
        user_id: int | None,
        status: ListingStatus | str | None,
        page_size: int,
        max_items: int | None,
        base_offset: int,
    ) -> JsonPage[Listing]:
        if page is None:
            raise ValidationError("Для операции требуется `page`.")

        offset = (page - 1) * page_size
        already_requested = max(offset - base_offset, 0)
        remaining = max_items - already_requested if max_items is not None else None
        if remaining is not None and remaining <= 0:
            return JsonPage(items=[], total=max_items, page=page, per_page=page_size)
        result = request_public_model(
            self.transport,
            "GET",
            "/core/v1/items",
            context=RequestContext("ads.list_items"),
            mapper=map_ads_list,
            params={
                "user_id": user_id,
                "status": status,
                "limit": min(page_size, remaining) if remaining is not None else page_size,
                "offset": offset,
            },
        )
        items = result.items[:remaining] if remaining is not None else result.items
        return JsonPage(
            items=list(items),
            total=_bounded_total(result.total, max_items),
            page=page,
            per_page=page_size,
        )

    def update_price(
        self,
        *,
        item_id: int,
        price: int | float,
        idempotency_key: str | None = None,
    ) -> UpdatePriceResult:
        """Обновляет цену объявления."""

        return request_public_model(
            self.transport,
            "POST",
            f"/core/v1/items/{item_id}/update_price",
            context=RequestContext("ads.update_price", allow_retry=idempotency_key is not None),
            mapper=map_update_price_result,
            json_body=UpdatePriceRequest(price=price).to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class StatsClient:
    """Выполняет HTTP-операции по статистике объявлений."""

    transport: Transport

    def get_calls_stats(
        self,
        *,
        user_id: int,
        item_ids: list[int],
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> CallsStatsResult:
        """Получает статистику звонков."""

        return request_public_model(
            self.transport,
            "POST",
            f"/core/v1/accounts/{user_id}/calls/stats/",
            context=RequestContext("ads.stats.calls", allow_retry=True),
            mapper=map_calls_stats,
            json_body=CallsStatsRequest(
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
            ).to_payload(),
        )

    def get_item_stats(
        self,
        *,
        user_id: int,
        item_ids: list[int],
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> ItemStatsResult:
        """Получает статистику по списку объявлений."""

        return request_public_model(
            self.transport,
            "POST",
            f"/stats/v1/accounts/{user_id}/items",
            context=RequestContext("ads.stats.items", allow_retry=True),
            mapper=map_item_stats,
            json_body=ItemStatsRequest(
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ).to_payload(),
        )

    def get_item_analytics(
        self,
        *,
        user_id: int,
        item_ids: list[int],
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> ItemAnalyticsResult:
        """Получает аналитику по профилю."""

        return request_public_model(
            self.transport,
            "POST",
            f"/stats/v2/accounts/{user_id}/items",
            context=RequestContext("ads.stats.analytics", allow_retry=True),
            mapper=map_item_analytics,
            json_body=ItemStatsRequest(
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ).to_payload(),
        )

    def get_account_spendings(
        self,
        *,
        user_id: int,
        item_ids: list[int],
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> AccountSpendings:
        """Получает статистику расходов профиля."""

        return request_public_model(
            self.transport,
            "POST",
            f"/stats/v2/accounts/{user_id}/spendings",
            context=RequestContext("ads.stats.spendings", allow_retry=True),
            mapper=map_spendings,
            json_body=ItemStatsRequest(
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class VasClient:
    """Выполняет HTTP-операции VAS и продвижения."""

    transport: Transport

    def get_prices(
        self, *, user_id: int, item_ids: list[int], location_id: int | None = None
    ) -> VasPricesResult:
        """Получает цены VAS и доступные услуги продвижения."""

        return request_public_model(
            self.transport,
            "POST",
            f"/core/v1/accounts/{user_id}/vas/prices",
            context=RequestContext("ads.vas.prices", allow_retry=True),
            mapper=map_vas_prices,
            json_body=VasPricesRequest(item_ids=item_ids, location_id=location_id).to_payload(),
        )

    def apply_item_vas(
        self,
        *,
        user_id: int,
        item_id: int,
        codes: list[str],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет дополнительные услуги к объявлению."""

        payload_to_send = ApplyVasRequest(codes=codes).to_payload()
        return self.transport.request_public_model(
            "PUT",
            f"/core/v1/accounts/{user_id}/items/{item_id}/vas",
            context=RequestContext(
                "ads.vas.apply_item_vas",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="apply_vas",
                target={"item_id": item_id, "user_id": user_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )

    def apply_item_vas_package(
        self,
        *,
        user_id: int,
        item_id: int,
        package_code: str,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет пакет дополнительных услуг."""

        payload_to_send = ApplyVasPackageRequest(package_code=package_code).to_payload()
        return self.transport.request_public_model(
            "PUT",
            f"/core/v2/accounts/{user_id}/items/{item_id}/vas_packages",
            context=RequestContext(
                "ads.vas.apply_item_vas_package",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="apply_vas_package",
                target={"item_id": item_id, "user_id": user_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )

    def apply_vas_direct(
        self,
        *,
        item_id: int,
        codes: list[str],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет услуги продвижения через v2 endpoint."""

        payload_to_send = ApplyVasRequest(codes=codes).to_payload()
        return self.transport.request_public_model(
            "PUT",
            f"/core/v2/items/{item_id}/vas/",
            context=RequestContext("ads.vas.apply_direct", allow_retry=idempotency_key is not None),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="apply_vas_direct",
                target={"item_id": item_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class AutoloadClient:
    """Выполняет HTTP-операции автозагрузки."""

    transport: Transport

    def get_profile(self) -> AutoloadProfileSettings:
        """Получает профиль пользователя автозагрузки."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v2/profile",
            context=RequestContext("ads.autoload.get_profile"),
            mapper=map_autoload_profile,
        )

    def save_profile(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Создает или редактирует профиль автозагрузки."""

        return request_public_model(
            self.transport,
            "POST",
            "/autoload/v2/profile",
            context=RequestContext("ads.autoload.save_profile", allow_retry=idempotency_key is not None),
            mapper=map_action_result,
            json_body=AutoloadProfileUpdateRequest(
                is_enabled=is_enabled,
                email=email,
                callback_url=callback_url,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def upload_by_url(self, *, url: str, idempotency_key: str | None = None) -> UploadResult:
        """Запускает загрузку файла по ссылке."""

        return request_public_model(
            self.transport,
            "POST",
            "/autoload/v1/upload",
            context=RequestContext(
                "ads.autoload.upload_by_url",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_upload_result,
            json_body=UploadByUrlRequest(url=url).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_node_fields(self, *, node_slug: str) -> AutoloadFieldsResult:
        """Получает поля категории по slug."""

        return request_public_model(
            self.transport,
            "GET",
            f"/autoload/v1/user-docs/node/{node_slug}/fields",
            context=RequestContext("ads.autoload.get_node_fields"),
            mapper=map_autoload_fields,
        )

    def get_tree(self) -> AutoloadTreeResult:
        """Получает дерево категорий автозагрузки."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v1/user-docs/tree",
            context=RequestContext("ads.autoload.get_tree"),
            mapper=map_autoload_tree,
        )

    def get_ad_ids_by_avito_ids(self, *, avito_ids: list[int]) -> IdMappingResult:
        """Получает ad ids по avito ids."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v2/items/ad_ids",
            context=RequestContext("ads.autoload.get_ad_ids_by_avito_ids"),
            mapper=map_id_mapping,
            params={"avito_ids": ",".join(str(item) for item in avito_ids)},
        )

    def get_avito_ids_by_ad_ids(self, *, ad_ids: list[int]) -> IdMappingResult:
        """Получает avito ids по ad ids."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v2/items/avito_ids",
            context=RequestContext("ads.autoload.get_avito_ids_by_ad_ids"),
            mapper=map_id_mapping,
            params={"ad_ids": ",".join(str(item) for item in ad_ids)},
        )

    def list_reports(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> PaginatedList[AutoloadReportSummary]:
        """Получает список отчетов автозагрузки."""

        page_size = limit or 25
        base_offset = offset or 0

        def fetch_page(page: int | None, _cursor: str | None) -> JsonPage[AutoloadReportSummary]:
            current_page = page or 1
            current_offset = base_offset + (current_page - 1) * page_size
            result = request_public_model(
                self.transport,
                "GET",
                "/autoload/v2/reports",
                context=RequestContext("ads.autoload.list_reports"),
                mapper=map_autoload_reports,
                params={"limit": page_size, "offset": current_offset},
            )
            return JsonPage(
                items=result.items,
                total=result.total,
                page=current_page,
                per_page=page_size,
            )

        return Paginator(fetch_page).as_list(first_page=fetch_page(1, None))

    def get_items_info(self, *, item_ids: list[int]) -> AutoloadReportItemsResult:
        """Получает объявления автозагрузки по ID."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v2/reports/items",
            context=RequestContext("ads.autoload.get_items_info"),
            mapper=map_autoload_report_items,
            params={"item_ids": ",".join(str(item) for item in item_ids)},
        )

    def get_report(self, *, report_id: int) -> AutoloadReportDetails:
        """Получает статистику по конкретной выгрузке v3."""

        return request_public_model(
            self.transport,
            "GET",
            f"/autoload/v3/reports/{report_id}",
            context=RequestContext("ads.autoload.get_report"),
            mapper=map_autoload_report_details,
        )

    def get_last_completed_report(self) -> AutoloadReportDetails:
        """Получает статистику по последней выгрузке v3."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v3/reports/last_completed_report",
            context=RequestContext("ads.autoload.get_last_completed_report"),
            mapper=map_autoload_report_details,
        )

    def get_report_items(self, *, report_id: int) -> AutoloadReportItemsResult:
        """Получает все объявления из конкретной выгрузки."""

        return request_public_model(
            self.transport,
            "GET",
            f"/autoload/v2/reports/{report_id}/items",
            context=RequestContext("ads.autoload.get_report_items"),
            mapper=map_autoload_report_items,
        )

    def get_report_fees(self, *, report_id: int) -> AutoloadFeesResult:
        """Получает списания по объявлениям выгрузки."""

        return request_public_model(
            self.transport,
            "GET",
            f"/autoload/v2/reports/{report_id}/items/fees",
            context=RequestContext("ads.autoload.get_report_fees"),
            mapper=map_autoload_fees,
        )


@dataclass(slots=True, frozen=True)
class AutoloadArchiveClient:
    """Выполняет архивные HTTP-операции автозагрузки."""

    transport: Transport

    def get_profile(self) -> AutoloadProfileSettings:
        """Получает архивный профиль автозагрузки."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v1/profile",
            context=RequestContext("ads.autoload_archive.get_profile"),
            mapper=map_autoload_profile,
        )

    def save_profile(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Создает или редактирует архивный профиль автозагрузки."""

        return request_public_model(
            self.transport,
            "POST",
            "/autoload/v1/profile",
            context=RequestContext(
                "ads.autoload_archive.save_profile",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_action_result,
            json_body=AutoloadProfileUpdateRequest(
                is_enabled=is_enabled,
                email=email,
                callback_url=callback_url,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_last_completed_report(self) -> LegacyAutoloadReport:
        """Получает статистику по последней архивной выгрузке."""

        return request_public_model(
            self.transport,
            "GET",
            "/autoload/v2/reports/last_completed_report",
            context=RequestContext("ads.autoload_archive.get_last_completed_report"),
            mapper=map_legacy_autoload_report,
        )

    def get_report(self, *, report_id: int) -> LegacyAutoloadReport:
        """Получает статистику по конкретной архивной выгрузке."""

        return request_public_model(
            self.transport,
            "GET",
            f"/autoload/v2/reports/{report_id}",
            context=RequestContext("ads.autoload_archive.get_report"),
            mapper=map_legacy_autoload_report,
        )


__all__ = ("AdsClient", "AutoloadArchiveClient", "AutoloadClient", "StatsClient", "VasClient")
