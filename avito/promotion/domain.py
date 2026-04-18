"""Доменные объекты пакета promotion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from avito.core import Transport
from avito.promotion.client import (
    AutostrategyClient,
    BbipClient,
    CpaAuctionClient,
    PromotionClient,
    TargetActionPriceClient,
    TrxPromoClient,
)
from avito.promotion.models import (
    AutostrategyBudget,
    AutostrategyStat,
    BbipForecastRequestItem,
    BbipForecastsResult,
    BbipOrderItem,
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
    PromotionOrderStatusesResult,
    PromotionServiceDictionary,
    PromotionServicesResult,
    StopAutostrategyCampaignRequest,
    TargetActionPromotionsResult,
    TrxCommissionsResult,
    TrxPromotionApplyItem,
    UpdateAutoBidRequest,
    UpdateAutostrategyCampaignRequest,
    UpdateManualBidRequest,
)


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела promotion."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class PromotionOrder(DomainObject):
    """Доменный объект заявок и словарей promotion API."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_service_dictionary(self) -> PromotionServiceDictionary:
        """Получает словарь услуг продвижения."""

        return PromotionClient(self.transport).get_service_dictionary()

    def list_services(self, *, item_ids: list[int]) -> PromotionServicesResult:
        """Получает список услуг продвижения по объявлениям."""

        return PromotionClient(self.transport).list_services(ListPromotionServicesRequest(item_ids=item_ids))

    def list_orders(
        self,
        *,
        item_ids: list[int] | None = None,
        order_ids: list[str] | None = None,
    ) -> PromotionOrdersResult:
        """Получает список заявок на продвижение."""

        return PromotionClient(self.transport).list_orders(
            ListPromotionOrdersRequest(item_ids=item_ids, order_ids=order_ids)
        )

    def get_order_status(self, *, order_ids: list[str] | None = None) -> PromotionOrderStatusesResult:
        """Получает статусы заявок на продвижение."""

        resolved_order_ids = order_ids or ([str(self.resource_id)] if self.resource_id is not None else [])
        if not resolved_order_ids:
            raise ValueError("Для операции требуется хотя бы один `order_id`.")
        return PromotionClient(self.transport).get_order_status(
            GetPromotionOrderStatusRequest(order_ids=resolved_order_ids)
        )


@dataclass(slots=True, frozen=True)
class BbipPromotion(DomainObject):
    """Доменный объект BBIP-продвижения."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_forecasts(self, *, items: list[BbipForecastRequestItem]) -> BbipForecastsResult:
        """Получает прогнозы BBIP."""

        return BbipClient(self.transport).get_forecasts(CreateBbipForecastsRequest(items=items))

    def create_order(self, *, items: list[BbipOrderItem]) -> PromotionActionResult:
        """Подключает BBIP-продвижение."""

        return BbipClient(self.transport).create_order(CreateBbipOrderRequest(items=items))

    def get_suggests(self, *, item_ids: list[int] | None = None) -> BbipSuggestsResult:
        """Получает варианты бюджета BBIP."""

        resolved_item_ids = item_ids or self._resource_item_ids()
        return BbipClient(self.transport).get_suggests(CreateBbipSuggestsRequest(item_ids=resolved_item_ids))

    def _resource_item_ids(self) -> list[int]:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id` или список `item_ids`.")
        return [int(self.resource_id)]


@dataclass(slots=True, frozen=True)
class TrxPromotion(DomainObject):
    """Доменный объект TrxPromo."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def apply(self, *, items: list[TrxPromotionApplyItem]) -> PromotionActionResult:
        """Запускает TrxPromo."""

        return TrxPromoClient(self.transport).apply(CreateTrxPromotionApplyRequest(items=items))

    def delete(self, *, item_ids: list[int] | None = None) -> PromotionActionResult:
        """Останавливает TrxPromo."""

        resolved_item_ids = item_ids or self._resource_item_ids()
        return TrxPromoClient(self.transport).cancel(CancelTrxPromotionRequest(item_ids=resolved_item_ids))

    def get_commissions(self, *, item_ids: list[int] | None = None) -> TrxCommissionsResult:
        """Получает доступные комиссии TrxPromo."""

        return TrxPromoClient(self.transport).get_commissions(item_ids=item_ids or self._resource_item_ids())

    def _resource_item_ids(self) -> list[int]:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id` или список `item_ids`.")
        return [int(self.resource_id)]


@dataclass(slots=True, frozen=True)
class CpaAuction(DomainObject):
    """Доменный объект CPA-аукциона."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_user_bids(
        self,
        *,
        from_item_id: int | None = None,
        batch_size: int | None = None,
    ) -> CpaAuctionBidsResult:
        """Получает действующие и доступные ставки."""

        return CpaAuctionClient(self.transport).get_user_bids(
            from_item_id=from_item_id,
            batch_size=batch_size,
        )

    def create_item_bids(self, *, items: list[CreateItemBid]) -> PromotionActionResult:
        """Сохраняет новые ставки по объявлениям."""

        return CpaAuctionClient(self.transport).create_item_bids(CreateItemBidsRequest(items=items))


@dataclass(slots=True, frozen=True)
class TargetActionPricing(DomainObject):
    """Доменный объект цены целевого действия."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_bids(self, *, item_id: int | None = None) -> TargetActionPromotionsResult:
        """Получает детализированные цены и бюджеты."""

        return TargetActionPriceClient(self.transport).get_bids(item_id=item_id or self._require_item_id())

    def get_promotions_by_item_ids(self, *, item_ids: list[int] | None = None) -> TargetActionPromotionsResult:
        """Получает текущие настройки по нескольким объявлениям."""

        resolved_item_ids = item_ids or [self._require_item_id()]
        return TargetActionPriceClient(self.transport).get_promotions_by_item_ids(
            GetPromotionsByItemIdsRequest(item_ids=resolved_item_ids)
        )

    def delete(self, *, item_id: int | None = None) -> PromotionActionResult:
        """Останавливает продвижение."""

        return TargetActionPriceClient(self.transport).delete_promotion(
            DeletePromotionRequest(item_id=item_id or self._require_item_id())
        )

    def update_auto(
        self,
        *,
        action_type_id: int,
        budget_penny: int,
        budget_type: str,
        item_id: int | None = None,
    ) -> PromotionActionResult:
        """Применяет автоматическую настройку."""

        return TargetActionPriceClient(self.transport).update_auto_bid(
            UpdateAutoBidRequest(
                item_id=item_id or self._require_item_id(),
                action_type_id=action_type_id,
                budget_penny=budget_penny,
                budget_type=budget_type,
            )
        )

    def update_manual(
        self,
        *,
        action_type_id: int,
        bid_penny: int,
        limit_penny: int | None = None,
        item_id: int | None = None,
    ) -> PromotionActionResult:
        """Применяет ручную настройку."""

        return TargetActionPriceClient(self.transport).update_manual_bid(
            UpdateManualBidRequest(
                item_id=item_id or self._require_item_id(),
                action_type_id=action_type_id,
                bid_penny=bid_penny,
                limit_penny=limit_penny,
            )
        )

    def _require_item_id(self) -> int:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `item_id`.")
        return int(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutostrategyCampaign(DomainObject):
    """Доменный объект кампаний автостратегии."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_budget(self, *, payload: Mapping[str, object]) -> AutostrategyBudget:
        """Рассчитывает бюджет кампании."""

        return AutostrategyClient(self.transport).create_budget(CreateAutostrategyBudgetRequest(payload=payload))

    def create(self, *, payload: Mapping[str, object]) -> CampaignActionResult:
        """Создает новую кампанию."""

        return AutostrategyClient(self.transport).create_campaign(
            CreateAutostrategyCampaignRequest(payload=payload)
        )

    def update(self, *, payload: Mapping[str, object]) -> CampaignActionResult:
        """Редактирует кампанию."""

        return AutostrategyClient(self.transport).edit_campaign(
            UpdateAutostrategyCampaignRequest(payload=payload)
        )

    def get(self, *, campaign_id: int | None = None) -> CampaignInfo:
        """Получает полную информацию о кампании."""

        return AutostrategyClient(self.transport).get_campaign_info(
            GetAutostrategyCampaignInfoRequest(campaign_id=campaign_id or self._require_campaign_id())
        )

    def delete(self, *, campaign_id: int | None = None) -> CampaignActionResult:
        """Останавливает кампанию."""

        return AutostrategyClient(self.transport).stop_campaign(
            StopAutostrategyCampaignRequest(campaign_id=campaign_id or self._require_campaign_id())
        )

    def list(self, *, payload: Mapping[str, object] | None = None) -> CampaignsResult:
        """Получает список кампаний."""

        return AutostrategyClient(self.transport).list_campaigns(
            ListAutostrategyCampaignsRequest(payload=payload or {})
        )

    def get_stat(self, *, campaign_id: int | None = None) -> AutostrategyStat:
        """Получает статистику кампании."""

        return AutostrategyClient(self.transport).get_stat(
            GetAutostrategyStatRequest(campaign_id=campaign_id or self._require_campaign_id())
        )

    def _require_campaign_id(self) -> int:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `campaign_id`.")
        return int(self.resource_id)


__all__ = (
    "AutostrategyCampaign",
    "BbipPromotion",
    "CpaAuction",
    "DomainObject",
    "PromotionOrder",
    "TargetActionPricing",
    "TrxPromotion",
)
