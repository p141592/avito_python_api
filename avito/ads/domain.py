"""Доменные объекты пакета ads."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from avito.ads.client import (
    AdsClient,
    AutoloadArchiveClient,
    AutoloadClient,
    StatsClient,
    VasClient,
)
from avito.ads.models import (
    ActionResult,
    AdItem,
    AdsListResult,
    ApplyVasPackageRequest,
    ApplyVasRequest,
    AutoloadFeesResult,
    AutoloadFieldsResult,
    AutoloadProfileSettings,
    AutoloadProfileUpdateRequest,
    AutoloadReportDetails,
    AutoloadReportItemsResult,
    AutoloadReportsResult,
    AutoloadTreeResult,
    CallsStatsRequest,
    CallsStatsResult,
    IdMappingResult,
    ItemAnalyticsResult,
    ItemStatsRequest,
    ItemStatsResult,
    LegacyAutoloadReport,
    SpendingsResult,
    UpdatePriceRequest,
    UpdatePriceResult,
    UploadByUrlRequest,
    UploadResult,
    VasPricesRequest,
    VasPricesResult,
)
from avito.core import Transport, ValidationError
from avito.promotion.models import PromotionActionResult


def _validate_non_empty_items(name: str, items: Sequence[Any]) -> None:
    if not items:
        raise ValidationError(f"`{name}` must contain at least one item.")


def _validate_non_empty_string(name: str, value: str) -> None:
    if not value.strip():
        raise ValidationError(f"`{name}` must be a non-empty string.")


def _validate_string_items(name: str, values: Sequence[str]) -> None:
    _validate_non_empty_items(name, values)
    for index, value in enumerate(values):
        _validate_non_empty_string(f"{name}[{index}]", value)


def _preview_result(
    *,
    action: str,
    target: dict[str, Any],
    request_payload: dict[str, Any],
) -> PromotionActionResult:
    return PromotionActionResult(
        action=action,
        target=dict(target),
        status="preview",
        applied=False,
        request_payload=dict(request_payload),
        details={"validated": True},
    )


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела ads."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class Ad(DomainObject):
    """Доменный объект объявления."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> AdItem:
        """Получает объявление по `item_id`."""

        item_id, user_id = self._require_ids()
        return AdsClient(self.transport).get_item(user_id=user_id, item_id=item_id)

    def list(
        self, *, status: str | None = None, limit: int | None = None, offset: int | None = None
    ) -> AdsListResult:
        """Получает список объявлений."""

        user_id = int(self.user_id) if self.user_id is not None else None
        return AdsClient(self.transport).list_items(
            user_id=user_id, status=status, limit=limit, offset=offset
        )

    def update_price(self, *, price: int | float) -> UpdatePriceResult:
        """Обновляет цену текущего объявления."""

        item_id = self._require_item_id()
        return AdsClient(self.transport).update_price(
            item_id=item_id, price=UpdatePriceRequest(price=price)
        )

    def get_stats(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        fields: Sequence[str] | None = None,
    ) -> ItemStatsResult:
        """Получает статистику текущего объявления."""

        item_id, user_id = self._require_ids()
        return StatsClient(self.transport).get_item_stats(
            user_id=user_id,
            request=ItemStatsRequest(
                item_ids=[item_id],
                date_from=date_from,
                date_to=date_to,
                fields=list(fields or []),
            ),
        )

    def _require_item_id(self) -> int:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.resource_id)

    def _require_ids(self) -> tuple[int, int]:
        if self.resource_id is None or self.user_id is None:
            raise ValidationError("Для операции требуются `item_id` и `user_id`.")
        return int(self.resource_id), int(self.user_id)


@dataclass(slots=True, frozen=True)
class AdStats(DomainObject):
    """Доменный объект статистики объявлений."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_calls_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> CallsStatsResult:
        """Получает статистику звонков."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.resource_id)] if self.resource_id is not None else []
        )
        return StatsClient(self.transport).get_calls_stats(
            user_id=user_id,
            request=CallsStatsRequest(
                item_ids=resolved_item_ids, date_from=date_from, date_to=date_to
            ),
        )

    def get_item_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> ItemStatsResult:
        """Получает статистику по списку объявлений."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.resource_id)] if self.resource_id is not None else []
        )
        return StatsClient(self.transport).get_item_stats(
            user_id=user_id,
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ),
        )

    def get_item_analytics(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> ItemAnalyticsResult:
        """Получает аналитику по профилю."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.resource_id)] if self.resource_id is not None else []
        )
        return StatsClient(self.transport).get_item_analytics(
            user_id=user_id,
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ),
        )

    def get_account_spendings(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        fields: list[str] | None = None,
    ) -> SpendingsResult:
        """Получает статистику расходов профиля."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.resource_id)] if self.resource_id is not None else []
        )
        return StatsClient(self.transport).get_account_spendings(
            user_id=user_id,
            request=ItemStatsRequest(
                item_ids=resolved_item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields or [],
            ),
        )

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)


@dataclass(slots=True, frozen=True)
class AdPromotion(DomainObject):
    """Доменный объект продвижения объявления."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_vas_prices(
        self, *, item_ids: list[int], location_id: int | None = None
    ) -> VasPricesResult:
        """Получает цены продвижения и доступные услуги."""

        user_id = self._require_user_id()
        return VasClient(self.transport).get_prices(
            user_id=user_id,
            request=VasPricesRequest(item_ids=item_ids, location_id=location_id),
        )

    def apply_vas(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
    ) -> PromotionActionResult:
        """Применяет дополнительные услуги к объявлению."""

        item_id, user_id = self._require_ids()
        _validate_string_items("codes", codes)
        request = ApplyVasRequest(codes=codes)
        request_payload = request.to_payload()
        target = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_item_vas(
            user_id=user_id,
            item_id=item_id,
            request=request,
        )

    def apply_vas_package(
        self,
        *,
        package_code: str,
        dry_run: bool = False,
    ) -> PromotionActionResult:
        """Применяет пакет дополнительных услуг."""

        item_id, user_id = self._require_ids()
        _validate_non_empty_string("package_code", package_code)
        request = ApplyVasPackageRequest(package_code=package_code)
        request_payload = request.to_payload()
        target = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_package",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_item_vas_package(
            user_id=user_id,
            item_id=item_id,
            request=request,
        )

    def apply_vas_direct(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
    ) -> PromotionActionResult:
        """Применяет услуги продвижения через прямой v2 endpoint."""

        item_id = self._require_item_id()
        _validate_string_items("codes", codes)
        request = ApplyVasRequest(codes=codes)
        request_payload = request.to_payload()
        target = {"item_id": item_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_direct",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_vas_direct(
            item_id=item_id,
            request=request,
        )

    def _require_item_id(self) -> int:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.resource_id)

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)

    def _require_ids(self) -> tuple[int, int]:
        return self._require_item_id(), self._require_user_id()


@dataclass(slots=True, frozen=True)
class AutoloadProfile(DomainObject):
    """Доменный объект профиля автозагрузки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> AutoloadProfileSettings:
        """Получает профиль автозагрузки."""

        return AutoloadClient(self.transport).get_profile()

    def save(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
    ) -> ActionResult:
        """Сохраняет профиль автозагрузки."""

        return AutoloadClient(self.transport).save_profile(
            AutoloadProfileUpdateRequest(
                is_enabled=is_enabled, email=email, callback_url=callback_url
            )
        )

    def upload_by_url(self, *, url: str) -> UploadResult:
        """Загружает файл по ссылке."""

        return AutoloadClient(self.transport).upload_by_url(UploadByUrlRequest(url=url))

    def get_tree(self) -> AutoloadTreeResult:
        """Получает дерево категорий."""

        return AutoloadClient(self.transport).get_tree()

    def get_node_fields(self, *, node_slug: str) -> AutoloadFieldsResult:
        """Получает поля категории."""

        return AutoloadClient(self.transport).get_node_fields(node_slug=node_slug)


@dataclass(slots=True, frozen=True)
class AutoloadReport(DomainObject):
    """Доменный объект отчета автозагрузки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> AutoloadReportDetails:
        """Получает конкретный отчет v3."""

        report_id = self._require_report_id()
        return AutoloadClient(self.transport).get_report(report_id=report_id)

    def list(self, *, limit: int | None = None, offset: int | None = None) -> AutoloadReportsResult:
        """Получает список отчетов автозагрузки."""

        return AutoloadClient(self.transport).list_reports(limit=limit, offset=offset)

    def get_last_completed(self) -> AutoloadReportDetails:
        """Получает последний завершенный отчет."""

        return AutoloadClient(self.transport).get_last_completed_report()

    def get_items(self) -> AutoloadReportItemsResult:
        """Получает объявления из отчета."""

        report_id = self._require_report_id()
        return AutoloadClient(self.transport).get_report_items(report_id=report_id)

    def get_fees(self) -> AutoloadFeesResult:
        """Получает списания по объявлениям отчета."""

        report_id = self._require_report_id()
        return AutoloadClient(self.transport).get_report_fees(report_id=report_id)

    def get_ad_ids_by_avito_ids(self, *, avito_ids: Sequence[int]) -> IdMappingResult:
        """Получает ad ids по avito ids."""

        return AutoloadClient(self.transport).get_ad_ids_by_avito_ids(avito_ids=list(avito_ids))

    def get_avito_ids_by_ad_ids(self, *, ad_ids: Sequence[int]) -> IdMappingResult:
        """Получает avito ids по ad ids."""

        return AutoloadClient(self.transport).get_avito_ids_by_ad_ids(ad_ids=list(ad_ids))

    def get_items_info(self, *, item_ids: Sequence[int]) -> AutoloadReportItemsResult:
        """Получает информацию по объявлениям автозагрузки."""

        return AutoloadClient(self.transport).get_items_info(item_ids=list(item_ids))

    def _require_report_id(self) -> int:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutoloadArchive(DomainObject):
    """Доменный объект архивных операций автозагрузки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_profile(self) -> AutoloadProfileSettings:
        """Получает архивный профиль автозагрузки."""

        return AutoloadArchiveClient(self.transport).get_profile()

    def save_profile(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
    ) -> ActionResult:
        """Сохраняет архивный профиль автозагрузки."""

        return AutoloadArchiveClient(self.transport).save_profile(
            AutoloadProfileUpdateRequest(
                is_enabled=is_enabled, email=email, callback_url=callback_url
            )
        )

    def get_last_completed_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по последней выгрузке."""

        return AutoloadArchiveClient(self.transport).get_last_completed_report()

    def get_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по конкретной выгрузке."""

        report_id = self._require_report_id()
        return AutoloadArchiveClient(self.transport).get_report(report_id=report_id)

    def _require_report_id(self) -> int:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.resource_id)


__all__ = (
    "DomainObject",
    "Ad",
    "AdStats",
    "AdPromotion",
    "AutoloadProfile",
    "AutoloadReport",
    "AutoloadArchive",
)
