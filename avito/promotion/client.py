"""Внутренние section clients для пакета promotion."""

from __future__ import annotations

from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.promotion.mappers import (
    map_autostrategy_budget,
    map_autostrategy_stat,
    map_bbip_forecasts,
    map_bbip_suggests,
    map_campaign_action,
    map_campaign_info,
    map_campaigns,
    map_cpa_auction_bids,
    map_promotion_action,
    map_promotion_order_statuses,
    map_promotion_orders,
    map_promotion_service_dictionary,
    map_promotion_services,
    map_target_action_promotions,
    map_trx_commissions,
)
from avito.promotion.models import (
    AutostrategyBudget,
    AutostrategyStat,
    BbipForecastsResult,
    BbipSuggestsResult,
    CampaignActionResult,
    CampaignInfo,
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
    PromotionActionResult,
    PromotionOrdersResult,
    PromotionOrderStatusesResult,
    PromotionServiceDictionary,
    PromotionServicesResult,
    StopAutostrategyCampaignRequest,
    TargetActionPromotionsResult,
    TrxCommissionsResult,
    UpdateAutoBidRequest,
    UpdateAutostrategyCampaignRequest,
    UpdateManualBidRequest,
)


@dataclass(slots=True)
class PromotionClient:
    """Выполняет HTTP-операции общего promotion API."""

    transport: Transport

    def get_service_dictionary(self) -> PromotionServiceDictionary:
        """Получает словарь услуг продвижения."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/dict",
            context=RequestContext("promotion.get_service_dictionary", allow_retry=True),
        )
        return map_promotion_service_dictionary(payload)

    def list_services(self, request: ListPromotionServicesRequest) -> PromotionServicesResult:
        """Получает список услуг продвижения по объявлениям."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/get",
            context=RequestContext("promotion.list_services", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_services(payload)

    def list_orders(self, request: ListPromotionOrdersRequest) -> PromotionOrdersResult:
        """Получает список заявок на продвижение."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/orders/get",
            context=RequestContext("promotion.list_orders", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_orders(payload)

    def get_order_status(
        self, request: GetPromotionOrderStatusRequest
    ) -> PromotionOrderStatusesResult:
        """Получает статусы заявок на продвижение."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/orders/status",
            context=RequestContext("promotion.get_order_status", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_order_statuses(payload)


@dataclass(slots=True)
class BbipClient:
    """Выполняет HTTP-операции BBIP-продвижения."""

    transport: Transport

    def get_forecasts(self, request: CreateBbipForecastsRequest) -> BbipForecastsResult:
        """Получает прогнозы BBIP по объявлениям."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/bbip/forecasts/get",
            context=RequestContext("promotion.bbip.get_forecasts", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_bbip_forecasts(payload)

    def create_order(self, request: CreateBbipOrderRequest) -> PromotionActionResult:
        """Подключает BBIP-услугу."""

        payload = self.transport.request_json(
            "PUT",
            "/promotion/v1/items/services/bbip/orders/create",
            context=RequestContext("promotion.bbip.create_order", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)

    def get_suggests(self, request: CreateBbipSuggestsRequest) -> BbipSuggestsResult:
        """Получает варианты бюджета BBIP."""

        payload = self.transport.request_json(
            "POST",
            "/promotion/v1/items/services/bbip/suggests/get",
            context=RequestContext("promotion.bbip.get_suggests", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_bbip_suggests(payload)


@dataclass(slots=True)
class TrxPromoClient:
    """Выполняет HTTP-операции TrxPromo."""

    transport: Transport

    def apply(self, request: CreateTrxPromotionApplyRequest) -> PromotionActionResult:
        """Запускает TrxPromo."""

        payload = self.transport.request_json(
            "POST",
            "/trx-promo/1/apply",
            context=RequestContext("promotion.trx.apply", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)

    def cancel(self, request: CancelTrxPromotionRequest) -> PromotionActionResult:
        """Останавливает TrxPromo."""

        payload = self.transport.request_json(
            "POST",
            "/trx-promo/1/cancel",
            context=RequestContext("promotion.trx.cancel", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)

    def get_commissions(self, *, item_ids: list[int] | None = None) -> TrxCommissionsResult:
        """Проверяет доступность TrxPromo и размер комиссий."""

        params = {"itemIDs": ",".join(str(item_id) for item_id in item_ids)} if item_ids else None
        payload = self.transport.request_json(
            "GET",
            "/trx-promo/1/commissions",
            context=RequestContext("promotion.trx.get_commissions"),
            params=params,
        )
        return map_trx_commissions(payload)


@dataclass(slots=True)
class CpaAuctionClient:
    """Выполняет HTTP-операции CPA-аукциона."""

    transport: Transport

    def get_user_bids(
        self,
        *,
        from_item_id: int | None = None,
        batch_size: int | None = None,
    ) -> CpaAuctionBidsResult:
        """Получает действующие и доступные ставки."""

        payload = self.transport.request_json(
            "GET",
            "/auction/1/bids",
            context=RequestContext("promotion.cpa_auction.get_user_bids"),
            params={"fromItemID": from_item_id, "batchSize": batch_size},
        )
        return map_cpa_auction_bids(payload)

    def create_item_bids(self, request: CreateItemBidsRequest) -> PromotionActionResult:
        """Сохраняет новые ставки."""

        payload = self.transport.request_json(
            "POST",
            "/auction/1/bids",
            context=RequestContext("promotion.cpa_auction.create_item_bids", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)


@dataclass(slots=True)
class TargetActionPriceClient:
    """Выполняет HTTP-операции цены целевого действия."""

    transport: Transport

    def get_bids(self, *, item_id: int) -> TargetActionPromotionsResult:
        """Получает детализированные цены и бюджеты по объявлению."""

        payload = self.transport.request_json(
            "GET",
            f"/cpxpromo/1/getBids/{item_id}",
            context=RequestContext("promotion.target_action.get_bids"),
        )
        return map_target_action_promotions(payload)

    def get_promotions_by_item_ids(
        self,
        request: GetPromotionsByItemIdsRequest,
    ) -> TargetActionPromotionsResult:
        """Получает текущие цены и бюджеты по нескольким объявлениям."""

        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/getPromotionsByItemIds",
            context=RequestContext(
                "promotion.target_action.get_promotions_by_item_ids", allow_retry=True
            ),
            json_body=request.to_payload(),
        )
        return map_target_action_promotions(payload)

    def delete_promotion(self, request: DeletePromotionRequest) -> PromotionActionResult:
        """Останавливает продвижение с ценой целевого действия."""

        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/remove",
            context=RequestContext("promotion.target_action.delete_promotion", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)

    def update_auto_bid(self, request: UpdateAutoBidRequest) -> PromotionActionResult:
        """Применяет автоматическую настройку."""

        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/setAuto",
            context=RequestContext("promotion.target_action.update_auto_bid", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)

    def update_manual_bid(self, request: UpdateManualBidRequest) -> PromotionActionResult:
        """Применяет ручную настройку."""

        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/setManual",
            context=RequestContext("promotion.target_action.update_manual_bid", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_promotion_action(payload)


@dataclass(slots=True)
class AutostrategyClient:
    """Выполняет HTTP-операции автостратегии."""

    transport: Transport

    def create_budget(self, request: CreateAutostrategyBudgetRequest) -> AutostrategyBudget:
        """Рассчитывает бюджет кампании."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/budget",
            context=RequestContext("promotion.autostrategy.create_budget", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_autostrategy_budget(payload)

    def create_campaign(self, request: CreateAutostrategyCampaignRequest) -> CampaignActionResult:
        """Создает новую кампанию."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/campaign/create",
            context=RequestContext("promotion.autostrategy.create_campaign", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_campaign_action(payload)

    def edit_campaign(self, request: UpdateAutostrategyCampaignRequest) -> CampaignActionResult:
        """Редактирует кампанию."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/campaign/edit",
            context=RequestContext("promotion.autostrategy.edit_campaign", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_campaign_action(payload)

    def get_campaign_info(self, request: GetAutostrategyCampaignInfoRequest) -> CampaignInfo:
        """Получает полную информацию о кампании."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/campaign/info",
            context=RequestContext("promotion.autostrategy.get_campaign_info", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_campaign_info(payload)

    def stop_campaign(self, request: StopAutostrategyCampaignRequest) -> CampaignActionResult:
        """Останавливает кампанию."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/campaign/stop",
            context=RequestContext("promotion.autostrategy.stop_campaign", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_campaign_action(payload)

    def list_campaigns(self, request: ListAutostrategyCampaignsRequest) -> CampaignsResult:
        """Получает список кампаний."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/campaigns",
            context=RequestContext("promotion.autostrategy.list_campaigns", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_campaigns(payload)

    def get_stat(self, request: GetAutostrategyStatRequest) -> AutostrategyStat:
        """Получает статистику кампании."""

        payload = self.transport.request_json(
            "POST",
            "/autostrategy/v1/stat",
            context=RequestContext("promotion.autostrategy.get_stat", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_autostrategy_stat(payload)


__all__ = (
    "AutostrategyClient",
    "BbipClient",
    "CpaAuctionClient",
    "PromotionClient",
    "TargetActionPriceClient",
    "TrxPromoClient",
)
