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
    PromotionOrderError,
    PromotionOrderInfo,
    PromotionOrdersResult,
    PromotionOrderStatusItem,
    PromotionOrderStatusResult,
    PromotionService,
    PromotionServiceDictionary,
    PromotionServicesResult,
    PromotionServiceType,
    TargetActionAutoBids,
    TargetActionAutoPromotion,
    TargetActionBid,
    TargetActionBudget,
    TargetActionGetBidsResult,
    TargetActionManualBids,
    TargetActionManualPromotion,
    TargetActionPromotion,
    TargetActionPromotionsByItemIdsResult,
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
            )
            for item in _items_payload(data)
        ],
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
            )
            for item in _items_payload(data)
        ],
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
            )
            for item in _items_payload(data)
        ],
    )


def map_promotion_order_status(payload: object) -> PromotionOrderStatusResult:
    """Преобразует documented shape статуса заявки на продвижение."""

    data = _expect_mapping(payload)
    order_id = _str(data, "orderId", "orderID", "id")
    status = _str(data, "status")
    if order_id is None or status is None:
        raise ResponseMappingError(
            "Статус заявки promotion должен содержать `orderId` и `status`.",
            payload=payload,
        )
    errors_payload = data.get("errors", [])
    if errors_payload is not None and not isinstance(errors_payload, list):
        raise ResponseMappingError("Поле `errors` должно быть массивом.", payload=payload)
    return PromotionOrderStatusResult(
        order_id=order_id,
        status=status,
        total_price=_int(data, "totalPrice"),
        items=[
            PromotionOrderStatusItem(
                item_id=_int(item, "itemId", "itemID"),
                price=_int(item, "price"),
                slug=_str(item, "slug"),
                status=_str(item, "status"),
                error_reason=_str(item, "errorReason"),
            )
            for item in _list(data, "items")
        ],
        errors=[
            PromotionOrderError(
                item_id=_int(item, "itemId", "itemID"),
                error_code=_int(item, "errorCode"),
                error_text=_str(item, "errorText"),
            )
            for item in errors_payload or []
            if isinstance(item, Mapping)
        ],
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
            )
            for item in _items_payload(data)
        ],
    )


def map_promotion_action(
    payload: object,
    *,
    action: str,
    target: Mapping[str, object] | None,
    request_payload: Mapping[str, object],
) -> PromotionActionResult:
    """Преобразует результат действия по продвижению."""

    data = _expect_mapping(payload)
    items_payload = _items_payload(data)
    if not items_payload:
        success_payload = _mapping(data, "success")
        items_payload = _list(success_payload, "items", "result")
    items = [
        PromotionActionItem(
            item_id=_int(item, "itemId", "itemID"),
            success=bool(item.get("success", True)),
            status=_str(item, "status"),
            message=_str(_mapping(item, "error"), "message") or _str(item, "message"),
            upstream_reference=_str(item, "orderId", "requestId", "promotionId", "id"),
        )
        for item in items_payload
    ]
    applied = bool(data.get("success", True)) if not items else all(item.success for item in items)
    statuses = [item.status for item in items if item.status]
    messages = [item.message for item in items if item.message]
    resolved_status = _resolve_action_status(payload=data, statuses=statuses, applied=applied)
    details: dict[str, object] = {}
    if items:
        details["items"] = [
            {
                "item_id": item.item_id,
                "success": item.success,
                "status": item.status,
                "message": item.message,
            }
            for item in items
        ]
    elif message := _str(data, "message", "status"):
        details["message"] = message
    return PromotionActionResult(
        action=action,
        target=dict(target) if target is not None else None,
        status=resolved_status,
        applied=applied,
        request_payload=dict(request_payload),
        warnings=messages if not applied else [],
        upstream_reference=_extract_upstream_reference(data, items),
        details=details,
    )


def _resolve_action_status(*, payload: Payload, statuses: list[str], applied: bool) -> str:
    if statuses:
        unique_statuses = list(dict.fromkeys(statuses))
        if len(unique_statuses) == 1:
            return unique_statuses[0]
        return "applied" if applied else "partial"
    payload_status = _str(payload, "status")
    if payload_status is not None:
        return payload_status
    return "applied" if applied else "failed"


def _extract_upstream_reference(
    payload: Payload,
    items: list[PromotionActionItem],
) -> str | None:
    reference = _str(payload, "orderId", "requestId", "promotionId", "id")
    if reference is not None:
        return reference
    for item in items:
        if item.upstream_reference is not None:
            return item.upstream_reference
    return None


def map_bbip_suggests(payload: object) -> BbipSuggestsResult:
    """Преобразует варианты бюджета BBIP."""

    data = _expect_mapping(payload)
    return BbipSuggestsResult(
        items=[
            BbipSuggest(
                item_id=_int(item, "itemId", "itemID"),
                duration=_map_bbip_duration(_mapping(item, "duration")),
                budgets=[_map_bbip_budget(option) for option in _list(item, "budgets")],
            )
            for item in _items_payload(data)
        ],
    )


def _map_bbip_budget(payload: Payload) -> BbipBudgetOption:
    return BbipBudgetOption(
        price=_int(payload, "price"),
        old_price=_int(payload, "oldPrice"),
        is_recommended=_bool(payload, "isRecommended"),
    )


def _map_bbip_duration(payload: Payload) -> BbipDurationRange | None:
    if not payload:
        return None
    return BbipDurationRange(
        start=_int(payload, "from"),
        stop=_int(payload, "to"),
        recommended=_int(payload, "recommended"),
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
            )
            for item in items_payload
        ],
    )


def _map_trx_range(payload: Payload) -> TrxCommissionRange | None:
    if not payload:
        return None
    return TrxCommissionRange(
        value_min=_int(payload, "valueMin"),
        value_max=_int(payload, "valueMax"),
        step=_int(payload, "step"),
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
                    )
                    for option in _list(item, "availablePrices")
                ],
            )
            for item in _items_payload(data)
        ],
    )


def _map_target_action_bid(item: Payload) -> TargetActionBid:
    return TargetActionBid(
        value_penny=_int(item, "valuePenny"),
        min_forecast=_int(item, "minForecast"),
        max_forecast=_int(item, "maxForecast"),
        compare=_int(item, "compare"),
    )


def _map_target_action_budget(item: Payload) -> TargetActionBudget:
    return TargetActionBudget(
        budget_penny=_int(item, "valuePenny"),
        min_forecast=_int(item, "minForecast"),
        max_forecast=_int(item, "maxForecast"),
        compare=_int(item, "compare"),
    )


def _map_target_action_manual(payload: Payload) -> TargetActionManualBids:
    bids_payload = payload.get("bids")
    if bids_payload is not None and not isinstance(bids_payload, list):
        raise ResponseMappingError("Поле `manual.bids` должно быть массивом.", payload=payload)
    return TargetActionManualBids(
        bid_penny=_int(payload, "bidPenny"),
        limit_penny=_int(payload, "limitPenny"),
        rec_bid_penny=_int(payload, "recBidPenny"),
        min_bid_penny=_int(payload, "minBidPenny"),
        max_bid_penny=_int(payload, "maxBidPenny"),
        min_limit_penny=_int(payload, "minLimitPenny"),
        max_limit_penny=_int(payload, "maxLimitPenny"),
        bids=[
            _map_target_action_bid(item) for item in bids_payload or [] if isinstance(item, Mapping)
        ],
    )


def _map_budget_values(payload: Payload, key: str) -> list[TargetActionBudget]:
    budget = payload.get(key)
    if budget is None:
        return []
    if not isinstance(budget, Mapping):
        raise ResponseMappingError(f"Поле `{key}` должно быть объектом.", payload=payload)
    values = budget.get("budgets")
    if values is not None and not isinstance(values, list):
        raise ResponseMappingError(f"Поле `{key}.budgets` должно быть массивом.", payload=payload)
    return [_map_target_action_budget(item) for item in values or [] if isinstance(item, Mapping)]


def _map_target_action_auto(payload: Payload) -> TargetActionAutoBids:
    return TargetActionAutoBids(
        budget_penny=_int(payload, "budgetPenny"),
        budget_type=_str(payload, "budgetType"),
        min_budget_penny=_int(payload, "minBudgetPenny"),
        max_budget_penny=_int(payload, "maxBudgetPenny"),
        daily_budget=_map_budget_values(payload, "dailyBudget"),
        weekly_budget=_map_budget_values(payload, "weeklyBudget"),
        monthly_budget=_map_budget_values(payload, "monthlyBudget"),
    )


def map_target_action_get_bids_out(payload: object) -> TargetActionGetBidsResult:
    """Преобразует documented shape GET /cpxpromo/1/getBids/{itemId}."""

    data = _expect_mapping(payload)
    action_type_id = _int(data, "actionTypeID")
    selected_type = _str(data, "selectedType")
    if action_type_id is None or selected_type is None:
        raise ResponseMappingError(
            "Ответ getBids должен содержать `actionTypeID` и `selectedType`.",
            payload=payload,
        )
    return TargetActionGetBidsResult(
        action_type_id=action_type_id,
        selected_type=selected_type,
        auto=(
            _map_target_action_auto(cast(Payload, data["auto"]))
            if isinstance(data.get("auto"), Mapping)
            else None
        ),
        manual=(
            _map_target_action_manual(cast(Payload, data["manual"]))
            if isinstance(data.get("manual"), Mapping)
            else None
        ),
    )


def map_target_action_get_promotions_by_item_ids_out(
    payload: object,
) -> TargetActionPromotionsByItemIdsResult:
    """Преобразует documented shape POST /cpxpromo/1/getPromotionsByItemIds."""

    data = _expect_mapping(payload)
    items_payload = data.get("items")
    if not isinstance(items_payload, list):
        raise ResponseMappingError(
            "Ответ getPromotionsByItemIds должен содержать массив `items`.", payload=payload
        )
    items: list[TargetActionPromotion] = []
    for item in items_payload:
        if not isinstance(item, Mapping):
            continue
        item_id = _int(item, "itemID")
        action_type_id = _int(item, "actionTypeID")
        if item_id is None or action_type_id is None:
            raise ResponseMappingError(
                "Элемент getPromotionsByItemIds должен содержать `itemID` и `actionTypeID`.",
                payload=item,
            )
        items.append(
            TargetActionPromotion(
                item_id=item_id,
                action_type_id=action_type_id,
                auto=(
                    TargetActionAutoPromotion(
                        budget_penny=_int(cast(Payload, item["autoPromotion"]), "budgetPenny"),
                        budget_type=_str(cast(Payload, item["autoPromotion"]), "budgetType"),
                    )
                    if isinstance(item.get("autoPromotion"), Mapping)
                    else None
                ),
                manual=(
                    TargetActionManualPromotion(
                        bid_penny=_int(cast(Payload, item["manualPromotion"]), "bidPenny"),
                        limit_penny=_int(cast(Payload, item["manualPromotion"]), "limitPenny"),
                    )
                    if isinstance(item.get("manualPromotion"), Mapping)
                    else None
                ),
            )
        )
    return TargetActionPromotionsByItemIdsResult(
        items=items,
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
    )


def map_campaign_action(payload: object) -> CampaignActionResult:
    """Преобразует результат операции с автокампанией."""

    data = _expect_mapping(payload)
    return CampaignActionResult(
        campaign_id=_int(data, "campaignId", "campaignID", "id"),
        status=_str(data, "status"),
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
    )


def map_campaigns(payload: object) -> CampaignsResult:
    """Преобразует список автокампаний."""

    data = _expect_mapping(payload)
    return CampaignsResult(
        items=[map_campaign_info(item) for item in _items_payload(data)],
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
    )
