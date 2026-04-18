"""Доменные объекты пакета autoteka."""

from __future__ import annotations

from collections.abc import Mapping
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
    CatalogResolveResult,
    JsonRequest,
    MonitoringBucketResult,
    MonitoringEventsResult,
)
from avito.core import Transport


@dataclass(slots=True, frozen=True)
class DomainObject:
    """Базовый доменный объект раздела autoteka."""

    transport: Transport


@dataclass(slots=True, frozen=True)
class AutotekaVehicle(DomainObject):
    """Доменный объект превью, спецификаций, тизеров и каталога."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_catalogs_resolve(self, *, payload: Mapping[str, object]) -> CatalogResolveResult:
        return CatalogClient(self.transport).get_catalogs_resolve(JsonRequest(payload))

    def get_leads(self, *, payload: Mapping[str, object]) -> AutotekaLeadsResult:
        return LeadsClient(self.transport).get_leads(JsonRequest(payload))

    def create_preview_by_vin(self, *, payload: Mapping[str, object]) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_vin(JsonRequest(payload))

    def get_preview(self, *, preview_id: int | str | None = None) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).get_preview(preview_id=preview_id or self._require_resource_id("preview_id"))

    def create_preview_by_external_item(self, *, payload: Mapping[str, object]) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_external_item(JsonRequest(payload))

    def create_preview_by_item_id(self, *, payload: Mapping[str, object]) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_item_id(JsonRequest(payload))

    def create_preview_by_reg_number(self, *, payload: Mapping[str, object]) -> AutotekaPreviewInfo:
        return PreviewClient(self.transport).create_by_reg_number(JsonRequest(payload))

    def create_specification_by_plate_number(self, *, payload: Mapping[str, object]) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_plate_number(JsonRequest(payload))

    def create_specification_by_vehicle_id(self, *, payload: Mapping[str, object]) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).create_by_vehicle_id(JsonRequest(payload))

    def get_specification_get_by_id(
        self,
        *,
        specification_id: int | str | None = None,
    ) -> AutotekaSpecificationInfo:
        return SpecificationsClient(self.transport).get_by_id(
            specification_id=specification_id or self._require_resource_id("specification_id")
        )

    def create_teaser(self, *, payload: Mapping[str, object]) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).create(JsonRequest(payload))

    def get_teaser(self, *, teaser_id: int | str | None = None) -> AutotekaTeaserInfo:
        return TeaserClient(self.transport).get(teaser_id=teaser_id or self._require_resource_id("teaser_id"))

    def _require_resource_id(self, field_name: str) -> str:
        if self.resource_id is None:
            raise ValueError(f"Для операции требуется `{field_name}`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaReport(DomainObject):
    """Доменный объект отчетов и пакетов Автотеки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_active_package(self) -> AutotekaPackageInfo:
        return ReportClient(self.transport).get_active_package()

    def create_report(self, *, payload: Mapping[str, object]) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report(JsonRequest(payload))

    def create_report_by_vehicle_id(self, *, payload: Mapping[str, object]) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_report_by_vehicle_id(JsonRequest(payload))

    def list_report_list(self) -> AutotekaReportsResult:
        return ReportClient(self.transport).list_reports()

    def get_report(self, *, report_id: int | str | None = None) -> AutotekaReportInfo:
        return ReportClient(self.transport).get_report(report_id=report_id or self._require_resource_id())

    def create_sync_create_report_by_reg_number(self, *, payload: Mapping[str, object]) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_reg_number(JsonRequest(payload))

    def create_sync_create_report_by_vin(self, *, payload: Mapping[str, object]) -> AutotekaReportInfo:
        return ReportClient(self.transport).create_sync_report_by_vin(JsonRequest(payload))

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `report_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaMonitoring(DomainObject):
    """Доменный объект мониторинга Автотеки."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_monitoring_bucket_add(self, *, payload: Mapping[str, object]) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).add_bucket(JsonRequest(payload))

    def list_monitoring_bucket_delete(self) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).delete_bucket()

    def delete_monitoring_bucket_remove(self, *, payload: Mapping[str, object]) -> MonitoringBucketResult:
        return MonitoringClient(self.transport).remove_bucket(JsonRequest(payload))

    def get_monitoring_get_reg_actions(
        self,
        *,
        params: Mapping[str, object] | None = None,
    ) -> MonitoringEventsResult:
        return MonitoringClient(self.transport).get_reg_actions(params=params)


@dataclass(slots=True, frozen=True)
class AutotekaScoring(DomainObject):
    """Доменный объект скоринга рисков."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def create_scoring_by_vehicle_id(self, *, payload: Mapping[str, object]) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).create_by_vehicle_id(JsonRequest(payload))

    def get_scoring_get_by_id(self, *, scoring_id: int | str | None = None) -> AutotekaScoringInfo:
        return ScoringClient(self.transport).get_by_id(scoring_id=scoring_id or self._require_resource_id())

    def _require_resource_id(self) -> str:
        if self.resource_id is None:
            raise ValueError("Для операции требуется `scoring_id`.")
        return str(self.resource_id)


@dataclass(slots=True, frozen=True)
class AutotekaValuation(DomainObject):
    """Доменный объект оценки автомобиля."""

    resource_id: int | str | None = None
    user_id: int | str | None = None

    def get_valuation_by_specification(self, *, payload: Mapping[str, object]) -> AutotekaValuationInfo:
        return ValuationClient(self.transport).get_by_specification(JsonRequest(payload))


__all__ = ("AutotekaMonitoring", "AutotekaReport", "AutotekaScoring", "AutotekaValuation", "AutotekaVehicle", "DomainObject")
