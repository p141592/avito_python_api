"""Доменные объекты пакета ads."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from avito.ads.client import (
    AdsClient,
    AutoloadArchiveClient,
    AutoloadClient,
    StatsClient,
    VasClient,
)
from avito.ads.enums import ListingStatus
from avito.ads.models import (
    AccountSpendings,
    AdsActionResult,
    ApplyVasPackageRequest,
    ApplyVasRequest,
    AutoloadFeesResult,
    AutoloadFieldsResult,
    AutoloadProfileSettings,
    AutoloadReportDetails,
    AutoloadReportItemsResult,
    AutoloadReportSummary,
    AutoloadTreeResult,
    CallsStatsResult,
    IdMappingResult,
    ItemAnalyticsResult,
    ItemStatsResult,
    LegacyAutoloadReport,
    Listing,
    UpdatePriceResult,
    UploadResult,
    VasPricesResult,
)
from avito.core import PaginatedList, ValidationError
from avito.core.deprecation import deprecated_method
from avito.core.domain import DomainObject
from avito.core.validation import (
    validate_non_empty_string,
    validate_string_items,
)
from avito.promotion.enums import PromotionStatus
from avito.promotion.models import PromotionActionResult


def _preview_result(
    *,
    action: str,
    target: dict[str, object],
    request_payload: dict[str, object],
) -> PromotionActionResult:
    return PromotionActionResult(
        action=action,
        target=target,
        status=PromotionStatus.PREVIEW,
        applied=False,
        request_payload=request_payload,
        details={"validated": True},
    )


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass(slots=True, frozen=True)
class Ad(DomainObject):
    """Доменный объект объявления."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get(self) -> Listing:
        """Получает объявление по `item_id`."""

        item_id, user_id = self._require_ids()
        return AdsClient(self.transport).get_item(user_id=user_id, item_id=item_id)

    def list(
        self,
        *,
        status: ListingStatus | str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> PaginatedList[Listing]:
        """Получает список объявлений."""

        user_id = int(self.user_id) if self.user_id is not None else None
        return AdsClient(self.transport).list_items(
            user_id=user_id, status=status, limit=limit, offset=offset
        )

    def update_price(
        self,
        *,
        price: int | float,
        idempotency_key: str | None = None,
    ) -> UpdatePriceResult:
        """Обновляет цену текущего объявления."""

        item_id = self._require_item_id()
        return AdsClient(self.transport).update_price(
            item_id=item_id,
            price=price,
            idempotency_key=idempotency_key,
        )

    def _require_item_id(self) -> int:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id)

    def _require_ids(self) -> tuple[int, int]:
        if self.item_id is None or self.user_id is None:
            raise ValidationError("Для операции требуются `item_id` и `user_id`.")
        return int(self.item_id), int(self.user_id)


@dataclass(slots=True, frozen=True)
class AdStats(DomainObject):
    """Доменный объект статистики объявлений."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_calls_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> CallsStatsResult:
        """Получает статистику звонков."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.item_id)] if self.item_id is not None else []
        )
        return StatsClient(self.transport).get_calls_stats(
            user_id=user_id,
            item_ids=resolved_item_ids,
            date_from=_serialize_datetime(date_from),
            date_to=_serialize_datetime(date_to),
        )

    def get_item_stats(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        fields: list[str] | None = None,
    ) -> ItemStatsResult:
        """Получает статистику по списку объявлений."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.item_id)] if self.item_id is not None else []
        )
        return StatsClient(self.transport).get_item_stats(
            user_id=user_id,
            item_ids=resolved_item_ids,
            date_from=_serialize_datetime(date_from),
            date_to=_serialize_datetime(date_to),
            fields=fields or [],
        )

    def get_item_analytics(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        fields: list[str] | None = None,
    ) -> ItemAnalyticsResult:
        """Получает аналитику по профилю."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.item_id)] if self.item_id is not None else []
        )
        return StatsClient(self.transport).get_item_analytics(
            user_id=user_id,
            item_ids=resolved_item_ids,
            date_from=_serialize_datetime(date_from),
            date_to=_serialize_datetime(date_to),
            fields=fields or [],
        )

    def get_account_spendings(
        self,
        *,
        item_ids: list[int] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        fields: list[str] | None = None,
    ) -> AccountSpendings:
        """Получает статистику расходов профиля."""

        user_id = self._require_user_id()
        resolved_item_ids = item_ids or (
            [int(self.item_id)] if self.item_id is not None else []
        )
        return StatsClient(self.transport).get_account_spendings(
            user_id=user_id,
            item_ids=resolved_item_ids,
            date_from=_serialize_datetime(date_from),
            date_to=_serialize_datetime(date_to),
            fields=fields or [],
        )

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)


@dataclass(slots=True, frozen=True)
class AdPromotion(DomainObject):
    """Доменный объект продвижения объявления."""

    item_id: int | str | None = None
    user_id: int | str | None = None

    def get_vas_prices(
        self, *, item_ids: list[int], location_id: int | None = None
    ) -> VasPricesResult:
        """Получает цены продвижения и доступные услуги."""

        user_id = self._require_user_id()
        return VasClient(self.transport).get_prices(
            user_id=user_id,
            item_ids=item_ids,
            location_id=location_id,
        )

    def apply_vas(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет дополнительные услуги к объявлению."""

        item_id, user_id = self._require_ids()
        validate_string_items("codes", codes)
        request_payload = ApplyVasRequest(codes=codes).to_payload()
        target: dict[str, object] = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_item_vas(
            user_id=user_id,
            item_id=item_id,
            codes=codes,
            idempotency_key=idempotency_key,
        )

    def apply_vas_package(
        self,
        *,
        package_code: str,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет пакет дополнительных услуг."""

        item_id, user_id = self._require_ids()
        validate_non_empty_string("package_code", package_code)
        request_payload = ApplyVasPackageRequest(package_code=package_code).to_payload()
        target: dict[str, object] = {"item_id": item_id, "user_id": user_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_package",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_item_vas_package(
            user_id=user_id,
            item_id=item_id,
            package_code=package_code,
            idempotency_key=idempotency_key,
        )

    def apply_vas_direct(
        self,
        *,
        codes: list[str],
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> PromotionActionResult:
        """Применяет услуги продвижения через прямой v2 endpoint."""

        item_id = self._require_item_id()
        validate_string_items("codes", codes)
        request_payload = ApplyVasRequest(codes=codes).to_payload()
        target: dict[str, object] = {"item_id": item_id}
        if dry_run:
            return _preview_result(
                action="apply_vas_direct",
                target=target,
                request_payload=request_payload,
            )
        return VasClient(self.transport).apply_vas_direct(
            item_id=item_id,
            codes=codes,
            idempotency_key=idempotency_key,
        )

    def _require_item_id(self) -> int:
        if self.item_id is None:
            raise ValidationError("Для операции требуется `item_id`.")
        return int(self.item_id)

    def _require_user_id(self) -> int:
        if self.user_id is None:
            raise ValidationError("Для операции требуется `user_id`.")
        return int(self.user_id)

    def _require_ids(self) -> tuple[int, int]:
        return self._require_item_id(), self._require_user_id()


@dataclass(slots=True, frozen=True)
class AutoloadProfile(DomainObject):
    """Доменный объект профиля автозагрузки."""

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
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Сохраняет профиль автозагрузки."""

        return AutoloadClient(self.transport).save_profile(
            is_enabled=is_enabled,
            email=email,
            callback_url=callback_url,
            idempotency_key=idempotency_key,
        )

    def upload_by_url(self, *, url: str, idempotency_key: str | None = None) -> UploadResult:
        """Загружает файл по ссылке."""

        return AutoloadClient(self.transport).upload_by_url(
            url=url,
            idempotency_key=idempotency_key,
        )

    def get_tree(self) -> AutoloadTreeResult:
        """Получает дерево категорий."""

        return AutoloadClient(self.transport).get_tree()

    def get_node_fields(self, *, node_slug: str) -> AutoloadFieldsResult:
        """Получает поля категории."""

        return AutoloadClient(self.transport).get_node_fields(node_slug=node_slug)


@dataclass(slots=True, frozen=True)
class AutoloadReport(DomainObject):
    """Доменный объект отчета автозагрузки."""

    report_id: int | str | None = None

    def get(self) -> AutoloadReportDetails:
        """Получает конкретный отчет v3."""

        report_id = self._require_report_id()
        return AutoloadClient(self.transport).get_report(report_id=report_id)

    def list(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> PaginatedList[AutoloadReportSummary]:
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
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.report_id)


@dataclass(slots=True, frozen=True)
class AutoloadArchive(DomainObject):
    """Доменный объект архивных операций автозагрузки."""

    report_id: int | str | None = None

    @deprecated_method(
        symbol="AutoloadArchive.get_profile",
        replacement="autoload_profile().get",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_profile(self) -> AutoloadProfileSettings:
        """Получает архивный профиль автозагрузки.

        Deprecated: используйте `autoload_profile().get`; удаление в версии 1.3.0.
        """

        return AutoloadArchiveClient(self.transport).get_profile()

    @deprecated_method(
        symbol="AutoloadArchive.save_profile",
        replacement="autoload_profile().save",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def save_profile(
        self,
        *,
        is_enabled: bool | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> AdsActionResult:
        """Сохраняет архивный профиль автозагрузки.

        Deprecated: используйте `autoload_profile().save`; удаление в версии 1.3.0.
        """

        return AutoloadArchiveClient(self.transport).save_profile(
            is_enabled=is_enabled,
            email=email,
            callback_url=callback_url,
            idempotency_key=idempotency_key,
        )

    @deprecated_method(
        symbol="AutoloadArchive.get_last_completed_report",
        replacement="autoload_report().get_last_completed",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_last_completed_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по последней выгрузке.

        Deprecated: используйте `autoload_report().get_last_completed`; удаление в версии 1.3.0.
        """

        return AutoloadArchiveClient(self.transport).get_last_completed_report()

    @deprecated_method(
        symbol="AutoloadArchive.get_report",
        replacement="autoload_report().get",
        removal_version="1.3.0",
        deprecated_since="1.1.0",
    )
    def get_report(self) -> LegacyAutoloadReport:
        """Получает архивную статистику по конкретной выгрузке.

        Deprecated: используйте `autoload_report().get`; удаление в версии 1.3.0.
        """

        report_id = self._require_report_id()
        return AutoloadArchiveClient(self.transport).get_report(report_id=report_id)

    def _require_report_id(self) -> int:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return int(self.report_id)


__all__ = (
    "Ad",
    "AdPromotion",
    "AdStats",
    "AutoloadArchive",
    "AutoloadProfile",
    "AutoloadReport",
)
