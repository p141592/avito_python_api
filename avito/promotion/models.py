"""Типизированные модели раздела promotion."""

from __future__ import annotations

from dataclasses import dataclass, field

from avito.core.serialization import SerializableModel, enable_module_serialization


@dataclass(slots=True, frozen=True)
class PromotionServiceType(SerializableModel):
    """Тип услуги продвижения."""

    code: str | None
    title: str | None


@dataclass(slots=True, frozen=True)
class PromotionServiceDictionary(SerializableModel):
    """Словарь услуг продвижения."""

    items: list[PromotionServiceType]


@dataclass(slots=True, frozen=True)
class ListPromotionServicesRequest:
    """Запрос списка услуг продвижения."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос списка услуг."""

        return {"itemIds": self.item_ids}


@dataclass(slots=True, frozen=True)
class PromotionService(SerializableModel):
    """Услуга продвижения по объявлению."""

    item_id: int | None
    service_code: str | None
    service_name: str | None
    price: int | None
    status: str | None


@dataclass(slots=True, frozen=True)
class PromotionServicesResult(SerializableModel):
    """Список услуг продвижения."""

    items: list[PromotionService]


@dataclass(slots=True, frozen=True)
class ListPromotionOrdersRequest:
    """Запрос списка заявок на продвижение."""

    item_ids: list[int] | None = None
    order_ids: list[str] | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос списка заявок."""

        payload: dict[str, object] = {}
        if self.item_ids is not None:
            payload["itemIds"] = self.item_ids
        if self.order_ids is not None:
            payload["orderIds"] = self.order_ids
        return payload


@dataclass(slots=True, frozen=True)
class PromotionOrderInfo(SerializableModel):
    """Заявка на продвижение."""

    order_id: str | None
    item_id: int | None
    service_code: str | None
    status: str | None
    created_at: str | None


@dataclass(slots=True, frozen=True)
class PromotionOrdersResult(SerializableModel):
    """Список заявок на продвижение."""

    items: list[PromotionOrderInfo]


@dataclass(slots=True, frozen=True)
class GetPromotionOrderStatusRequest:
    """Запрос статуса заявок."""

    order_ids: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статуса заявок."""

        return {"orderIds": self.order_ids}


@dataclass(slots=True, frozen=True)
class PromotionOrderError(SerializableModel):
    """Ошибка по объявлению в ответе promotion API."""

    item_id: int | None
    error_code: int | None
    error_text: str | None


@dataclass(slots=True, frozen=True)
class PromotionOrderStatusItem(SerializableModel):
    """Статус услуги внутри заявки на продвижение."""

    item_id: int | None
    price: int | None
    slug: str | None
    status: str | None
    error_reason: str | None


@dataclass(slots=True, frozen=True)
class PromotionOrderStatusResult(SerializableModel):
    """Статус заявки на продвижение."""

    order_id: str | None
    status: str | None
    total_price: int | None
    items: list[PromotionOrderStatusItem]
    errors: list[PromotionOrderError]


@dataclass(slots=True, frozen=True)
class BbipForecastRequestItem:
    """Параметры прогноза BBIP по объявлению."""

    item_id: int
    duration: int
    price: int
    old_price: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует один BBIP-элемент прогноза."""

        return {
            "itemId": self.item_id,
            "duration": self.duration,
            "price": self.price,
            "oldPrice": self.old_price,
        }


@dataclass(slots=True, frozen=True)
class CreateBbipForecastsRequest:
    """Запрос прогноза BBIP."""

    items: list[BbipForecastRequestItem]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос прогноза BBIP."""

        return {"items": [item.to_payload() for item in self.items]}


@dataclass(slots=True, frozen=True)
class BbipForecast(SerializableModel):
    """Прогноз BBIP по объявлению."""

    item_id: int | None
    min_views: int | None
    max_views: int | None
    total_price: int | None
    total_old_price: int | None


@dataclass(slots=True, frozen=True)
class BbipForecastsResult(SerializableModel):
    """Результат прогноза BBIP."""

    items: list[BbipForecast]


@dataclass(slots=True, frozen=True)
class BbipOrderItem:
    """Параметры подключения BBIP по объявлению."""

    item_id: int
    duration: int
    price: int
    old_price: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует одну заявку BBIP."""

        return {
            "itemId": self.item_id,
            "duration": self.duration,
            "price": self.price,
            "oldPrice": self.old_price,
        }


@dataclass(slots=True, frozen=True)
class CreateBbipOrderRequest:
    """Запрос подключения BBIP."""

    items: list[BbipOrderItem]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос подключения BBIP."""

        return {"items": [item.to_payload() for item in self.items]}


@dataclass(slots=True, frozen=True)
class PromotionActionItem(SerializableModel):
    """Результат действия по одному объявлению."""

    item_id: int | None
    success: bool
    status: str | None = None
    message: str | None = None
    upstream_reference: str | None = None


@dataclass(slots=True, frozen=True)
class PromotionActionResult(SerializableModel):
    """Стабильный результат write-операции продвижения."""

    action: str
    target: dict[str, object] | None
    status: str
    applied: bool
    request_payload: dict[str, object] | None = None
    warnings: list[str] = field(default_factory=list)
    upstream_reference: str | None = None
    details: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CreateBbipSuggestsRequest:
    """Запрос вариантов бюджета BBIP."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос вариантов бюджета BBIP."""

        return {"itemIds": self.item_ids}


@dataclass(slots=True, frozen=True)
class BbipBudgetOption(SerializableModel):
    """Вариант бюджета BBIP."""

    price: int | None
    old_price: int | None
    is_recommended: bool | None


@dataclass(slots=True, frozen=True)
class BbipDurationRange(SerializableModel):
    """Доступный диапазон длительности BBIP."""

    start: int | None
    stop: int | None
    recommended: int | None


@dataclass(slots=True, frozen=True)
class BbipSuggest(SerializableModel):
    """Варианты бюджета BBIP по объявлению."""

    item_id: int | None
    duration: BbipDurationRange | None
    budgets: list[BbipBudgetOption]


@dataclass(slots=True, frozen=True)
class BbipSuggestsResult(SerializableModel):
    """Результат вариантов бюджета BBIP."""

    items: list[BbipSuggest]


@dataclass(slots=True, frozen=True)
class TrxPromotionApplyItem:
    """Параметры запуска TrxPromo по объявлению."""

    item_id: int
    commission: int
    date_from: str
    date_to: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует один элемент запуска TrxPromo."""

        payload: dict[str, object] = {
            "itemID": self.item_id,
            "commission": self.commission,
            "dateFrom": self.date_from,
        }
        if self.date_to is not None:
            payload["dateTo"] = self.date_to
        return payload


@dataclass(slots=True, frozen=True)
class CreateTrxPromotionApplyRequest:
    """Запрос запуска TrxPromo."""

    items: list[TrxPromotionApplyItem]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос запуска TrxPromo."""

        return {"items": [item.to_payload() for item in self.items]}


@dataclass(slots=True, frozen=True)
class CancelTrxPromotionRequest:
    """Запрос остановки TrxPromo."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос остановки TrxPromo."""

        return {"items": [{"itemID": item_id} for item_id in self.item_ids]}


@dataclass(slots=True, frozen=True)
class TrxCommissionRange(SerializableModel):
    """Диапазон комиссии TrxPromo."""

    value_min: int | None
    value_max: int | None
    step: int | None


@dataclass(slots=True, frozen=True)
class TrxCommissionInfo(SerializableModel):
    """Доступность и комиссия TrxPromo по объявлению."""

    item_id: int | None
    commission: int | None
    is_active: bool | None
    valid_commission_range: TrxCommissionRange | None


@dataclass(slots=True, frozen=True)
class TrxCommissionsResult(SerializableModel):
    """Список комиссий TrxPromo."""

    items: list[TrxCommissionInfo]


@dataclass(slots=True, frozen=True)
class CpaAuctionBidOption(SerializableModel):
    """Доступная ставка CPA-аукциона."""

    price_penny: int | None
    goodness: int | None


@dataclass(slots=True, frozen=True)
class CpaAuctionItemBid(SerializableModel):
    """Текущая и доступные ставки CPA-аукциона по объявлению."""

    item_id: int | None
    price_penny: int | None
    expiration_time: str | None
    available_prices: list[CpaAuctionBidOption]


@dataclass(slots=True, frozen=True)
class CpaAuctionBidsResult(SerializableModel):
    """Список ставок CPA-аукциона."""

    items: list[CpaAuctionItemBid]


@dataclass(slots=True, frozen=True)
class CreateItemBid:
    """Новая ставка CPA-аукциона."""

    item_id: int
    price_penny: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует одну ставку CPA-аукциона."""

        return {"itemID": self.item_id, "pricePenny": self.price_penny}


@dataclass(slots=True, frozen=True)
class CreateItemBidsRequest:
    """Запрос сохранения новых ставок CPA-аукциона."""

    items: list[CreateItemBid]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос сохранения ставок."""

        return {"items": [item.to_payload() for item in self.items]}


@dataclass(slots=True, frozen=True)
class TargetActionBid(SerializableModel):
    """Доступная цена целевого действия."""

    value_penny: int | None
    min_forecast: int | None
    max_forecast: int | None
    compare: int | None


@dataclass(slots=True, frozen=True)
class TargetActionManualBids(SerializableModel):
    """Детали ручной ставки цены целевого действия."""

    bid_penny: int | None
    limit_penny: int | None
    rec_bid_penny: int | None
    min_bid_penny: int | None
    max_bid_penny: int | None
    min_limit_penny: int | None
    max_limit_penny: int | None
    bids: list[TargetActionBid]


@dataclass(slots=True, frozen=True)
class TargetActionBudget(SerializableModel):
    """Диапазон доступных бюджетов цены целевого действия."""

    budget_penny: int | None
    min_forecast: int | None
    max_forecast: int | None
    compare: int | None


@dataclass(slots=True, frozen=True)
class TargetActionAutoBids(SerializableModel):
    """Детали автоматического продвижения цены целевого действия."""

    budget_penny: int | None
    budget_type: str | None
    min_budget_penny: int | None
    max_budget_penny: int | None
    daily_budget: list[TargetActionBudget]
    weekly_budget: list[TargetActionBudget]
    monthly_budget: list[TargetActionBudget]


@dataclass(slots=True, frozen=True)
class TargetActionGetBidsResult(SerializableModel):
    """Ответ GET /cpxpromo/1/getBids/{itemId}."""

    action_type_id: int
    selected_type: str
    auto: TargetActionAutoBids | None = None
    manual: TargetActionManualBids | None = None


@dataclass(slots=True, frozen=True)
class TargetActionPromotion(SerializableModel):
    """Текущая настройка цены целевого действия по объявлению."""

    item_id: int
    action_type_id: int
    auto: TargetActionAutoPromotion | None = None
    manual: TargetActionManualPromotion | None = None


@dataclass(slots=True, frozen=True)
class TargetActionAutoPromotion(SerializableModel):
    """Текущий auto-budget по объявлению."""

    budget_penny: int | None
    budget_type: str | None


@dataclass(slots=True, frozen=True)
class TargetActionManualPromotion(SerializableModel):
    """Текущая manual-настройка по объявлению."""

    bid_penny: int | None
    limit_penny: int | None


@dataclass(slots=True, frozen=True)
class TargetActionPromotionsByItemIdsResult(SerializableModel):
    """Ответ POST /cpxpromo/1/getPromotionsByItemIds."""

    items: list[TargetActionPromotion]


@dataclass(slots=True, frozen=True)
class GetPromotionsByItemIdsRequest:
    """Запрос настроек по нескольким объявлениям."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос настроек по нескольким объявлениям."""

        return {"itemIDs": self.item_ids}


@dataclass(slots=True, frozen=True)
class DeletePromotionRequest:
    """Запрос остановки продвижения с ЦД."""

    item_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос остановки продвижения."""

        return {"itemID": self.item_id}


@dataclass(slots=True, frozen=True)
class UpdateAutoBidRequest:
    """Запрос автоматической настройки цены целевого действия."""

    item_id: int
    action_type_id: int
    budget_penny: int
    budget_type: str

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос автоматической настройки."""

        return {
            "itemID": self.item_id,
            "actionTypeID": self.action_type_id,
            "budgetPenny": self.budget_penny,
            "budgetType": self.budget_type,
        }


@dataclass(slots=True, frozen=True)
class UpdateManualBidRequest:
    """Запрос ручной настройки цены целевого действия."""

    item_id: int
    action_type_id: int
    bid_penny: int
    limit_penny: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос ручной настройки."""

        payload: dict[str, object] = {
            "itemID": self.item_id,
            "actionTypeID": self.action_type_id,
            "bidPenny": self.bid_penny,
        }
        if self.limit_penny is not None:
            payload["limitPenny"] = self.limit_penny
        return payload


@dataclass(slots=True, frozen=True)
class AutostrategyBudgetPoint(SerializableModel):
    """Оценка бюджета автокампании."""

    total: int | None
    real: int | None
    bonus: int | None
    calls_from: int | None
    calls_to: int | None
    views_from: int | None
    views_to: int | None


@dataclass(slots=True, frozen=True)
class AutostrategyPriceRange(SerializableModel):
    """Ценовой диапазон бюджета автокампании."""

    price_from: int | None
    price_to: int | None
    percent: int | None
    calls_from: int | None
    calls_to: int | None
    views_from: int | None
    views_to: int | None


@dataclass(slots=True, frozen=True)
class AutostrategyBudget(SerializableModel):
    """Расчет бюджета автокампании."""

    calc_id: int | None
    recommended: AutostrategyBudgetPoint | None
    minimal: AutostrategyBudgetPoint | None
    maximal: AutostrategyBudgetPoint | None
    price_ranges: list[AutostrategyPriceRange]


@dataclass(slots=True, frozen=True)
class CreateAutostrategyBudgetRequest:
    """Запрос расчета бюджета кампании."""

    campaign_type: str
    start_time: str | None = None
    finish_time: str | None = None
    items: list[int] | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос расчета бюджета."""

        payload: dict[str, object] = {"campaignType": self.campaign_type}
        if self.start_time is not None:
            payload["startTime"] = self.start_time
        if self.finish_time is not None:
            payload["finishTime"] = self.finish_time
        if self.items is not None:
            payload["items"] = list(self.items)
        return payload


@dataclass(slots=True, frozen=True)
class CampaignActionResult(SerializableModel):
    """Результат операции с автокампанией."""

    campaign: CampaignInfo | None


@dataclass(slots=True, frozen=True)
class CampaignInfo(SerializableModel):
    """Информация об автокампании."""

    campaign_id: int | None
    campaign_type: str | None
    budget: int | None
    balance: int | None
    create_time: str | None
    description: str | None
    finish_time: str | None
    items_count: int | None
    start_time: str | None
    status_id: int | None
    title: str | None
    update_time: str | None
    user_id: int | None
    version: int | None


@dataclass(slots=True, frozen=True)
class CampaignForecastRange(SerializableModel):
    """Диапазон прогноза кампании."""

    from_value: int | None
    to_value: int | None


@dataclass(slots=True, frozen=True)
class CampaignForecast(SerializableModel):
    """Прогноз кампании автостратегии."""

    calls: CampaignForecastRange | None
    views: CampaignForecastRange | None


@dataclass(slots=True, frozen=True)
class CampaignItem(SerializableModel):
    """Объявление внутри автокампании."""

    item_id: int | None
    is_active: bool | None


@dataclass(slots=True, frozen=True)
class CampaignDetailsResult(SerializableModel):
    """Полный ответ ручки информации о кампании."""

    campaign: CampaignInfo | None
    forecast: CampaignForecast | None
    items: list[CampaignItem]


@dataclass(slots=True, frozen=True)
class CampaignsResult(SerializableModel):
    """Список автокампаний."""

    items: list[CampaignInfo]
    total_count: int | None = None


@dataclass(slots=True, frozen=True)
class AutostrategyStat(SerializableModel):
    """Статистика автокампании."""

    items: list[AutostrategyStatItem]
    totals: AutostrategyStatTotals | None


@dataclass(slots=True, frozen=True)
class CreateAutostrategyCampaignRequest:
    """Запрос создания автокампании."""

    campaign_type: str
    title: str
    budget: int | None = None
    budget_bonus: int | None = None
    budget_real: int | None = None
    calc_id: int | None = None
    description: str | None = None
    finish_time: str | None = None
    items: list[int] | None = None
    start_time: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос создания кампании."""

        payload: dict[str, object] = {
            "campaignType": self.campaign_type,
            "title": self.title,
        }
        if self.budget is not None:
            payload["budget"] = self.budget
        if self.budget_bonus is not None:
            payload["budgetBonus"] = self.budget_bonus
        if self.budget_real is not None:
            payload["budgetReal"] = self.budget_real
        if self.calc_id is not None:
            payload["calcId"] = self.calc_id
        if self.description is not None:
            payload["description"] = self.description
        if self.finish_time is not None:
            payload["finishTime"] = self.finish_time
        if self.items is not None:
            payload["items"] = list(self.items)
        if self.start_time is not None:
            payload["startTime"] = self.start_time
        return payload


@dataclass(slots=True, frozen=True)
class UpdateAutostrategyCampaignRequest:
    """Запрос редактирования автокампании."""

    campaign_id: int
    version: int
    budget: int | None = None
    calc_id: int | None = None
    description: str | None = None
    finish_time: str | None = None
    items: list[int] | None = None
    start_time: str | None = None
    title: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос редактирования кампании."""

        payload: dict[str, object] = {
            "campaignId": self.campaign_id,
            "version": self.version,
        }
        if self.budget is not None:
            payload["budget"] = self.budget
        if self.calc_id is not None:
            payload["calcId"] = self.calc_id
        if self.description is not None:
            payload["description"] = self.description
        if self.finish_time is not None:
            payload["finishTime"] = self.finish_time
        if self.items is not None:
            payload["items"] = list(self.items)
        if self.start_time is not None:
            payload["startTime"] = self.start_time
        if self.title is not None:
            payload["title"] = self.title
        return payload


@dataclass(slots=True, frozen=True)
class GetAutostrategyCampaignInfoRequest:
    """Запрос полной информации о кампании."""

    campaign_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос информации о кампании."""

        return {"campaignId": self.campaign_id}


@dataclass(slots=True, frozen=True)
class StopAutostrategyCampaignRequest:
    """Запрос остановки автокампании."""

    campaign_id: int
    version: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос остановки кампании."""

        return {"campaignId": self.campaign_id, "version": self.version}


@dataclass(slots=True, frozen=True)
class CampaignUpdateTimeFilter:
    """Фильтр кампаний по времени обновления."""

    from_time: str | None = None
    to_time: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.from_time is not None:
            payload["from"] = self.from_time
        if self.to_time is not None:
            payload["to"] = self.to_time
        return payload


@dataclass(slots=True, frozen=True)
class CampaignListFilter:
    """Фильтр списка кампаний."""

    by_update_time: CampaignUpdateTimeFilter | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.by_update_time is not None:
            payload["byUpdateTime"] = self.by_update_time.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class CampaignOrderBy:
    """Параметры сортировки списка кампаний."""

    column: str
    direction: str

    def to_payload(self) -> dict[str, object]:
        return {"column": self.column, "direction": self.direction}


@dataclass(slots=True, frozen=True)
class ListAutostrategyCampaignsRequest:
    """Запрос списка автокампаний."""

    limit: int
    offset: int | None = None
    status_id: list[int] | None = None
    order_by: list[CampaignOrderBy] | None = None
    filter: CampaignListFilter | None = None

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос списка кампаний."""

        payload: dict[str, object] = {"limit": self.limit}
        if self.offset is not None:
            payload["offset"] = self.offset
        if self.status_id is not None:
            payload["statusId"] = list(self.status_id)
        if self.order_by is not None:
            payload["orderBy"] = [item.to_payload() for item in self.order_by]
        if self.filter is not None:
            payload["filter"] = self.filter.to_payload()
        return payload


@dataclass(slots=True, frozen=True)
class GetAutostrategyStatRequest:
    """Запрос статистики автокампании."""

    campaign_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статистики кампании."""

        return {"campaignId": self.campaign_id}


@dataclass(slots=True, frozen=True)
class AutostrategyStatItem(SerializableModel):
    """Статистика кампании за день."""

    date: str | None
    calls: int | None
    views: int | None
    calls_forecast: CampaignForecastRange | None = None
    views_forecast: CampaignForecastRange | None = None


@dataclass(slots=True, frozen=True)
class AutostrategyStatTotals(SerializableModel):
    """Суммарная статистика кампании."""

    calls: int | None
    views: int | None


PromotionOrder = PromotionOrderInfo
PromotionForecast = BbipForecast

enable_module_serialization(globals())
