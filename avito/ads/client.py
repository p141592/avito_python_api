"""Внутренние section clients для раздела ads."""

from __future__ import annotations

from dataclasses import dataclass

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
    map_vas_apply_result,
    map_vas_prices,
)
from avito.ads.models import (
    ActionResult,
    AdItem,
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
    AutoloadTreeResult,
    CallsStatsRequest,
    CallsStatsResult,
    IdMappingResult,
    ItemAnalyticsResult,
    ItemStatsRequest,
    ItemStatsResult,
    LegacyAutoloadReport,
    SpendingsResult,
    UpdatePriceRequest,
    UpdatePriceResult,
    UploadByUrlRequest,
    UploadResult,
    VasApplyResult,
    VasPricesRequest,
    VasPricesResult,
)
from avito.core import JsonPage, Paginator, RequestContext, Transport


@dataclass(slots=True)
class AdsClient:
    """Выполняет HTTP-операции по разделу объявлений."""

    transport: Transport

    def get_item(self, *, user_id: int, item_id: int) -> AdItem:
        """Получает одно объявление."""

        payload = self.transport.request_json(
            "GET",
            f"/core/v1/accounts/{user_id}/items/{item_id}/",
            context=RequestContext("ads.get_item"),
        )
        return map_ad_item(payload)

    def list_items(
        self,
        *,
        user_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> AdsListResult:
        """Получает список объявлений пользователя."""

        start_offset = offset if offset is not None else 0 if limit is not None else None
        payload = self.transport.request_json(
            "GET",
            "/core/v1/items",
            context=RequestContext("ads.list_items"),
            params={
                "user_id": user_id,
                "status": status,
                "limit": limit,
                "offset": start_offset,
            },
        )
        result = map_ads_list(payload)
        page_size = limit if limit and limit > 0 else len(result.items)
        resolved_offset = start_offset or 0

        if result.total is None or page_size <= 0 or resolved_offset + len(result.items) >= result.total:
            return result

        start_page = resolved_offset // page_size + 1
        paginator = Paginator(
            lambda page, cursor: self._fetch_ads_page(
                page=page,
                user_id=user_id,
                status=status,
                page_size=page_size,
            )
        )
        paginated_items = paginator.as_list(
            start_page=start_page,
            first_page=JsonPage(
                items=list(result.items),
                total=result.total,
                page=start_page,
                per_page=page_size,
            ),
        )
        return AdsListResult(items=paginated_items, total=result.total, raw_payload=result.raw_payload)

    def _fetch_ads_page(
        self,
        *,
        page: int | None,
        user_id: int | None,
        status: str | None,
        page_size: int,
    ) -> JsonPage[AdItem]:
        if page is None:
            raise ValueError("Постраничная загрузка объявлений требует номера страницы.")

        offset = (page - 1) * page_size
        payload = self.transport.request_json(
            "GET",
            "/core/v1/items",
            context=RequestContext("ads.list_items"),
            params={
                "user_id": user_id,
                "status": status,
                "limit": page_size,
                "offset": offset,
            },
        )
        result = map_ads_list(payload)
        return JsonPage(
            items=list(result.items),
            total=result.total,
            page=page,
            per_page=page_size,
        )

    def update_price(self, *, item_id: int, price: UpdatePriceRequest) -> UpdatePriceResult:
        """Обновляет цену объявления."""

        payload = self.transport.request_json(
            "POST",
            f"/core/v1/items/{item_id}/update_price",
            context=RequestContext("ads.update_price", allow_retry=True),
            json_body=price.to_payload(),
        )
        return map_update_price_result(payload)


@dataclass(slots=True)
class StatsClient:
    """Выполняет HTTP-операции по статистике объявлений."""

    transport: Transport

    def get_calls_stats(self, *, user_id: int, request: CallsStatsRequest) -> CallsStatsResult:
        """Получает статистику звонков."""

        payload = self.transport.request_json(
            "POST",
            f"/core/v1/accounts/{user_id}/calls/stats/",
            context=RequestContext("ads.stats.calls", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_calls_stats(payload)

    def get_item_stats(self, *, user_id: int, request: ItemStatsRequest) -> ItemStatsResult:
        """Получает статистику по списку объявлений."""

        payload = self.transport.request_json(
            "POST",
            f"/stats/v1/accounts/{user_id}/items",
            context=RequestContext("ads.stats.items", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_item_stats(payload)

    def get_item_analytics(self, *, user_id: int, request: ItemStatsRequest) -> ItemAnalyticsResult:
        """Получает аналитику по профилю."""

        payload = self.transport.request_json(
            "POST",
            f"/stats/v2/accounts/{user_id}/items",
            context=RequestContext("ads.stats.analytics", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_item_analytics(payload)

    def get_account_spendings(self, *, user_id: int, request: ItemStatsRequest) -> SpendingsResult:
        """Получает статистику расходов профиля."""

        payload = self.transport.request_json(
            "POST",
            f"/stats/v2/accounts/{user_id}/spendings",
            context=RequestContext("ads.stats.spendings", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_spendings(payload)


@dataclass(slots=True)
class VasClient:
    """Выполняет HTTP-операции VAS и продвижения."""

    transport: Transport

    def get_prices(self, *, user_id: int, request: VasPricesRequest) -> VasPricesResult:
        """Получает цены VAS и доступные услуги продвижения."""

        payload = self.transport.request_json(
            "POST",
            f"/core/v1/accounts/{user_id}/vas/prices",
            context=RequestContext("ads.vas.prices", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_vas_prices(payload)

    def apply_item_vas(
        self, *, user_id: int, item_id: int, request: ApplyVasRequest
    ) -> ActionResult:
        """Применяет дополнительные услуги к объявлению."""

        payload = self.transport.request_json(
            "PUT",
            f"/core/v1/accounts/{user_id}/items/{item_id}/vas",
            context=RequestContext("ads.vas.apply_item_vas", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action_result(payload)

    def apply_item_vas_package(
        self, *, user_id: int, item_id: int, request: ApplyVasPackageRequest
    ) -> ActionResult:
        """Применяет пакет дополнительных услуг."""

        payload = self.transport.request_json(
            "PUT",
            f"/core/v2/accounts/{user_id}/items/{item_id}/vas_packages",
            context=RequestContext("ads.vas.apply_item_vas_package", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action_result(payload)

    def apply_vas_v2(self, *, item_id: int, request: ApplyVasRequest) -> VasApplyResult:
        """Применяет услуги продвижения через v2 endpoint."""

        payload = self.transport.request_json(
            "PUT",
            f"/core/v2/items/{item_id}/vas/",
            context=RequestContext("ads.vas.apply_v2", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_vas_apply_result(payload)


@dataclass(slots=True)
class AutoloadClient:
    """Выполняет HTTP-операции автозагрузки."""

    transport: Transport

    def get_profile(self) -> AutoloadProfileSettings:
        """Получает профиль пользователя автозагрузки."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/profile",
            context=RequestContext("ads.autoload.get_profile"),
        )
        return map_autoload_profile(payload)

    def save_profile(self, request: AutoloadProfileUpdateRequest) -> ActionResult:
        """Создает или редактирует профиль автозагрузки."""

        payload = self.transport.request_json(
            "POST",
            "/autoload/v2/profile",
            context=RequestContext("ads.autoload.save_profile", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action_result(payload)

    def upload_by_url(self, request: UploadByUrlRequest) -> UploadResult:
        """Запускает загрузку файла по ссылке."""

        payload = self.transport.request_json(
            "POST",
            "/autoload/v1/upload",
            context=RequestContext("ads.autoload.upload_by_url", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_upload_result(payload)

    def get_node_fields(self, *, node_slug: str) -> AutoloadFieldsResult:
        """Получает поля категории по slug."""

        payload = self.transport.request_json(
            "GET",
            f"/autoload/v1/user-docs/node/{node_slug}/fields",
            context=RequestContext("ads.autoload.get_node_fields"),
        )
        return map_autoload_fields(payload)

    def get_tree(self) -> AutoloadTreeResult:
        """Получает дерево категорий автозагрузки."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v1/user-docs/tree",
            context=RequestContext("ads.autoload.get_tree"),
        )
        return map_autoload_tree(payload)

    def get_ad_ids_by_avito_ids(self, *, avito_ids: list[int]) -> IdMappingResult:
        """Получает ad ids по avito ids."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/items/ad_ids",
            context=RequestContext("ads.autoload.get_ad_ids_by_avito_ids"),
            params={"avito_ids": ",".join(str(item) for item in avito_ids)},
        )
        return map_id_mapping(payload)

    def get_avito_ids_by_ad_ids(self, *, ad_ids: list[int]) -> IdMappingResult:
        """Получает avito ids по ad ids."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/items/avito_ids",
            context=RequestContext("ads.autoload.get_avito_ids_by_ad_ids"),
            params={"ad_ids": ",".join(str(item) for item in ad_ids)},
        )
        return map_id_mapping(payload)

    def list_reports(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> AutoloadReportsResult:
        """Получает список отчетов автозагрузки."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/reports",
            context=RequestContext("ads.autoload.list_reports"),
            params={"limit": limit, "offset": offset},
        )
        return map_autoload_reports(payload)

    def get_items_info(self, *, item_ids: list[int]) -> AutoloadReportItemsResult:
        """Получает объявления автозагрузки по ID."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/reports/items",
            context=RequestContext("ads.autoload.get_items_info"),
            params={"item_ids": ",".join(str(item) for item in item_ids)},
        )
        return map_autoload_report_items(payload)

    def get_report(self, *, report_id: int) -> AutoloadReportDetails:
        """Получает статистику по конкретной выгрузке v3."""

        payload = self.transport.request_json(
            "GET",
            f"/autoload/v3/reports/{report_id}",
            context=RequestContext("ads.autoload.get_report"),
        )
        return map_autoload_report_details(payload)

    def get_last_completed_report(self) -> AutoloadReportDetails:
        """Получает статистику по последней выгрузке v3."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v3/reports/last_completed_report",
            context=RequestContext("ads.autoload.get_last_completed_report"),
        )
        return map_autoload_report_details(payload)

    def get_report_items(self, *, report_id: int) -> AutoloadReportItemsResult:
        """Получает все объявления из конкретной выгрузки."""

        payload = self.transport.request_json(
            "GET",
            f"/autoload/v2/reports/{report_id}/items",
            context=RequestContext("ads.autoload.get_report_items"),
        )
        return map_autoload_report_items(payload)

    def get_report_fees(self, *, report_id: int) -> AutoloadFeesResult:
        """Получает списания по объявлениям выгрузки."""

        payload = self.transport.request_json(
            "GET",
            f"/autoload/v2/reports/{report_id}/items/fees",
            context=RequestContext("ads.autoload.get_report_fees"),
        )
        return map_autoload_fees(payload)


@dataclass(slots=True)
class AutoloadLegacyClient:
    """Выполняет legacy HTTP-операции автозагрузки."""

    transport: Transport

    def get_profile(self) -> AutoloadProfileSettings:
        """Получает legacy профиль автозагрузки."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v1/profile",
            context=RequestContext("ads.autoload_legacy.get_profile"),
        )
        return map_autoload_profile(payload)

    def save_profile(self, request: AutoloadProfileUpdateRequest) -> ActionResult:
        """Создает или редактирует legacy профиль автозагрузки."""

        payload = self.transport.request_json(
            "POST",
            "/autoload/v1/profile",
            context=RequestContext("ads.autoload_legacy.save_profile", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_action_result(payload)

    def get_last_completed_report(self) -> LegacyAutoloadReport:
        """Получает статистику по последней выгрузке legacy v2."""

        payload = self.transport.request_json(
            "GET",
            "/autoload/v2/reports/last_completed_report",
            context=RequestContext("ads.autoload_legacy.get_last_completed_report"),
        )
        return map_legacy_autoload_report(payload)

    def get_report(self, *, report_id: int) -> LegacyAutoloadReport:
        """Получает статистику по конкретной выгрузке legacy v2."""

        payload = self.transport.request_json(
            "GET",
            f"/autoload/v2/reports/{report_id}",
            context=RequestContext("ads.autoload_legacy.get_report"),
        )
        return map_legacy_autoload_report(payload)


__all__ = ("AdsClient", "AutoloadClient", "AutoloadLegacyClient", "StatsClient", "VasClient")
