"""Типизированные модели раздела promotion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromotionServiceType:
    """Тип услуги продвижения."""

    code: str | None
    title: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromotionServiceDictionary:
    """Словарь услуг продвижения."""

    items: list[PromotionServiceType]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ListPromotionServicesRequest:
    """Запрос списка услуг продвижения."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос списка услуг."""

        return {"itemIds": self.item_ids}


@dataclass(slots=True, frozen=True)
class PromotionService:
    """Услуга продвижения по объявлению."""

    item_id: int | None
    service_code: str | None
    service_name: str | None
    price: int | None
    status: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromotionServicesResult:
    """Список услуг продвижения."""

    items: list[PromotionService]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class PromotionOrderInfo:
    """Заявка на продвижение."""

    order_id: str | None
    item_id: int | None
    service_code: str | None
    status: str | None
    created_at: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromotionOrdersResult:
    """Список заявок на продвижение."""

    items: list[PromotionOrderInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class GetPromotionOrderStatusRequest:
    """Запрос статуса заявок."""

    order_ids: list[str]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статуса заявок."""

        return {"orderIds": self.order_ids}


@dataclass(slots=True, frozen=True)
class PromotionOrderStatus:
    """Статус заявки на продвижение."""

    order_id: str | None
    status: str | None
    message: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromotionOrderStatusesResult:
    """Набор статусов заявок."""

    items: list[PromotionOrderStatus]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class BbipForecast:
    """Прогноз BBIP по объявлению."""

    item_id: int | None
    min_views: int | None
    max_views: int | None
    total_price: int | None
    total_old_price: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BbipForecastsResult:
    """Результат прогноза BBIP."""

    items: list[BbipForecast]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class PromotionActionItem:
    """Результат действия по одному объявлению."""

    item_id: int | None
    success: bool
    status: str | None = None
    message: str | None = None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromotionActionResult:
    """Результат операции продвижения."""

    items: list[PromotionActionItem]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CreateBbipSuggestsRequest:
    """Запрос вариантов бюджета BBIP."""

    item_ids: list[int]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос вариантов бюджета BBIP."""

        return {"itemIds": self.item_ids}


@dataclass(slots=True, frozen=True)
class BbipBudgetOption:
    """Вариант бюджета BBIP."""

    price: int | None
    old_price: int | None
    is_recommended: bool | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BbipDurationRange:
    """Доступный диапазон длительности BBIP."""

    start: int | None
    stop: int | None
    recommended: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BbipSuggest:
    """Варианты бюджета BBIP по объявлению."""

    item_id: int | None
    duration: BbipDurationRange | None
    budgets: list[BbipBudgetOption]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BbipSuggestsResult:
    """Результат вариантов бюджета BBIP."""

    items: list[BbipSuggest]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class TrxCommissionRange:
    """Диапазон комиссии TrxPromo."""

    value_min: int | None
    value_max: int | None
    step: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TrxCommissionInfo:
    """Доступность и комиссия TrxPromo по объявлению."""

    item_id: int | None
    commission: int | None
    is_active: bool | None
    valid_commission_range: TrxCommissionRange | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TrxCommissionsResult:
    """Список комиссий TrxPromo."""

    items: list[TrxCommissionInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaAuctionBidOption:
    """Доступная ставка CPA-аукциона."""

    price_penny: int | None
    goodness: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaAuctionItemBid:
    """Текущая и доступные ставки CPA-аукциона по объявлению."""

    item_id: int | None
    price_penny: int | None
    expiration_time: str | None
    available_prices: list[CpaAuctionBidOption]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CpaAuctionBidsResult:
    """Список ставок CPA-аукциона."""

    items: list[CpaAuctionItemBid]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class TargetActionBid:
    """Доступная цена целевого действия."""

    value_penny: int | None
    min_forecast: int | None
    max_forecast: int | None
    compare: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TargetActionBudget:
    """Бюджет целевого действия."""

    budget_penny: int | None
    budget_type: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TargetActionPromotion:
    """Текущая настройка цены целевого действия."""

    item_id: int | None
    action_type_id: int | None
    is_auto: bool | None
    bid_penny: int | None
    budget_penny: int | None
    budget_type: str | None
    available_bids: list[TargetActionBid]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TargetActionPromotionsResult:
    """Набор текущих настроек цены целевого действия."""

    items: list[TargetActionPromotion]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


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
class AutostrategyBudgetPoint:
    """Оценка бюджета автокампании."""

    total: int | None
    real: int | None
    bonus: int | None
    calls_from: int | None
    calls_to: int | None
    views_from: int | None
    views_to: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutostrategyPriceRange:
    """Ценовой диапазон бюджета автокампании."""

    price_from: int | None
    price_to: int | None
    percent: int | None
    calls_from: int | None
    calls_to: int | None
    views_from: int | None
    views_to: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutostrategyBudget:
    """Расчет бюджета автокампании."""

    budget_id: str | None
    recommended: AutostrategyBudgetPoint | None
    minimal: AutostrategyBudgetPoint | None
    maximal: AutostrategyBudgetPoint | None
    price_ranges: list[AutostrategyPriceRange]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CreateAutostrategyBudgetRequest:
    """Запрос расчета бюджета кампании."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос расчета бюджета."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class CampaignActionResult:
    """Результат операции с автокампанией."""

    campaign_id: int | None
    status: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CampaignInfo:
    """Информация об автокампании."""

    campaign_id: int | None
    campaign_type: str | None
    status: str | None
    budget: int | None
    balance: int | None
    title: str | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CampaignsResult:
    """Список автокампаний."""

    items: list[CampaignInfo]
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutostrategyStat:
    """Статистика автокампании."""

    campaign_id: int | None
    views: int | None
    contacts: int | None
    spend: int | None
    raw_payload: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CreateAutostrategyCampaignRequest:
    """Запрос создания автокампании."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос создания кампании."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class UpdateAutostrategyCampaignRequest:
    """Запрос редактирования автокампании."""

    payload: Mapping[str, object]

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос редактирования кампании."""

        return dict(self.payload)


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

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос остановки кампании."""

        return {"campaignId": self.campaign_id}


@dataclass(slots=True, frozen=True)
class ListAutostrategyCampaignsRequest:
    """Запрос списка автокампаний."""

    payload: Mapping[str, object] = field(default_factory=dict)

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос списка кампаний."""

        return dict(self.payload)


@dataclass(slots=True, frozen=True)
class GetAutostrategyStatRequest:
    """Запрос статистики автокампании."""

    campaign_id: int

    def to_payload(self) -> dict[str, object]:
        """Сериализует запрос статистики кампании."""

        return {"campaignId": self.campaign_id}
