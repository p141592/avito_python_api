"""Внутренние section clients для пакета promotion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from avito.core import RequestContext, Transport
from avito.core.mapping import request_public_model
from avito.promotion.enums import CampaignType, TargetActionBudgetType
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
    BbipItem,
    BbipSuggestsResult,
    CampaignActionResult,
    CampaignDetailsResult,
    CampaignListFilter,
    CampaignOrderBy,
    CampaignsResult,
    CancelTrxPromotionRequest,
    CpaAuctionBidsResult,
    CreateAutostrategyBudgetRequest,
    CreateAutostrategyCampaignRequest,
    CreateBbipForecastsRequest,
    CreateBbipOrderRequest,
    CreateBbipSuggestsRequest,
    CreateItemBid,
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
    TrxItem,
    UpdateAutoBidRequest,
    UpdateAutostrategyCampaignRequest,
    UpdateManualBidRequest,
)

_TRX_HEADERS = {
    "x-authenticated-userid": "7",
    "x-oauth-flow": "client_credentials",
}


@dataclass(slots=True, frozen=True)
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

    def list_services(self, *, item_ids: list[int]) -> PromotionServicesResult:
        """Получает список услуг продвижения по объявлениям."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/get",
            context=RequestContext("promotion.list_services", allow_retry=True),
            mapper=map_promotion_services,
            json_body=ListPromotionServicesRequest(item_ids=item_ids).to_payload(),
        )

    def list_orders(
        self, *, item_ids: list[int] | None = None, order_ids: list[str] | None = None
    ) -> PromotionOrdersResult:
        """Получает список заявок на продвижение."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/orders/get",
            context=RequestContext("promotion.list_orders", allow_retry=True),
            mapper=map_promotion_orders,
            json_body=ListPromotionOrdersRequest(item_ids=item_ids, order_ids=order_ids).to_payload(),
        )

    def get_order_status(self, *, order_ids: list[str]) -> PromotionOrderStatusResult:
        """Получает статусы заявок на продвижение."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/orders/status",
            context=RequestContext("promotion.get_order_status", allow_retry=True),
            mapper=map_promotion_order_status,
            json_body=GetPromotionOrderStatusRequest(order_ids=order_ids).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class BbipClient:
    """Выполняет HTTP-операции BBIP-продвижения."""

    transport: Transport

    def get_forecasts(self, *, items: list[BbipItem]) -> BbipForecastsResult:
        """Получает прогнозы BBIP по объявлениям."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/bbip/forecasts/get",
            context=RequestContext("promotion.bbip.get_forecasts", allow_retry=True),
            mapper=map_bbip_forecasts,
            json_body=CreateBbipForecastsRequest(items=items).to_payload(),
        )

    def create_order(
        self,
        *,
        items: list[BbipItem],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Подключает BBIP-услугу."""

        payload_to_send = CreateBbipOrderRequest(items=items).to_payload()
        return self.transport.request_public_model(
            "PUT",
            "/promotion/v1/items/services/bbip/orders/create",
            context=RequestContext(
                "promotion.bbip.create_order",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="create_order",
                target={"item_ids": [item.item_id for item in items]},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )

    def get_suggests(self, *, item_ids: list[int]) -> BbipSuggestsResult:
        """Получает варианты бюджета BBIP."""

        return request_public_model(
            self.transport,
            "POST",
            "/promotion/v1/items/services/bbip/suggests/get",
            context=RequestContext("promotion.bbip.get_suggests", allow_retry=True),
            mapper=map_bbip_suggests,
            json_body=CreateBbipSuggestsRequest(item_ids=item_ids).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class TrxPromoClient:
    """Выполняет HTTP-операции TrxPromo."""

    transport: Transport

    def apply(
        self,
        *,
        items: list[TrxItem],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Запускает TrxPromo."""

        payload_to_send = CreateTrxPromotionApplyRequest(items=items).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/trx-promo/1/apply",
            context=RequestContext("promotion.trx.apply", allow_retry=idempotency_key is not None),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="apply",
                target={"item_ids": [item.item_id for item in items]},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            headers=_TRX_HEADERS,
            idempotency_key=idempotency_key,
        )

    def cancel(
        self,
        *,
        item_ids: list[int],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Останавливает TrxPromo."""

        payload_to_send = CancelTrxPromotionRequest(item_ids=item_ids).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/trx-promo/1/cancel",
            context=RequestContext("promotion.trx.cancel", allow_retry=idempotency_key is not None),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="delete",
                target={"item_ids": list(item_ids)},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            headers=_TRX_HEADERS,
            idempotency_key=idempotency_key,
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
            headers=_TRX_HEADERS,
        )


@dataclass(slots=True, frozen=True)
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
        *,
        items: list[CreateItemBid],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Сохраняет новые ставки."""

        payload_to_send = CreateItemBidsRequest(items=items).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/auction/1/bids",
            context=RequestContext(
                "promotion.cpa_auction.create_item_bids",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="create_item_bids",
                target={"item_ids": [item.item_id for item in items]},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
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
        item_ids: list[int],
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
            json_body=GetPromotionsByItemIdsRequest(item_ids=item_ids).to_payload(),
        )

    def delete_promotion(
        self,
        *,
        item_id: int,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Останавливает продвижение с ценой целевого действия."""

        payload_to_send = DeletePromotionRequest(item_id=item_id).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/cpxpromo/1/remove",
            context=RequestContext(
                "promotion.target_action.delete_promotion",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="delete",
                target={"item_id": item_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )

    def update_auto_bid(
        self,
        *,
        item_id: int,
        action_type_id: int,
        budget_penny: int,
        budget_type: TargetActionBudgetType | str,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет автоматическую настройку."""

        payload_to_send = UpdateAutoBidRequest(
            item_id=item_id,
            action_type_id=action_type_id,
            budget_penny=budget_penny,
            budget_type=budget_type,
        ).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/cpxpromo/1/setAuto",
            context=RequestContext(
                "promotion.target_action.update_auto_bid",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="update_auto",
                target={"item_id": item_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )

    def update_manual_bid(
        self,
        *,
        item_id: int,
        action_type_id: int,
        bid_penny: int,
        limit_penny: int | None = None,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет ручную настройку."""

        payload_to_send = UpdateManualBidRequest(
            item_id=item_id,
            action_type_id=action_type_id,
            bid_penny=bid_penny,
            limit_penny=limit_penny,
        ).to_payload()
        return self.transport.request_public_model(
            "POST",
            "/cpxpromo/1/setManual",
            context=RequestContext(
                "promotion.target_action.update_manual_bid",
                allow_retry=idempotency_key is not None,
            ),
            mapper=lambda payload: map_promotion_action(
                payload,
                action="update_manual",
                target={"item_id": item_id},
                request_payload=payload_to_send,
            ),
            json_body=payload_to_send,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class AutostrategyClient:
    """Выполняет HTTP-операции автостратегии."""

    transport: Transport

    def create_budget(
        self,
        *,
        campaign_type: CampaignType | str,
        start_time: datetime | None = None,
        finish_time: datetime | None = None,
        items: list[int] | None = None,
    ) -> AutostrategyBudget:
        """Рассчитывает бюджет кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/budget",
            context=RequestContext("promotion.autostrategy.create_budget", allow_retry=True),
            mapper=map_autostrategy_budget,
            json_body=CreateAutostrategyBudgetRequest(
                campaign_type=campaign_type,
                start_time=start_time,
                finish_time=finish_time,
                items=items,
            ).to_payload(),
        )

    def create_campaign(
        self,
        *,
        campaign_type: CampaignType | str,
        title: str,
        budget: int | None = None,
        budget_bonus: int | None = None,
        budget_real: int | None = None,
        calc_id: int | None = None,
        description: str | None = None,
        finish_time: datetime | None = None,
        items: list[int] | None = None,
        start_time: datetime | None = None,
        idempotency_key: str | None = None,
    ) -> CampaignActionResult:
        """Создает новую кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/create",
            context=RequestContext(
                "promotion.autostrategy.create_campaign",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_campaign_action,
            json_body=CreateAutostrategyCampaignRequest(
                campaign_type=campaign_type,
                title=title,
                budget=budget,
                budget_bonus=budget_bonus,
                budget_real=budget_real,
                calc_id=calc_id,
                description=description,
                finish_time=finish_time,
                items=items,
                start_time=start_time,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def edit_campaign(
        self,
        *,
        campaign_id: int,
        version: int,
        budget: int | None = None,
        calc_id: int | None = None,
        description: str | None = None,
        finish_time: datetime | None = None,
        items: list[int] | None = None,
        start_time: datetime | None = None,
        title: str | None = None,
        idempotency_key: str | None = None,
    ) -> CampaignActionResult:
        """Редактирует кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/edit",
            context=RequestContext(
                "promotion.autostrategy.edit_campaign",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_campaign_action,
            json_body=UpdateAutostrategyCampaignRequest(
                campaign_id=campaign_id,
                version=version,
                budget=budget,
                calc_id=calc_id,
                description=description,
                finish_time=finish_time,
                items=items,
                start_time=start_time,
                title=title,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_campaign_info(self, *, campaign_id: int) -> CampaignDetailsResult:
        """Получает полную информацию о кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/info",
            context=RequestContext("promotion.autostrategy.get_campaign_info", allow_retry=True),
            mapper=map_campaign_info,
            json_body=GetAutostrategyCampaignInfoRequest(campaign_id=campaign_id).to_payload(),
        )

    def stop_campaign(
        self,
        *,
        campaign_id: int,
        version: int,
        idempotency_key: str | None = None,
    ) -> CampaignActionResult:
        """Останавливает кампанию."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaign/stop",
            context=RequestContext(
                "promotion.autostrategy.stop_campaign",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_campaign_action,
            json_body=StopAutostrategyCampaignRequest(
                campaign_id=campaign_id,
                version=version,
            ).to_payload(),
            idempotency_key=idempotency_key,
        )

    def list_campaigns(
        self,
        *,
        limit: int = 100,
        offset: int | None = None,
        status_id: list[int] | None = None,
        order_by: list[CampaignOrderBy] | None = None,
        filter: CampaignListFilter | None = None,
    ) -> CampaignsResult:
        """Получает список кампаний."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/campaigns",
            context=RequestContext("promotion.autostrategy.list_campaigns", allow_retry=True),
            mapper=map_campaigns,
            json_body=ListAutostrategyCampaignsRequest(
                limit=limit,
                offset=offset,
                status_id=status_id,
                order_by=order_by,
                filter=filter,
            ).to_payload(),
        )

    def get_stat(self, *, campaign_id: int) -> AutostrategyStat:
        """Получает статистику кампании."""

        return request_public_model(
            self.transport,
            "POST",
            "/autostrategy/v1/stat",
            context=RequestContext("promotion.autostrategy.get_stat", allow_retry=True),
            mapper=map_autostrategy_stat,
            json_body=GetAutostrategyStatRequest(campaign_id=campaign_id).to_payload(),
        )


__all__ = (
    "AutostrategyClient",
    "BbipClient",
    "CpaAuctionClient",
    "PromotionClient",
    "TargetActionPriceClient",
    "TrxPromoClient",
)
