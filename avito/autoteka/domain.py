"""Доменные объекты пакета autoteka."""

from __future__ import annotations

from dataclasses import dataclass

from avito.autoteka.client import (
    CatalogClient,
    LeadsClient,
    MonitoringClient,
    PreviewClient,
    ReportClient,
    ScoringClient,
    SpecificationsClient,
    TeaserClient,
    ValuationClient,
)
from avito.autoteka.models import (
    AutotekaLeadsResult,
    AutotekaPackageInfo,
    AutotekaPreviewInfo,
    AutotekaReportInfo,
    AutotekaReportsResult,
    AutotekaScoringInfo,
    AutotekaSpecificationInfo,
    AutotekaTeaserInfo,
    AutotekaValuationInfo,
    CatalogResolveRequest,
    CatalogResolveResult,
    ExternalItemPreviewRequest,
    ItemIdRequest,
    LeadsRequest,
    MonitoringBucketRequest,
    MonitoringBucketResult,
    MonitoringEventsQuery,
    MonitoringEventsResult,
    PlateNumberRequest,
    PreviewReportRequest,
    RegNumberRequest,
    TeaserCreateRequest,
    ValuationBySpecificationRequest,
    VehicleIdRequest,
    VinRequest,
)
from avito.core import ValidationError
from avito.core.domain import DomainObject


@dataclass(slots=True, frozen=True)
class AutotekaVehicle(DomainObject):
    """Доменный объект превью, спецификаций, тизеров и каталога."""

    vehicle_id: int | str | None = None
    user_id: int | str | None = None

    def resolve_catalog(self, *, brand_id: int) -> CatalogResolveResult:
        """Актуализирует параметры автокаталога."""

        return CatalogClient(self.transport).resolve_catalog(CatalogResolveRequest(brand_id=brand_id))

    def get_leads(self, *, limit: int) -> AutotekaLeadsResult:
        return LeadsClient(self.transport).get_leads(LeadsRequest(limit=limit))

    def create_preview_by_vin(self, *, vin: str) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_vin(VinRequest(vin=vin))

    def get_preview(self, *, preview_id: int | str | None = None) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).get_preview(
            preview_id=preview_id or self._require_vehicle_id("preview_id")
        )

    def create_preview_by_external_item(self, *, item_id: str, site: str) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_external_item(
            ExternalItemPreviewRequest(item_id=item_id, site=site)
        )

    def create_preview_by_item_id(self, *, item_id: int) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_item_id(ItemIdRequest(item_id=item_id))

    def create_preview_by_reg_number(self, *, reg_number: str) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_reg_number(
            RegNumberRequest(reg_number=reg_number)
        )

    def create_specification_by_plate_number(
        self, *, plate_number: str
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_plate_number(
            PlateNumberRequest(plate_number=plate_number)
        )

    def create_specification_by_vehicle_id(
        self, *, vehicle_id: str
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_vehicle_id(
            VehicleIdRequest(vehicle_id=vehicle_id)
        )

    def get_specification_by_id(
        self,
        *,
        specification_id: int | str | None = None,
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).get_by_id(
            specification_id=specification_id or self._require_vehicle_id("specification_id")
        )

    def create_teaser(self, *, vehicle_id: str) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).create(TeaserCreateRequest(vehicle_id=vehicle_id))

    def get_teaser(self, *, teaser_id: int | str | None = None) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).get(
            teaser_id=teaser_id or self._require_vehicle_id("teaser_id")
        )

    def _require_vehicle_id(self, field_name: str) -> str:
        if self.vehicle_id is None:
            raise ValidationError(f"Для операции требуется `{field_name}`.")
        return str(self.vehicle_id)


@dataclass(slots=True, frozen=True)
class AutotekaReport(DomainObject):
    """Доменный объект отчетов и пакетов Автотеки."""

    report_id: int | str | None = None
    user_id: int | str | None = None

    def get_active_package(self) -> AutotekaPackageInfo:
        return ReportClient(self.transport).get_active_package()

    def create_report(self, *, preview_id: int) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report(PreviewReportRequest(preview_id=preview_id))

    def create_report_by_vehicle_id(self, *, vehicle_id: str) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report_by_vehicle_id(
            VehicleIdRequest(vehicle_id=vehicle_id)
        )

    def list_reports(self) -> AutotekaReportsResult:
        """Получает список отчетов Автотеки."""

        return ReportClient(self.transport).list_reports()

    def get_report(self, *, report_id: int | str | None = None) -> AutotekaReportInfo:
        return ReportClient(self.transport).get_report(
            report_id=report_id or self._require_report_id()
        )

    def create_sync_report_by_reg_number(self, *, reg_number: str) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_reg_number(
            RegNumberRequest(reg_number=reg_number)
        )

    def create_sync_report_by_vin(self, *, vin: str) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_vin(VinRequest(vin=vin))

    def _require_report_id(self) -> str:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return str(self.report_id)


@dataclass(slots=True, frozen=True)
class AutotekaMonitoring(DomainObject):
    """Доменный объект мониторинга Автотеки."""

    user_id: int | str | None = None

    def create_monitoring_bucket_add(self, *, vehicles: list[str]) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).add_bucket(
            MonitoringBucketRequest(vehicles=vehicles)
        )

    def delete_bucket(self) -> MonitoringBucketResult:
        """Очищает bucket мониторинга."""

        return MonitoringClient(self.transport).delete_bucket()

    def remove_bucket(self, *, vehicles: list[str]) -> MonitoringBucketResult:
        """Удаляет автомобили из bucket мониторинга."""

        return MonitoringClient(self.transport).remove_bucket(
            MonitoringBucketRequest(vehicles=vehicles)
        )

    def get_monitoring_reg_actions(
        self,
        *,
        query: MonitoringEventsQuery | None = None,
    ) -> MonitoringEventsResult:
        return MonitoringClient(self.transport).get_reg_actions(query=query)


@dataclass(slots=True, frozen=True)
class AutotekaScoring(DomainObject):
    """Доменный объект скоринга рисков."""

    scoring_id: int | str | None = None
    user_id: int | str | None = None

    def create_scoring_by_vehicle_id(self, *, vehicle_id: str) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).create_by_vehicle_id(
            VehicleIdRequest(vehicle_id=vehicle_id)
        )

    def get_scoring_by_id(self, *, scoring_id: int | str | None = None) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).get_by_id(
            scoring_id=scoring_id or self._require_scoring_id()
        )

    def _require_scoring_id(self) -> str:
        if self.scoring_id is None:
            raise ValidationError("Для операции требуется `scoring_id`.")
        return str(self.scoring_id)


@dataclass(slots=True, frozen=True)
class AutotekaValuation(DomainObject):
    """Доменный объект оценки автомобиля."""

    user_id: int | str | None = None

    def get_valuation_by_specification(
        self, *, specification_id: int, mileage: int
    ) -> AutotekaValuationInfo:
        return ValuationClient(self.transport).get_by_specification(
            ValuationBySpecificationRequest(specification_id=specification_id, mileage=mileage)
        )


__all__ = (
    "AutotekaMonitoring",
    "AutotekaReport",
    "AutotekaScoring",
    "AutotekaValuation",
    "AutotekaVehicle",
)
