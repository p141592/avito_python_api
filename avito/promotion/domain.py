"""Доменные объекты пакета promotion."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.core.validation import (
    validate_non_empty,
    validate_non_empty_string,
    validate_positive_int,
)
from avito.promotion.client import (
    AutostrategyClient,
    BbipClient,
    CpaAuctionClient,
    PromotionClient,
    TargetActionPriceClient,
    TrxPromoClient,
)
from avito.promotion.enums import CampaignType, PromotionStatus, TargetActionBudgetType
from avito.promotion.models import (
    AutostrategyBudget,
    AutostrategyStat,
    BbipForecastsResult,
    BbipItem,
    BbipItemInput,
    BbipSuggestsResult,
    BidItemInput,
    CampaignActionResult,
    CampaignDetailsResult,
    CampaignListFilter,
    CampaignOrderBy,
    CampaignsResult,
    CampaignUpdateTimeFilter,
    CancelTrxPromotionRequest,
    CpaAuctionBidsResult,
    CreateBbipOrderRequest,
    CreateItemBid,
    CreateTrxPromotionApplyRequest,
    DeletePromotionRequest,
    PromotionActionResult,
    PromotionOrdersResult,
    PromotionOrderStatusResult,
    PromotionServiceDictionary,
    PromotionServicesResult,
    TargetActionGetBidsResult,
    TargetActionPromotionsByItemIdsResult,
    TrxCommissionsResult,
    TrxItem,
    TrxItemInput,
    UpdateAutoBidRequest,
    UpdateManualBidRequest,
)


def _preview_result(
    *,
    action: str,
    target: Mapping[str, object],
    request_payload: Mapping[str, object],
) -> PromotionActionResult:
    return PromotionActionResult(
        action=action,
        target=dict(target),
        status=PromotionStatus.PREVIEW,
        applied=False,
        request_payload=dict(request_payload),
        details={"validated": True},
    )


def _validate_optional_datetime(name: str, value: datetime | None) -> None:
    if value is not None and not isinstance(value, datetime):
        raise ValidationError(f"`{name}` должен быть datetime.")


@dataclass(slots=True, frozen=True)
class PromotionOrder(DomainObject):
    """Доменный объект заявок и словарей promotion API."""

    order_id: int | str | None = None

    def get_service_dictionary(self) -> PromotionServiceDictionary:
        """Получает словарь услуг продвижения.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PromotionClient(self.transport).get_service_dictionary()

    def list_services(self, *, item_ids: list[int]) -> PromotionServicesResult:
        """Получает список услуг продвижения по объявлениям.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PromotionClient(self.transport).list_services(item_ids=item_ids)

    def list_orders(
        self,
        *,
        item_ids: list[int] | None = None,
        order_ids: list[str] | None = None,
    ) -> PromotionOrdersResult:
        """Получает список заявок на продвижение.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PromotionClient(self.transport).list_orders(
            item_ids=item_ids,
            order_ids=order_ids,
        )

    def get_order_status(self, *, order_ids: list[str] | None = None) -> PromotionOrderStatusResult:
        """Получает статусы заявок на продвижение.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_order_ids = order_ids or (
            [str(self.order_id)] if self.order_id is not None else []
        )
        if not resolved_order_ids:
            raise ValidationError("Для операции требуется хотя бы один `order_id`.")
        return PromotionClient(self.transport).get_order_status(order_ids=resolved_order_ids)


@dataclass(slots=True, frozen=True)
class BbipPromotion(DomainObject):
    """Доменный объект BBIP-продвижения."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_forecasts(self, *, items: list[BbipItemInput]) -> BbipForecastsResult:
        """Получает прогнозы BBIP.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        bbip_items = [
            BbipItem(
                item_id=item["item_id"],
                duration=item["duration"],
                price=item["price"],
                old_price=item["old_price"],
            )
            for item in items
        ]
        return BbipClient(self.transport).get_forecasts(items=bbip_items)

    def create_order(
        self,
        *,
        items: list[BbipItemInput],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Подключает BBIP-продвижение.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        validate_non_empty("items", items)
        for index, item in enumerate(items):
            validate_positive_int(f"items[{index}].item_id", item["item_id"])
            validate_positive_int(f"items[{index}].duration", item["duration"])
            validate_positive_int(f"items[{index}].price", item["price"])
            validate_positive_int(f"items[{index}].old_price", item["old_price"])
        bbip_items = [
            BbipItem(
                item_id=item["item_id"],
                duration=item["duration"],
                price=item["price"],
                old_price=item["old_price"],
            )
            for item in items
        ]
        request_payload = CreateBbipOrderRequest(items=bbip_items).to_payload()
        target: dict[str, object] = {"item_ids": [item["item_id"] for item in items]}
        if dry_run:
            return _preview_result(
                action="create_order",
                target=target,
                request_payload=request_payload,
            )
        return BbipClient(self.transport).create_order(
            items=bbip_items,
            idempotency_key=idempotency_key,
        )

    def get_suggests(self, *, item_ids: list[int] | None = None) -> BbipSuggestsResult:
        """Получает варианты бюджета BBIP.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_ids = item_ids or self._resource_item_ids()
        return BbipClient(self.transport).get_suggests(item_ids=resolved_item_ids)

    def _resource_item_ids(self) -> list[int]:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id` или список `item_ids`.")
        return [int(self.item_id)]


@dataclass(slots=True, frozen=True)
class TrxPromotion(DomainObject):
    """Доменный объект TrxPromo."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def apply(
        self,
        *,
        items: list[TrxItemInput],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Запускает TrxPromo.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        validate_non_empty("items", items)
        for index, item in enumerate(items):
            validate_positive_int(f"items[{index}].item_id", item["item_id"])
            validate_positive_int(f"items[{index}].commission", item["commission"])
            if not isinstance(item.get("date_from"), datetime):
                raise ValidationError(f"items[{index}].date_from должен быть datetime.")
        trx_items = [
            TrxItem(
                item_id=item["item_id"],
                commission=item["commission"],
                date_from=item["date_from"],
                date_to=item.get("date_to"),
            )
            for item in items
        ]
        request_payload = CreateTrxPromotionApplyRequest(items=trx_items).to_payload()
        target: dict[str, object] = {"item_ids": [item["item_id"] for item in items]}
        if dry_run:
            return _preview_result(action="apply", target=target, request_payload=request_payload)
        return TrxPromoClient(self.transport).apply(
            items=trx_items,
            idempotency_key=idempotency_key,
        )

    def delete(
        self,
        *,
        item_ids: list[int] | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Останавливает TrxPromo.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_ids = item_ids or self._resource_item_ids()
        validate_non_empty("item_ids", resolved_item_ids)
        request_payload = CancelTrxPromotionRequest(item_ids=resolved_item_ids).to_payload()
        target = {"item_ids": list(resolved_item_ids)}
        if dry_run:
            return _preview_result(action="delete", target=target, request_payload=request_payload)
        return TrxPromoClient(self.transport).cancel(
            item_ids=resolved_item_ids,
            idempotency_key=idempotency_key,
        )

    def get_commissions(self, *, item_ids: list[int] | None = None) -> TrxCommissionsResult:
        """Получает доступные комиссии TrxPromo.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return TrxPromoClient(self.transport).get_commissions(
            item_ids=item_ids or self._resource_item_ids()
        )

    def _resource_item_ids(self) -> list[int]:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id` или список `item_ids`.")
        return [int(self.item_id)]


@dataclass(slots=True, frozen=True)
class CpaAuction(DomainObject):
    """Доменный объект CPA-аукциона."""

    item_id: int | str | None = None

    def get_user_bids(
        self,
        *,
        from_item_id: int | None = None,
        batch_size: int | None = None,
    ) -> CpaAuctionBidsResult:
        """Получает действующие и доступные ставки.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return CpaAuctionClient(self.transport).get_user_bids(
            from_item_id=from_item_id,
            batch_size=batch_size,
        )

    def create_item_bids(
        self,
        *,
        items: list[BidItemInput],
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Сохраняет новые ставки по объявлениям.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        bids = [
            CreateItemBid(item_id=item["item_id"], price_penny=item["price_penny"])
            for item in items
        ]
        return CpaAuctionClient(self.transport).create_item_bids(
            items=bids,
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class TargetActionPricing(DomainObject):
    """Доменный объект цены целевого действия."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_bids(self, *, item_id: int | None = None) -> TargetActionGetBidsResult:
        """Получает детализированные цены и бюджеты.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return TargetActionPriceClient(self.transport).get_bids(
            item_id=item_id or self._require_item_id()
        )

    def get_promotions_by_item_ids(
        self, *, item_ids: list[int] | None = None
    ) -> TargetActionPromotionsByItemIdsResult:
        """Получает текущие настройки по нескольким объявлениям.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_ids = item_ids or [self._require_item_id()]
        return TargetActionPriceClient(self.transport).get_promotions_by_item_ids(
            item_ids=resolved_item_ids
        )

    def delete(
        self,
        *,
        item_id: int | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Останавливает продвижение.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_id = item_id or self._require_item_id()
        validate_positive_int("item_id", resolved_item_id)
        request_payload = DeletePromotionRequest(item_id=resolved_item_id).to_payload()
        target = {"item_id": resolved_item_id}
        if dry_run:
            return _preview_result(action="delete", target=target, request_payload=request_payload)
        return TargetActionPriceClient(self.transport).delete_promotion(
            item_id=resolved_item_id,
            idempotency_key=idempotency_key,
        )

    def update_auto(
        self,
        *,
        action_type_id: int,
        budget_penny: int,
        budget_type: TargetActionBudgetType | str,
        item_id: int | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет автоматическую настройку.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_id = item_id or self._require_item_id()
        validate_positive_int("item_id", resolved_item_id)
        validate_positive_int("action_type_id", action_type_id)
        validate_positive_int("budget_penny", budget_penny)
        validate_non_empty_string("budget_type", budget_type)
        request_payload = UpdateAutoBidRequest(
            item_id=resolved_item_id,
            action_type_id=action_type_id,
            budget_penny=budget_penny,
            budget_type=budget_type,
        ).to_payload()
        target = {"item_id": resolved_item_id}
        if dry_run:
            return _preview_result(
                action="update_auto",
                target=target,
                request_payload=request_payload,
            )
        return TargetActionPriceClient(self.transport).update_auto_bid(
            item_id=resolved_item_id,
            action_type_id=action_type_id,
            budget_penny=budget_penny,
            budget_type=budget_type,
            idempotency_key=idempotency_key,
        )

    def update_manual(
        self,
        *,
        action_type_id: int,
        bid_penny: int,
        limit_penny: int | None = None,
        item_id: int | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет ручную настройку.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        При `dry_run=True` payload строится без вызова транспорта.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        resolved_item_id = item_id or self._require_item_id()
        validate_positive_int("item_id", resolved_item_id)
        validate_positive_int("action_type_id", action_type_id)
        validate_positive_int("bid_penny", bid_penny)
        if limit_penny is not None:
            validate_positive_int("limit_penny", limit_penny)
        request_payload = UpdateManualBidRequest(
            item_id=resolved_item_id,
            action_type_id=action_type_id,
            bid_penny=bid_penny,
            limit_penny=limit_penny,
        ).to_payload()
        target = {"item_id": resolved_item_id}
        if dry_run:
            return _preview_result(
                action="update_manual",
                target=target,
                request_payload=request_payload,
            )
        return TargetActionPriceClient(self.transport).update_manual_bid(
            item_id=resolved_item_id,
            action_type_id=action_type_id,
            bid_penny=bid_penny,
            limit_penny=limit_penny,
            idempotency_key=idempotency_key,
        )

    def _require_item_id(self) -> int:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id)


@dataclass(slots=True, frozen=True)
class AutostrategyCampaign(DomainObject):
    """Доменный объект кампаний автостратегии."""

    campaign_id: int | str | None = None
    user_id: int | str | None = None

    def create_budget(
        self,
        *,
        campaign_type: CampaignType | str,
        start_time: datetime | None = None,
        finish_time: datetime | None = None,
        items: list[int] | None = None,
    ) -> AutostrategyBudget:
        """Рассчитывает бюджет кампании.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        _validate_optional_datetime("start_time", start_time)
        _validate_optional_datetime("finish_time", finish_time)
        return AutostrategyClient(self.transport).create_budget(
            campaign_type=campaign_type,
            start_time=start_time,
            finish_time=finish_time,
            items=items,
        )

    def create(
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
        """Создает новую кампанию.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        _validate_optional_datetime("start_time", start_time)
        _validate_optional_datetime("finish_time", finish_time)
        return AutostrategyClient(self.transport).create_campaign(
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
            idempotency_key=idempotency_key,
        )

    def update(
        self,
        *,
        version: int,
        campaign_id: int | None = None,
        budget: int | None = None,
        calc_id: int | None = None,
        description: str | None = None,
        finish_time: datetime | None = None,
        items: list[int] | None = None,
        start_time: datetime | None = None,
        title: str | None = None,
        idempotency_key: str | None = None,
    ) -> CampaignActionResult:
        """Редактирует кампанию.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        _validate_optional_datetime("start_time", start_time)
        _validate_optional_datetime("finish_time", finish_time)
        return AutostrategyClient(self.transport).edit_campaign(
            campaign_id=campaign_id or self._require_campaign_id(),
            version=version,
            budget=budget,
            calc_id=calc_id,
            description=description,
            finish_time=finish_time,
            items=items,
            start_time=start_time,
            title=title,
            idempotency_key=idempotency_key,
        )

    def get(self, *, campaign_id: int | None = None) -> CampaignDetailsResult:
        """Получает полную информацию о кампании.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AutostrategyClient(self.transport).get_campaign_info(
            campaign_id=campaign_id or self._require_campaign_id()
        )

    def delete(
        self,
        *,
        version: int,
        campaign_id: int | None = None,
        idempotency_key: str | None = None,
    ) -> CampaignActionResult:
        """Останавливает кампанию.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AutostrategyClient(self.transport).stop_campaign(
            campaign_id=campaign_id or self._require_campaign_id(),
            version=version,
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        limit: int = 100,
        offset: int | None = None,
        status_id: list[int] | None = None,
        order_by: list[tuple[str, str]] | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
    ) -> CampaignsResult:
        """Получает список кампаний.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        filter_payload = (
            CampaignListFilter(
                by_update_time=CampaignUpdateTimeFilter(
                    from_time=updated_from,
                    to_time=updated_to,
                )
            )
            if updated_from is not None or updated_to is not None
            else None
        )
        order_by_payload = (
            [CampaignOrderBy(column=column, direction=direction) for column, direction in order_by]
            if order_by is not None
            else None
        )
        return AutostrategyClient(self.transport).list_campaigns(
            limit=limit,
            offset=offset,
            status_id=status_id,
            order_by=order_by_payload,
            filter=filter_payload,
        )

    def get_stat(self, *, campaign_id: int | None = None) -> AutostrategyStat:
        """Получает статистику кампании.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return AutostrategyClient(self.transport).get_stat(
            campaign_id=campaign_id or self._require_campaign_id()
        )

    def _require_campaign_id(self) -> int:
        if self.campaign_id is None:
            raise ValidationError("Для операции требуется `campaign_id`.")
        return int(self.campaign_id)


__all__ = (
    "AutostrategyCampaign",
    "BbipPromotion",
    "CpaAuction",
    "PromotionOrder",
    "TargetActionPricing",
    "TrxPromotion",
)
