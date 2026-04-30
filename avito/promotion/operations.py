"""Operation specs for promotion domain."""

from __future__ import annotations

from avito.core import OperationSpec
from avito.promotion import _mapping
from avito.promotion.models import (
    AutostrategyBudget,
    AutostrategyStat,
    BbipForecastsResult,
    BbipSuggestsResult,
    CampaignActionResult,
    CampaignDetailsResult,
    CampaignsResult,
    CancelTrxPromotionRequest,
    CpaAuctionBidsResult,
    CreateAutostrategyBudgetRequest,
    CreateAutostrategyCampaignRequest,
    CreateBbipForecastsRequest,
    CreateBbipOrderRequest,
    CreateBbipSuggestsRequest,
    CreateItemBidsRequest,
    CreateTrxPromotionApplyRequest,
    DeletePromotionRequest,
    GetAutostrategyCampaignInfoRequest,
    GetAutostrategyStatRequest,
    GetPromotionOrderStatusRequest,
    GetPromotionsByItemIdsRequest,
    ListAutostrategyCampaignsRequest,
    ListPromotionOrdersRequest,
    ListPromotionServicesRequest,
    PromotionOrdersResult,
    PromotionOrderStatusResult,
    PromotionServiceDictionary,
    PromotionServicesResult,
    StopAutostrategyCampaignRequest,
    TargetActionGetBidsResult,
    TargetActionPromotionsByItemIdsResult,
    TrxCommissionsResult,
    UpdateAutoBidRequest,
    UpdateAutostrategyCampaignRequest,
    UpdateManualBidRequest,
)


class PromotionServiceDictionaryResponse(PromotionServiceDictionary):
    @classmethod
    def from_payload(cls, payload: object) -> PromotionServiceDictionary:
        return _mapping.map_promotion_service_dictionary(payload)


class PromotionServicesResponse(PromotionServicesResult):
    @classmethod
    def from_payload(cls, payload: object) -> PromotionServicesResult:
        return _mapping.map_promotion_services(payload)


class PromotionOrdersResponse(PromotionOrdersResult):
    @classmethod
    def from_payload(cls, payload: object) -> PromotionOrdersResult:
        return _mapping.map_promotion_orders(payload)


class PromotionOrderStatusResponse(PromotionOrderStatusResult):
    @classmethod
    def from_payload(cls, payload: object) -> PromotionOrderStatusResult:
        return _mapping.map_promotion_order_status(payload)


class BbipForecastsResponse(BbipForecastsResult):
    @classmethod
    def from_payload(cls, payload: object) -> BbipForecastsResult:
        return _mapping.map_bbip_forecasts(payload)


class BbipSuggestsResponse(BbipSuggestsResult):
    @classmethod
    def from_payload(cls, payload: object) -> BbipSuggestsResult:
        return _mapping.map_bbip_suggests(payload)


class TrxCommissionsResponse(TrxCommissionsResult):
    @classmethod
    def from_payload(cls, payload: object) -> TrxCommissionsResult:
        return _mapping.map_trx_commissions(payload)


class CpaAuctionBidsResponse(CpaAuctionBidsResult):
    @classmethod
    def from_payload(cls, payload: object) -> CpaAuctionBidsResult:
        return _mapping.map_cpa_auction_bids(payload)


class TargetActionGetBidsResponse(TargetActionGetBidsResult):
    @classmethod
    def from_payload(cls, payload: object) -> TargetActionGetBidsResult:
        return _mapping.map_target_action_get_bids_out(payload)


class TargetActionPromotionsResponse(TargetActionPromotionsByItemIdsResult):
    @classmethod
    def from_payload(cls, payload: object) -> TargetActionPromotionsByItemIdsResult:
        return _mapping.map_target_action_get_promotions_by_item_ids_out(payload)


class AutostrategyBudgetResponse(AutostrategyBudget):
    @classmethod
    def from_payload(cls, payload: object) -> AutostrategyBudget:
        return _mapping.map_autostrategy_budget(payload)


class CampaignActionResponse(CampaignActionResult):
    @classmethod
    def from_payload(cls, payload: object) -> CampaignActionResult:
        return _mapping.map_campaign_action(payload)


class CampaignDetailsResponse(CampaignDetailsResult):
    @classmethod
    def from_payload(cls, payload: object) -> CampaignDetailsResult:
        return _mapping.map_campaign_info(payload)


class CampaignsResponse(CampaignsResult):
    @classmethod
    def from_payload(cls, payload: object) -> CampaignsResult:
        return _mapping.map_campaigns(payload)


class AutostrategyStatResponse(AutostrategyStat):
    @classmethod
    def from_payload(cls, payload: object) -> AutostrategyStat:
        return _mapping.map_autostrategy_stat(payload)


GET_SERVICE_DICTIONARY = OperationSpec(
    name="promotion.get_service_dictionary",
    method="POST",
    path="/promotion/v1/items/services/dict",
    response_model=PromotionServiceDictionaryResponse,
    retry_mode="enabled",
)
LIST_SERVICES = OperationSpec(
    name="promotion.list_services",
    method="POST",
    path="/promotion/v1/items/services/get",
    request_model=ListPromotionServicesRequest,
    response_model=PromotionServicesResponse,
    retry_mode="enabled",
)
LIST_ORDERS = OperationSpec(
    name="promotion.list_orders",
    method="POST",
    path="/promotion/v1/items/services/orders/get",
    request_model=ListPromotionOrdersRequest,
    response_model=PromotionOrdersResponse,
    retry_mode="enabled",
)
GET_ORDER_STATUS = OperationSpec(
    name="promotion.get_order_status",
    method="POST",
    path="/promotion/v1/items/services/orders/status",
    request_model=GetPromotionOrderStatusRequest,
    response_model=PromotionOrderStatusResponse,
    retry_mode="enabled",
)
GET_BBIP_FORECASTS = OperationSpec(
    name="promotion.bbip.get_forecasts",
    method="POST",
    path="/promotion/v1/items/services/bbip/forecasts/get",
    request_model=CreateBbipForecastsRequest,
    response_model=BbipForecastsResponse,
    retry_mode="enabled",
)
CREATE_BBIP_ORDER = OperationSpec(
    name="promotion.bbip.create_order",
    method="PUT",
    path="/promotion/v1/items/services/bbip/orders/create",
    request_model=CreateBbipOrderRequest,
    retry_mode="enabled",
)
GET_BBIP_SUGGESTS = OperationSpec(
    name="promotion.bbip.get_suggests",
    method="POST",
    path="/promotion/v1/items/services/bbip/suggests/get",
    request_model=CreateBbipSuggestsRequest,
    response_model=BbipSuggestsResponse,
    retry_mode="enabled",
)
APPLY_TRX = OperationSpec(
    name="promotion.trx.apply",
    method="POST",
    path="/trx-promo/1/apply",
    request_model=CreateTrxPromotionApplyRequest,
    retry_mode="enabled",
)
CANCEL_TRX = OperationSpec(
    name="promotion.trx.cancel",
    method="POST",
    path="/trx-promo/1/cancel",
    request_model=CancelTrxPromotionRequest,
    retry_mode="enabled",
)
GET_TRX_COMMISSIONS = OperationSpec(
    name="promotion.trx.get_commissions",
    method="GET",
    path="/trx-promo/1/commissions",
    response_model=TrxCommissionsResponse,
)
GET_CPA_AUCTION_BIDS = OperationSpec(
    name="promotion.cpa_auction.get_user_bids",
    method="GET",
    path="/auction/1/bids",
    response_model=CpaAuctionBidsResponse,
)
CREATE_CPA_AUCTION_BIDS = OperationSpec(
    name="promotion.cpa_auction.create_item_bids",
    method="POST",
    path="/auction/1/bids",
    request_model=CreateItemBidsRequest,
    retry_mode="enabled",
)
GET_TARGET_ACTION_BIDS = OperationSpec(
    name="promotion.target_action.get_bids",
    method="GET",
    path="/cpxpromo/1/getBids/{item_id}",
    response_model=TargetActionGetBidsResponse,
)
GET_TARGET_ACTION_PROMOTIONS = OperationSpec(
    name="promotion.target_action.get_promotions_by_item_ids",
    method="POST",
    path="/cpxpromo/1/getPromotionsByItemIds",
    request_model=GetPromotionsByItemIdsRequest,
    response_model=TargetActionPromotionsResponse,
    retry_mode="enabled",
)
DELETE_TARGET_ACTION_PROMOTION = OperationSpec(
    name="promotion.target_action.delete_promotion",
    method="POST",
    path="/cpxpromo/1/remove",
    request_model=DeletePromotionRequest,
    retry_mode="enabled",
)
UPDATE_TARGET_ACTION_AUTO = OperationSpec(
    name="promotion.target_action.update_auto_bid",
    method="POST",
    path="/cpxpromo/1/setAuto",
    request_model=UpdateAutoBidRequest,
    retry_mode="enabled",
)
UPDATE_TARGET_ACTION_MANUAL = OperationSpec(
    name="promotion.target_action.update_manual_bid",
    method="POST",
    path="/cpxpromo/1/setManual",
    request_model=UpdateManualBidRequest,
    retry_mode="enabled",
)
CREATE_AUTOSTRATEGY_BUDGET = OperationSpec(
    name="promotion.autostrategy.create_budget",
    method="POST",
    path="/autostrategy/v1/budget",
    request_model=CreateAutostrategyBudgetRequest,
    response_model=AutostrategyBudgetResponse,
    retry_mode="enabled",
)
CREATE_AUTOSTRATEGY_CAMPAIGN = OperationSpec(
    name="promotion.autostrategy.create_campaign",
    method="POST",
    path="/autostrategy/v1/campaign/create",
    request_model=CreateAutostrategyCampaignRequest,
    response_model=CampaignActionResponse,
    retry_mode="enabled",
)
UPDATE_AUTOSTRATEGY_CAMPAIGN = OperationSpec(
    name="promotion.autostrategy.edit_campaign",
    method="POST",
    path="/autostrategy/v1/campaign/edit",
    request_model=UpdateAutostrategyCampaignRequest,
    response_model=CampaignActionResponse,
    retry_mode="enabled",
)
GET_AUTOSTRATEGY_CAMPAIGN = OperationSpec(
    name="promotion.autostrategy.get_campaign_info",
    method="POST",
    path="/autostrategy/v1/campaign/info",
    request_model=GetAutostrategyCampaignInfoRequest,
    response_model=CampaignDetailsResponse,
    retry_mode="enabled",
)
DELETE_AUTOSTRATEGY_CAMPAIGN = OperationSpec(
    name="promotion.autostrategy.stop_campaign",
    method="POST",
    path="/autostrategy/v1/campaign/stop",
    request_model=StopAutostrategyCampaignRequest,
    response_model=CampaignActionResponse,
    retry_mode="enabled",
)
LIST_AUTOSTRATEGY_CAMPAIGNS = OperationSpec(
    name="promotion.autostrategy.list_campaigns",
    method="POST",
    path="/autostrategy/v1/campaigns",
    request_model=ListAutostrategyCampaignsRequest,
    response_model=CampaignsResponse,
    retry_mode="enabled",
)
GET_AUTOSTRATEGY_STAT = OperationSpec(
    name="promotion.autostrategy.get_stat",
    method="POST",
    path="/autostrategy/v1/stat",
    request_model=GetAutostrategyStatRequest,
    response_model=AutostrategyStatResponse,
    retry_mode="enabled",
)

TRX_HEADERS = {
    "x-authenticated-userid": "7",
    "x-oauth-flow": "client_credentials",
}
