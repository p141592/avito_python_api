"""Operation specs for ads domain."""

from __future__ import annotations

from avito.ads import _mapping
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
from avito.core import OperationSpec


class ListingResponse(Listing):
    @classmethod
    def from_payload(cls, payload: object) -> Listing:
        return _mapping.map_ad_item(payload)


class AdsListResponse(AdsListResult):
    @classmethod
    def from_payload(cls, payload: object) -> AdsListResult:
        return _mapping.map_ads_list(payload)


class UpdatePriceResponse(UpdatePriceResult):
    @classmethod
    def from_payload(cls, payload: object) -> UpdatePriceResult:
        return _mapping.map_update_price_result(payload)


class CallsStatsResponse(CallsStatsResult):
    @classmethod
    def from_payload(cls, payload: object) -> CallsStatsResult:
        return _mapping.map_calls_stats(payload)


class ItemStatsResponse(ItemStatsResult):
    @classmethod
    def from_payload(cls, payload: object) -> ItemStatsResult:
        return _mapping.map_item_stats(payload)


class ItemAnalyticsResponse(ItemAnalyticsResult):
    @classmethod
    def from_payload(cls, payload: object) -> ItemAnalyticsResult:
        return _mapping.map_item_analytics(payload)


class AccountSpendingsResponse(AccountSpendings):
    @classmethod
    def from_payload(cls, payload: object) -> AccountSpendings:
        return _mapping.map_spendings(payload)


class VasPricesResponse(VasPricesResult):
    @classmethod
    def from_payload(cls, payload: object) -> VasPricesResult:
        return _mapping.map_vas_prices(payload)


class AutoloadProfileResponse(AutoloadProfileSettings):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadProfileSettings:
        return _mapping.map_autoload_profile(payload)


class AdsActionResponse(AdsActionResult):
    @classmethod
    def from_payload(cls, payload: object) -> AdsActionResult:
        return _mapping.map_action_result(payload)


class UploadResponse(UploadResult):
    @classmethod
    def from_payload(cls, payload: object) -> UploadResult:
        return _mapping.map_upload_result(payload)


class AutoloadFieldsResponse(AutoloadFieldsResult):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadFieldsResult:
        return _mapping.map_autoload_fields(payload)


class AutoloadTreeResponse(AutoloadTreeResult):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadTreeResult:
        return _mapping.map_autoload_tree(payload)


class IdMappingResponse(IdMappingResult):
    @classmethod
    def from_payload(cls, payload: object) -> IdMappingResult:
        return _mapping.map_id_mapping(payload)


class AutoloadReportsResponse(AutoloadReportsResult):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadReportsResult:
        return _mapping.map_autoload_reports(payload)


class AutoloadReportItemsResponse(AutoloadReportItemsResult):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadReportItemsResult:
        return _mapping.map_autoload_report_items(payload)


class AutoloadReportDetailsResponse(AutoloadReportDetails):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadReportDetails:
        return _mapping.map_autoload_report_details(payload)


class AutoloadFeesResponse(AutoloadFeesResult):
    @classmethod
    def from_payload(cls, payload: object) -> AutoloadFeesResult:
        return _mapping.map_autoload_fees(payload)


class LegacyAutoloadReportResponse(LegacyAutoloadReport):
    @classmethod
    def from_payload(cls, payload: object) -> LegacyAutoloadReport:
        return _mapping.map_legacy_autoload_report(payload)


GET_ITEM = OperationSpec(
    name="ads.get_item",
    method="GET",
    path="/core/v1/accounts/{user_id}/items/{item_id}/",
    response_model=ListingResponse,
)
LIST_ITEMS = OperationSpec(
    name="ads.list_items",
    method="GET",
    path="/core/v1/items",
    response_model=AdsListResponse,
)
UPDATE_PRICE = OperationSpec(
    name="ads.update_price",
    method="POST",
    path="/core/v1/items/{item_id}/update_price",
    request_model=UpdatePriceRequest,
    response_model=UpdatePriceResponse,
    retry_mode="enabled",
)
GET_CALLS_STATS = OperationSpec(
    name="ads.stats.calls",
    method="POST",
    path="/core/v1/accounts/{user_id}/calls/stats/",
    request_model=CallsStatsRequest,
    response_model=CallsStatsResponse,
    retry_mode="enabled",
)
GET_ITEM_STATS = OperationSpec(
    name="ads.stats.items",
    method="POST",
    path="/stats/v1/accounts/{user_id}/items",
    request_model=ItemStatsRequest,
    response_model=ItemStatsResponse,
    retry_mode="enabled",
)
GET_ITEM_ANALYTICS = OperationSpec(
    name="ads.stats.analytics",
    method="POST",
    path="/stats/v2/accounts/{user_id}/items",
    request_model=ItemStatsRequest,
    response_model=ItemAnalyticsResponse,
    retry_mode="enabled",
)
GET_ACCOUNT_SPENDINGS = OperationSpec(
    name="ads.stats.spendings",
    method="POST",
    path="/stats/v2/accounts/{user_id}/spendings",
    request_model=ItemStatsRequest,
    response_model=AccountSpendingsResponse,
    retry_mode="enabled",
)
GET_VAS_PRICES = OperationSpec(
    name="ads.vas.prices",
    method="POST",
    path="/core/v1/accounts/{user_id}/vas/prices",
    request_model=VasPricesRequest,
    response_model=VasPricesResponse,
    retry_mode="enabled",
)
APPLY_ITEM_VAS = OperationSpec(
    name="ads.vas.apply_item_vas",
    method="PUT",
    path="/core/v1/accounts/{user_id}/items/{item_id}/vas",
    request_model=ApplyVasRequest,
    retry_mode="enabled",
)
APPLY_ITEM_VAS_PACKAGE = OperationSpec(
    name="ads.vas.apply_item_vas_package",
    method="PUT",
    path="/core/v2/accounts/{user_id}/items/{item_id}/vas_packages",
    request_model=ApplyVasPackageRequest,
    retry_mode="enabled",
)
APPLY_VAS_DIRECT = OperationSpec(
    name="ads.vas.apply_direct",
    method="PUT",
    path="/core/v2/items/{item_id}/vas/",
    request_model=ApplyVasRequest,
    retry_mode="enabled",
)
GET_AUTOLOAD_PROFILE = OperationSpec(
    name="ads.autoload.get_profile",
    method="GET",
    path="/autoload/v2/profile",
    response_model=AutoloadProfileResponse,
)
SAVE_AUTOLOAD_PROFILE = OperationSpec(
    name="ads.autoload.save_profile",
    method="POST",
    path="/autoload/v2/profile",
    request_model=AutoloadProfileUpdateRequest,
    response_model=AdsActionResponse,
    retry_mode="enabled",
)
UPLOAD_BY_URL = OperationSpec(
    name="ads.autoload.upload_by_url",
    method="POST",
    path="/autoload/v1/upload",
    request_model=UploadByUrlRequest,
    response_model=UploadResponse,
    retry_mode="enabled",
)
GET_AUTOLOAD_NODE_FIELDS = OperationSpec(
    name="ads.autoload.get_node_fields",
    method="GET",
    path="/autoload/v1/user-docs/node/{node_slug}/fields",
    response_model=AutoloadFieldsResponse,
)
GET_AUTOLOAD_TREE = OperationSpec(
    name="ads.autoload.get_tree",
    method="GET",
    path="/autoload/v1/user-docs/tree",
    response_model=AutoloadTreeResponse,
)
GET_AD_IDS_BY_AVITO_IDS = OperationSpec(
    name="ads.autoload.get_ad_ids_by_avito_ids",
    method="GET",
    path="/autoload/v2/items/ad_ids",
    response_model=IdMappingResponse,
)
GET_AVITO_IDS_BY_AD_IDS = OperationSpec(
    name="ads.autoload.get_avito_ids_by_ad_ids",
    method="GET",
    path="/autoload/v2/items/avito_ids",
    response_model=IdMappingResponse,
)
LIST_AUTOLOAD_REPORTS = OperationSpec(
    name="ads.autoload.list_reports",
    method="GET",
    path="/autoload/v2/reports",
    response_model=AutoloadReportsResponse,
)
GET_AUTOLOAD_ITEMS_INFO = OperationSpec(
    name="ads.autoload.get_items_info",
    method="GET",
    path="/autoload/v2/reports/items",
    response_model=AutoloadReportItemsResponse,
)
GET_AUTOLOAD_REPORT = OperationSpec(
    name="ads.autoload.get_report",
    method="GET",
    path="/autoload/v3/reports/{report_id}",
    response_model=AutoloadReportDetailsResponse,
)
GET_AUTOLOAD_LAST_COMPLETED_REPORT = OperationSpec(
    name="ads.autoload.get_last_completed_report",
    method="GET",
    path="/autoload/v3/reports/last_completed_report",
    response_model=AutoloadReportDetailsResponse,
)
GET_AUTOLOAD_REPORT_ITEMS = OperationSpec(
    name="ads.autoload.get_report_items",
    method="GET",
    path="/autoload/v2/reports/{report_id}/items",
    response_model=AutoloadReportItemsResponse,
)
GET_AUTOLOAD_REPORT_FEES = OperationSpec(
    name="ads.autoload.get_report_fees",
    method="GET",
    path="/autoload/v2/reports/{report_id}/items/fees",
    response_model=AutoloadFeesResponse,
)
GET_ARCHIVE_PROFILE = OperationSpec(
    name="ads.autoload_archive.get_profile",
    method="GET",
    path="/autoload/v1/profile",
    response_model=AutoloadProfileResponse,
)
SAVE_ARCHIVE_PROFILE = OperationSpec(
    name="ads.autoload_archive.save_profile",
    method="POST",
    path="/autoload/v1/profile",
    request_model=AutoloadProfileUpdateRequest,
    response_model=AdsActionResponse,
    retry_mode="enabled",
)
GET_ARCHIVE_LAST_COMPLETED_REPORT = OperationSpec(
    name="ads.autoload_archive.get_last_completed_report",
    method="GET",
    path="/autoload/v2/reports/last_completed_report",
    response_model=LegacyAutoloadReportResponse,
)
GET_ARCHIVE_REPORT = OperationSpec(
    name="ads.autoload_archive.get_report",
    method="GET",
    path="/autoload/v2/reports/{report_id}",
    response_model=LegacyAutoloadReportResponse,
)
