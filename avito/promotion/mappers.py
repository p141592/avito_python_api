"""Мапперы JSON -> dataclass для пакета promotion."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from avito.core.exceptions import ResponseMappingError
from avito.promotion.models import (
    AutostrategyBudget,
    AutostrategyBudgetPoint,
    AutostrategyPriceRange,
    AutostrategyStat,
    BbipBudgetOption,
    BbipDurationRange,
    BbipForecast,
    BbipForecastsResult,
    BbipSuggest,
    BbipSuggestsResult,
    CampaignActionResult,
    CampaignInfo,
    CampaignsResult,
    CpaAuctionBidOption,
    CpaAuctionBidsResult,
    CpaAuctionItemBid,
    PromotionActionItem,
    PromotionActionResult,
    PromotionOrderInfo,
    PromotionOrdersResult,
    PromotionOrderStatus,
    PromotionOrderStatusesResult,
    PromotionService,
    PromotionServiceDictionary,
    PromotionServicesResult,
    PromotionServiceType,
    TargetActionBid,
    TargetActionPromotion,
    TargetActionPromotionsResult,
    TrxCommissionInfo,
    TrxCommissionRange,
    TrxCommissionsResult,
)

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


def _mapping(payload: Payload, *keys: str) -> Payload:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return cast(Payload, value)
    return {}


def _str(payload: Payload, *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None


def _int(payload: Payload, *keys: str) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
    return None


def _bool(payload: Payload, *keys: str) -> bool | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def _items_payload(payload: Payload) -> list[Payload]:
    return _list(payload, "items", "result", "services", "orders", "campaigns")


def map_promotion_service_dictionary(payload: object) -> PromotionServiceDictionary:
    """Преобразует словарь услуг продвижения."""

    data = _expect_mapping(payload)
    return PromotionServiceDictionary(
        items=[
            PromotionServiceType(
                code=_str(item, "code", "serviceCode", "id"),
                title=_str(item, "title", "name", "description"),
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_promotion_services(payload: object) -> PromotionServicesResult:
    """Преобразует список услуг продвижения."""

    data = _expect_mapping(payload)
    return PromotionServicesResult(
        items=[
            PromotionService(
                item_id=_int(item, "itemId", "itemID"),
                service_code=_str(item, "serviceCode", "code"),
                service_name=_str(item, "serviceName", "name", "title"),
                price=_int(item, "price", "pricePenny"),
                status=_str(item, "status"),
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_promotion_orders(payload: object) -> PromotionOrdersResult:
    """Преобразует список заявок на продвижение."""

    data = _expect_mapping(payload)
    return PromotionOrdersResult(
        items=[
            PromotionOrderInfo(
                order_id=_str(item, "orderId", "orderID", "id"),
                item_id=_int(item, "itemId", "itemID"),
                service_code=_str(item, "serviceCode", "code"),
                status=_str(item, "status"),
                created_at=_str(item, "createdAt", "created_at"),
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_promotion_order_statuses(payload: object) -> PromotionOrderStatusesResult:
    """Преобразует статусы заявок на продвижение."""

    data = _expect_mapping(payload)
    return PromotionOrderStatusesResult(
        items=[
            PromotionOrderStatus(
                order_id=_str(item, "orderId", "orderID", "id"),
                status=_str(item, "status"),
                message=_str(item, "message", "description"),
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_bbip_forecasts(payload: object) -> BbipForecastsResult:
    """Преобразует прогнозы BBIP."""

    data = _expect_mapping(payload)
    return BbipForecastsResult(
        items=[
            BbipForecast(
                item_id=_int(item, "itemId", "itemID"),
                min_views=_int(item, "min"),
                max_views=_int(item, "max"),
                total_price=_int(item, "totalPrice"),
                total_old_price=_int(item, "totalOldPrice"),
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_promotion_action(payload: object) -> PromotionActionResult:
    """Преобразует результат действия по продвижению."""

    data = _expect_mapping(payload)
    items_payload = _items_payload(data)
    if not items_payload:
        success_payload = _mapping(data, "success")
        items_payload = _list(success_payload, "items", "result")
    return PromotionActionResult(
        items=[
            PromotionActionItem(
                item_id=_int(item, "itemId", "itemID"),
                success=bool(item.get("success", True)),
                status=_str(item, "status"),
                message=_str(_mapping(item, "error"), "message") or _str(item, "message"),
                raw_payload=item,
            )
            for item in items_payload
        ],
        raw_payload=data,
    )


def map_bbip_suggests(payload: object) -> BbipSuggestsResult:
    """Преобразует варианты бюджета BBIP."""

    data = _expect_mapping(payload)
    return BbipSuggestsResult(
        items=[
            BbipSuggest(
                item_id=_int(item, "itemId", "itemID"),
                duration=_map_bbip_duration(_mapping(item, "duration")),
                budgets=[_map_bbip_budget(option) for option in _list(item, "budgets")],
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def _map_bbip_budget(payload: Payload) -> BbipBudgetOption:
    return BbipBudgetOption(
        price=_int(payload, "price"),
        old_price=_int(payload, "oldPrice"),
        is_recommended=_bool(payload, "isRecommended"),
        raw_payload=payload,
    )


def _map_bbip_duration(payload: Payload) -> BbipDurationRange | None:
    if not payload:
        return None
    return BbipDurationRange(
        start=_int(payload, "from"),
        stop=_int(payload, "to"),
        recommended=_int(payload, "recommended"),
        raw_payload=payload,
    )


def map_trx_commissions(payload: object) -> TrxCommissionsResult:
    """Преобразует комиссии TrxPromo."""

    data = _expect_mapping(payload)
    items_payload = _items_payload(data)
    if not items_payload:
        success_payload = _mapping(data, "success")
        items_payload = _list(success_payload, "items", "result")
    return TrxCommissionsResult(
        items=[
            TrxCommissionInfo(
                item_id=_int(item, "itemId", "itemID"),
                commission=_int(item, "commission"),
                is_active=_bool(item, "isActive", "active"),
                valid_commission_range=_map_trx_range(_mapping(item, "validCommissionRange")),
                raw_payload=item,
            )
            for item in items_payload
        ],
        raw_payload=data,
    )


def _map_trx_range(payload: Payload) -> TrxCommissionRange | None:
    if not payload:
        return None
    return TrxCommissionRange(
        value_min=_int(payload, "valueMin"),
        value_max=_int(payload, "valueMax"),
        step=_int(payload, "step"),
        raw_payload=payload,
    )


def map_cpa_auction_bids(payload: object) -> CpaAuctionBidsResult:
    """Преобразует действующие и доступные ставки CPA-аукциона."""

    data = _expect_mapping(payload)
    return CpaAuctionBidsResult(
        items=[
            CpaAuctionItemBid(
                item_id=_int(item, "itemId", "itemID"),
                price_penny=_int(item, "pricePenny"),
                expiration_time=_str(item, "expirationTime"),
                available_prices=[
                    CpaAuctionBidOption(
                        price_penny=_int(option, "pricePenny"),
                        goodness=_int(option, "goodness"),
                        raw_payload=option,
                    )
                    for option in _list(item, "availablePrices")
                ],
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_target_action_promotions(payload: object) -> TargetActionPromotionsResult:
    """Преобразует текущие настройки цены целевого действия."""

    data = _expect_mapping(payload)
    return TargetActionPromotionsResult(
        items=[
            TargetActionPromotion(
                item_id=_int(item, "itemID", "itemId"),
                action_type_id=_int(item, "actionTypeID", "actionTypeId"),
                is_auto=_bool(item, "isAuto", "auto"),
                bid_penny=_int(item, "bidPenny"),
                budget_penny=_int(item, "budgetPenny"),
                budget_type=_str(item, "budgetType"),
                available_bids=[
                    TargetActionBid(
                        value_penny=_int(option, "valuePenny"),
                        min_forecast=_int(option, "minForecast"),
                        max_forecast=_int(option, "maxForecast"),
                        compare=_int(option, "compare"),
                        raw_payload=option,
                    )
                    for option in _list(item, "availableBids", "bids")
                ],
                raw_payload=item,
            )
            for item in _items_payload(data)
        ],
        raw_payload=data,
    )


def map_autostrategy_budget(payload: object) -> AutostrategyBudget:
    """Преобразует расчет бюджета автокампании."""

    data = _expect_mapping(payload)
    budget_payload = _mapping(data, "budget")
    source = budget_payload or data
    return AutostrategyBudget(
        budget_id=_str(data, "budgetId", "budgetID", "id"),
        recommended=_map_budget_point(_mapping(source, "recommended")),
        minimal=_map_budget_point(_mapping(source, "minimal")),
        maximal=_map_budget_point(_mapping(source, "maximal")),
        price_ranges=[_map_price_range(item) for item in _list(source, "priceRanges")],
        raw_payload=data,
    )


def _map_budget_point(payload: Payload) -> AutostrategyBudgetPoint | None:
    if not payload:
        return None
    return AutostrategyBudgetPoint(
        total=_int(payload, "total"),
        real=_int(payload, "real"),
        bonus=_int(payload, "bonus"),
        calls_from=_int(payload, "callsFrom"),
        calls_to=_int(payload, "callsTo"),
        views_from=_int(payload, "viewsFrom"),
        views_to=_int(payload, "viewsTo"),
        raw_payload=payload,
    )


def _map_price_range(payload: Payload) -> AutostrategyPriceRange:
    return AutostrategyPriceRange(
        price_from=_int(payload, "priceFrom"),
        price_to=_int(payload, "priceTo"),
        percent=_int(payload, "percent"),
        calls_from=_int(payload, "callsFrom"),
        calls_to=_int(payload, "callsTo"),
        views_from=_int(payload, "viewsFrom"),
        views_to=_int(payload, "viewsTo"),
        raw_payload=payload,
    )


def map_campaign_action(payload: object) -> CampaignActionResult:
    """Преобразует результат операции с автокампанией."""

    data = _expect_mapping(payload)
    return CampaignActionResult(
        campaign_id=_int(data, "campaignId", "campaignID", "id"),
        status=_str(data, "status"),
        raw_payload=data,
    )


def map_campaign_info(payload: object) -> CampaignInfo:
    """Преобразует информацию об автокампании."""

    data = _expect_mapping(payload)
    source = _mapping(data, "campaign") or data
    return CampaignInfo(
        campaign_id=_int(source, "campaignId", "campaignID", "id"),
        campaign_type=_str(source, "campaignType"),
        status=_str(source, "status"),
        budget=_int(source, "budget"),
        balance=_int(source, "balance"),
        title=_str(source, "title", "name"),
        raw_payload=data,
    )


def map_campaigns(payload: object) -> CampaignsResult:
    """Преобразует список автокампаний."""

    data = _expect_mapping(payload)
    return CampaignsResult(
        items=[map_campaign_info(item) for item in _items_payload(data)],
        raw_payload=data,
    )


def map_autostrategy_stat(payload: object) -> AutostrategyStat:
    """Преобразует статистику автокампании."""

    data = _expect_mapping(payload)
    source = _mapping(data, "stat") or data
    return AutostrategyStat(
        campaign_id=_int(source, "campaignId", "campaignID", "id"),
        views=_int(source, "views"),
        contacts=_int(source, "contacts", "leads"),
        spend=_int(source, "spend", "spendTotal"),
        raw_payload=data,
    )
