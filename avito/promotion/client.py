"""Внутренние section clients для пакета promotion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import RequestContext, Transport
from avito.core.mapping import request_public_model
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
    map_promotion_order_status,
    map_promotion_orders,
    map_promotion_service_dictionary,
    map_promotion_services,
    map_target_action_get_bids_out,
    map_target_action_get_promotions_by_item_ids_out,
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


@dataclass(slots=True)
class PromotionClient:
    """Выполняет HTTP-операции общего promotion API."""

    transport: Transport

    def get_service_dictionary(self) -> PromotionServiceDictionary:
        """Получает словарь услуг продвижения."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/dict",
            context=RequestContext("promotion.get_service_dictionary", allow_retry=True),
            mapper=map_promotion_service_dictionary,
        )

    def list_services(self, request: ListPromotionServicesRequest) -> PromotionServicesResult:
        """Получает список услуг продвижения по объявлениям."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/get",
            context=RequestContext("promotion.list_services", allow_retry=True),
            mapper=map_promotion_services,
            json_body=request.to_payload(),
        )

    def list_orders(self, request: ListPromotionOrdersRequest) -> PromotionOrdersResult:
        """Получает список заявок на продвижение."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/orders/get",
            context=RequestContext("promotion.list_orders", allow_retry=True),
            mapper=map_promotion_orders,
            json_body=request.to_payload(),
        )

    def get_order_status(
        self, request: GetPromotionOrderStatusRequest
    ) -> PromotionOrderStatusResult:
        """Получает статусы заявок на продвижение."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/orders/status",
            context=RequestContext("promotion.get_order_status", allow_retry=True),
            mapper=map_promotion_order_status,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class BbipClient:
    """Выполняет HTTP-операции BBIP-продвижения."""

    transport: Transport

    def get_forecasts(self, request: CreateBbipForecastsRequest) -> BbipForecastsResult:
        """Получает прогнозы BBIP по объявлениям."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/bbip/forecasts/get",
            context=RequestContext("promotion.bbip.get_forecasts", allow_retry=True),
            mapper=map_bbip_forecasts,
            json_body=request.to_payload(),
        )

    def create_order(
        self,
        request: CreateBbipOrderRequest,
        *,
        action: str = "create_order",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Подключает BBIP-услугу."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "PUT",
            "/promotion/v1/items/services/bbip/orders/create",
            context=RequestContext("promotion.bbip.create_order", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_ids": [item.item_id for item in request.items]},
            request_payload=payload_to_send,
        )

    def get_suggests(self, request: CreateBbipSuggestsRequest) -> BbipSuggestsResult:
        """Получает варианты бюджета BBIP."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/bbip/suggests/get",
            context=RequestContext("promotion.bbip.get_suggests", allow_retry=True),
            mapper=map_bbip_suggests,
            json_body=request.to_payload(),
        )


@dataclass(slots=True)
class TrxPromoClient:
    """Выполняет HTTP-операции TrxPromo."""

    transport: Transport

    def apply(
        self,
        request: CreateTrxPromotionApplyRequest,
        *,
        action: str = "apply",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Запускает TrxPromo."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/trx-promo/1/apply",
            context=RequestContext("promotion.trx.apply", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_ids": [item.item_id for item in request.items]},
            request_payload=payload_to_send,
        )

    def cancel(
        self,
        request: CancelTrxPromotionRequest,
        *,
        action: str = "delete",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Останавливает TrxPromo."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/trx-promo/1/cancel",
            context=RequestContext("promotion.trx.cancel", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_ids": list(request.item_ids)},
            request_payload=payload_to_send,
        )

    def get_commissions(self, *, item_ids: list[int] | None = None) -> TrxCommissionsResult:
        """Проверяет доступность TrxPromo и размер комиссий."""

        params = {"itemIDs": ",".join(str(item_id) for item_id in item_ids)} if item_ids else None
        return request_public_model(
            self.transport,
            "GET",
            "/trx-promo/1/commissions",
            context=RequestContext("promotion.trx.get_commissions"),
            mapper=map_trx_commissions,
            params=params,
        )


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

        return request_public_model(
            self.transport,
            "GET",
            "/auction/1/bids",
            context=RequestContext("promotion.cpa_auction.get_user_bids"),
            mapper=map_cpa_auction_bids,
            params={"fromItemID": from_item_id, "batchSize": batch_size},
        )

    def create_item_bids(
        self,
        request: CreateItemBidsRequest,
        *,
        action: str = "create_item_bids",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Сохраняет новые ставки."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/auction/1/bids",
            context=RequestContext("promotion.cpa_auction.create_item_bids", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_ids": [item.item_id for item in request.items]},
            request_payload=payload_to_send,
        )


@dataclass(slots=True)
class TargetActionPriceClient:
    """Выполняет HTTP-операции цены целевого действия."""

    transport: Transport

    def get_bids(self, *, item_id: int) -> TargetActionGetBidsResult:
        """Получает детализированные цены и бюджеты по объявлению."""

        return request_public_model(
            self.transport,
            "GET",
            f"/cpxpromo/1/getBids/{item_id}",
            context=RequestContext("promotion.target_action.get_bids"),
            mapper=map_target_action_get_bids_out,
        )

    def get_promotions_by_item_ids(
        self,
        request: GetPromotionsByItemIdsRequest,
    ) -> TargetActionPromotionsByItemIdsResult:
        """Получает текущие цены и бюджеты по нескольким объявлениям."""

        return request_public_model(
            self.transport,
            "POST",
            "/cpxpromo/1/getPromotionsByItemIds",
            context=RequestContext(
                "promotion.target_action.get_promotions_by_item_ids", allow_retry=True
            ),
            mapper=map_target_action_get_promotions_by_item_ids_out,
            json_body=request.to_payload(),
        )

    def delete_promotion(
        self,
        request: DeletePromotionRequest,
        *,
        action: str = "delete",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Останавливает продвижение с ценой целевого действия."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/remove",
            context=RequestContext("promotion.target_action.delete_promotion", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_id": request.item_id},
            request_payload=payload_to_send,
        )

    def update_auto_bid(
        self,
        request: UpdateAutoBidRequest,
        *,
        action: str = "update_auto",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Применяет автоматическую настройку."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/setAuto",
            context=RequestContext("promotion.target_action.update_auto_bid", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_id": request.item_id},
            request_payload=payload_to_send,
        )

    def update_manual_bid(
        self,
        request: UpdateManualBidRequest,
        *,
        action: str = "update_manual",
        target: Mapping[str, object] | None = None,
        request_payload: Mapping[str, object] | None = None,
    ) -> PromotionActionResult:
        """Применяет ручную настройку."""

        payload_to_send = (
            dict(request_payload) if request_payload is not None else request.to_payload()
        )
        payload = self.transport.request_json(
            "POST",
            "/cpxpromo/1/setManual",
            context=RequestContext("promotion.target_action.update_manual_bid", allow_retry=True),
            json_body=payload_to_send,
        )
        return map_promotion_action(
            payload,
            action=action,
            target=target or {"item_id": request.item_id},
            request_payload=payload_to_send,
        )


@dataclass(slots=True)
class AutostrategyClient:
    """Выполняет HTTP-операции автостратегии."""

    transport: Transport

    def create_budget(self, request: CreateAutostrategyBudgetRequest) -> AutostrategyBudget:
        """Рассчитывает бюджет кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/budget",
            context=RequestContext("promotion.autostrategy.create_budget", allow_retry=True),
            mapper=map_autostrategy_budget,
            json_body=request.to_payload(),
        )

    def create_campaign(self, request: CreateAutostrategyCampaignRequest) -> CampaignActionResult:
        """Создает новую кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/create",
            context=RequestContext("promotion.autostrategy.create_campaign", allow_retry=True),
            mapper=map_campaign_action,
            json_body=request.to_payload(),
        )

    def edit_campaign(self, request: UpdateAutostrategyCampaignRequest) -> CampaignActionResult:
        """Редактирует кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/edit",
            context=RequestContext("promotion.autostrategy.edit_campaign", allow_retry=True),
            mapper=map_campaign_action,
            json_body=request.to_payload(),
        )

    def get_campaign_info(self, request: GetAutostrategyCampaignInfoRequest) -> CampaignInfo:
        """Получает полную информацию о кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/info",
            context=RequestContext("promotion.autostrategy.get_campaign_info", allow_retry=True),
            mapper=map_campaign_info,
            json_body=request.to_payload(),
        )

    def stop_campaign(self, request: StopAutostrategyCampaignRequest) -> CampaignActionResult:
        """Останавливает кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/stop",
            context=RequestContext("promotion.autostrategy.stop_campaign", allow_retry=True),
            mapper=map_campaign_action,
            json_body=request.to_payload(),
        )

    def list_campaigns(self, request: ListAutostrategyCampaignsRequest) -> CampaignsResult:
        """Получает список кампаний."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaigns",
            context=RequestContext("promotion.autostrategy.list_campaigns", allow_retry=True),
            mapper=map_campaigns,
            json_body=request.to_payload(),
        )

    def get_stat(self, request: GetAutostrategyStatRequest) -> AutostrategyStat:
        """Получает статистику кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/stat",
            context=RequestContext("promotion.autostrategy.get_stat", allow_retry=True),
            mapper=map_autostrategy_stat,
            json_body=request.to_payload(),
        )


__all__ = (
    "AutostrategyClient",
    "BbipClient",
    "CpaAuctionClient",
    "PromotionClient",
    "TargetActionPriceClient",
    "TrxPromoClient",
)
