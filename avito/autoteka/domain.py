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
    AutotekaQuery,
    AutotekaReportInfo,
    AutotekaReportsResult,
    AutotekaRequest,
    AutotekaScoringInfo,
    AutotekaSpecificationInfo,
    AutotekaTeaserInfo,
    AutotekaValuationInfo,
    CatalogResolveResult,
    MonitoringBucketResult,
    MonitoringEventsResult,
)
from avito.core import Transport, ValidationError


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела autoteka."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class AutotekaVehicle(DomainObject):
    """Доменный объект превью, спецификаций, тизеров и каталога."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_catalogs_resolve(self, *, request: AutotekaRequest) -> CatalogResolveResult:
        return CatalogClient(self.transport).get_catalogs_resolve(request)

    def get_leads(self, *, request: AutotekaRequest) -> AutotekaLeadsResult:
        return LeadsClient(self.transport).get_leads(request)

    def create_preview_by_vin(self, *, request: AutotekaRequest) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_vin(request)

    def get_preview(self, *, preview_id: int | str | None = None) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).get_preview(
            preview_id=preview_id or self._require_resource_id("preview_id")
        )

    def create_preview_by_external_item(
        self, *, request: AutotekaRequest
    ) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_external_item(request)

    def create_preview_by_item_id(self, *, request: AutotekaRequest) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_item_id(request)

    def create_preview_by_reg_number(self, *, request: AutotekaRequest) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_reg_number(request)

    def create_specification_by_plate_number(
        self, *, request: AutotekaRequest
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_plate_number(request)

    def create_specification_by_vehicle_id(
        self, *, request: AutotekaRequest
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_vehicle_id(request)

    def get_specification_by_id(
        self,
        *,
        specification_id: int | str | None = None,
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).get_by_id(
            specification_id=specification_id or self._require_resource_id("specification_id")
        )

    def create_teaser(self, *, request: AutotekaRequest) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).create(request)

    def get_teaser(self, *, teaser_id: int | str | None = None) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).get(
            teaser_id=teaser_id or self._require_resource_id("teaser_id")
        )

    def _require_resource_id(self, field_name: str) -> str:
        if self.resource_id is None:
            raise ValidationError(f"Для операции требуется `{field_name}`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaReport(DomainObject):
    """Доменный объект отчетов и пакетов Автотеки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_active_package(self) -> AutotekaPackageInfo:
        return ReportClient(self.transport).get_active_package()

    def create_report(self, *, request: AutotekaRequest) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report(request)

    def create_report_by_vehicle_id(self, *, request: AutotekaRequest) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report_by_vehicle_id(request)

    def list_report_list(self) -> AutotekaReportsResult:
        return ReportClient(self.transport).list_reports()

    def get_report(self, *, report_id: int | str | None = None) -> AutotekaReportInfo:
        return ReportClient(self.transport).get_report(
            report_id=report_id or self._require_resource_id()
        )

    def create_sync_report_by_reg_number(
        self, *, request: AutotekaRequest
    ) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_reg_number(request)

    def create_sync_report_by_vin(
        self, *, request: AutotekaRequest
    ) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_vin(request)

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaMonitoring(DomainObject):
    """Доменный объект мониторинга Автотеки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_monitoring_bucket_add(
        self, *, request: AutotekaRequest
    ) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).add_bucket(request)

    def list_monitoring_bucket_delete(self) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).delete_bucket()

    def delete_monitoring_bucket_remove(
        self, *, request: AutotekaRequest
    ) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).remove_bucket(request)

    def get_monitoring_reg_actions(
        self,
        *,
        query: AutotekaQuery | None = None,
    ) -> MonitoringEventsResult:
        return MonitoringClient(self.transport).get_reg_actions(query=query)


@dataclass(slots=True, frozen=True)
class AutotekaScoring(DomainObject):
    """Доменный объект скоринга рисков."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_scoring_by_vehicle_id(self, *, request: AutotekaRequest) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).create_by_vehicle_id(request)

    def get_scoring_by_id(self, *, scoring_id: int | str | None = None) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).get_by_id(
            scoring_id=scoring_id or self._require_resource_id()
        )

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValidationError("Для операции требуется `scoring_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaValuation(DomainObject):
    """Доменный объект оценки автомобиля."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_valuation_by_specification(
        self, *, request: AutotekaRequest
    ) -> AutotekaValuationInfo:
        return ValuationClient(self.transport).get_by_specification(request)


__all__ = (
    "AutotekaMonitoring",
    "AutotekaReport",
    "AutotekaScoring",
    "AutotekaValuation",
    "AutotekaVehicle",
    "DomainObject",
)
