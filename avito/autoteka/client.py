"""Внутренние section clients для пакета autoteka."""

from __future__ import annotations

from dataclasses import dataclass

from avito.autoteka.mappers import (
    map_catalogs_resolve,
    map_leads,
    map_monitoring_bucket,
    map_monitoring_events,
    map_package,
    map_preview,
    map_report,
    map_reports,
    map_scoring,
    map_specification,
    map_teaser,
    map_valuation,
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
from avito.core import RequestContext, Transport


@dataclass(slots=True)
class AutotekaBaseClient:
    """Базовый клиент Автотеки с отдельным access token."""

    transport: Transport

    def _context(self, operation_name: str, *, allow_retry: bool = False) -> RequestContext:
        auth_provider = getattr(self.transport, "_auth_provider", None)
        headers: dict[str, str] = {}
        if auth_provider is not None:
            headers["Authorization"] = f"Bearer {auth_provider.get_autoteka_access_token()}"
        return RequestContext(
            operation_name,
            allow_retry=allow_retry,
            requires_auth=False,
            headers=headers,
        )


@dataclass(slots=True)
class CatalogClient(AutotekaBaseClient):
    """Выполняет HTTP-операции автокаталога."""

    def get_catalogs_resolve(self, request: CatalogResolveRequest) -> CatalogResolveResult:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/catalogs/resolve",
            context=self._context("autoteka.catalog.resolve", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_catalogs_resolve(payload)


@dataclass(slots=True)
class LeadsClient(AutotekaBaseClient):
    """Выполняет HTTP-операции сервиса Сигнал."""

    def get_leads(self, request: LeadsRequest) -> AutotekaLeadsResult:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/get-leads/",
            context=self._context("autoteka.leads.get", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_leads(payload)


@dataclass(slots=True)
class PreviewClient(AutotekaBaseClient):
    """Выполняет HTTP-операции превью автомобиля."""

    def create_by_vin(self, request: VinRequest) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/previews", "autoteka.preview.create_by_vin", request
        )

    def create_by_external_item(self, request: ExternalItemPreviewRequest) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-external-item",
            "autoteka.preview.create_by_external_item",
            request,
        )

    def create_by_item_id(self, request: ItemIdRequest) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-item-id",
            "autoteka.preview.create_by_item_id",
            request,
        )

    def create_by_reg_number(self, request: RegNumberRequest) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-regnumber",
            "autoteka.preview.create_by_reg_number",
            request,
        )

    def get_preview(self, *, preview_id: int | str) -> AutotekaPreviewInfo:
        payload = self.transport.request_json(
            "GET",
            f"/autoteka/v1/previews/{preview_id}",
            context=self._context("autoteka.preview.get"),
        )
        return map_preview(payload)

    def _post_preview(
        self,
        path: str,
        operation: str,
        request: VinRequest | ExternalItemPreviewRequest | ItemIdRequest | RegNumberRequest,
    ) -> AutotekaPreviewInfo:
        payload = self.transport.request_json(
            "POST",
            path,
            context=self._context(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_preview(payload)


@dataclass(slots=True)
class ReportClient(AutotekaBaseClient):
    """Выполняет HTTP-операции отчетов Автотеки."""

    def get_active_package(self) -> AutotekaPackageInfo:
        payload = self.transport.request_json(
            "GET",
            "/autoteka/v1/packages/active_package",
            context=self._context("autoteka.report.get_active_package"),
        )
        return map_package(payload)

    def create_report(self, request: PreviewReportRequest) -> AutotekaReportInfo:
        return self._post_report("/autoteka/v1/reports", "autoteka.report.create", request)

    def create_report_by_vehicle_id(self, request: VehicleIdRequest) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/reports-by-vehicle-id",
            "autoteka.report.create_by_vehicle_id",
            request,
        )

    def list_reports(self) -> AutotekaReportsResult:
        payload = self.transport.request_json(
            "GET",
            "/autoteka/v1/reports/list/",
            context=self._context("autoteka.report.list"),
        )
        return map_reports(payload)

    def get_report(self, *, report_id: int | str) -> AutotekaReportInfo:
        payload = self.transport.request_json(
            "GET",
            f"/autoteka/v1/reports/{report_id}",
            context=self._context("autoteka.report.get"),
        )
        return map_report(payload)

    def create_sync_report_by_reg_number(self, request: RegNumberRequest) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/sync/create-by-regnumber",
            "autoteka.report.create_sync_by_reg_number",
            request,
        )

    def create_sync_report_by_vin(self, request: VinRequest) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/sync/create-by-vin",
            "autoteka.report.create_sync_by_vin",
            request,
        )

    def _post_report(
        self,
        path: str,
        operation: str,
        request: PreviewReportRequest | VehicleIdRequest | RegNumberRequest | VinRequest,
    ) -> AutotekaReportInfo:
        payload = self.transport.request_json(
            "POST",
            path,
            context=self._context(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_report(payload)


@dataclass(slots=True)
class MonitoringClient(AutotekaBaseClient):
    """Выполняет HTTP-операции мониторинга."""

    def add_bucket(self, request: MonitoringBucketRequest) -> MonitoringBucketResult:
        return self._post_bucket(
            "/autoteka/v1/monitoring/bucket/add",
            "autoteka.monitoring.bucket_add",
            request,
        )

    def delete_bucket(self) -> MonitoringBucketResult:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/monitoring/bucket/delete",
            context=self._context("autoteka.monitoring.bucket_delete", allow_retry=True),
        )
        return map_monitoring_bucket(payload)

    def remove_bucket(self, request: MonitoringBucketRequest) -> MonitoringBucketResult:
        return self._post_bucket(
            "/autoteka/v1/monitoring/bucket/remove",
            "autoteka.monitoring.bucket_remove",
            request,
        )

    def get_reg_actions(
        self, *, query: MonitoringEventsQuery | None = None
    ) -> MonitoringEventsResult:
        payload = self.transport.request_json(
            "GET",
            "/autoteka/v1/monitoring/get-reg-actions/",
            context=self._context("autoteka.monitoring.get_reg_actions"),
            params=query.to_params() if query is not None else None,
        )
        return map_monitoring_events(payload)

    def _post_bucket(
        self,
        path: str,
        operation: str,
        request: MonitoringBucketRequest,
    ) -> MonitoringBucketResult:
        payload = self.transport.request_json(
            "POST",
            path,
            context=self._context(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_monitoring_bucket(payload)


@dataclass(slots=True)
class ScoringClient(AutotekaBaseClient):
    """Выполняет HTTP-операции скоринга рисков."""

    def create_by_vehicle_id(self, request: VehicleIdRequest) -> AutotekaScoringInfo:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/scoring/by-vehicle-id",
            context=self._context("autoteka.scoring.create_by_vehicle_id", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_scoring(payload)

    def get_by_id(self, *, scoring_id: int | str) -> AutotekaScoringInfo:
        payload = self.transport.request_json(
            "GET",
            f"/autoteka/v1/scoring/{scoring_id}",
            context=self._context("autoteka.scoring.get_by_id"),
        )
        return map_scoring(payload)


@dataclass(slots=True)
class SpecificationsClient(AutotekaBaseClient):
    """Выполняет HTTP-операции спецификаций автомобиля."""

    def create_by_plate_number(self, request: PlateNumberRequest) -> AutotekaSpecificationInfo:
        return self._post_specification(
            "/autoteka/v1/specifications/by-plate-number",
            "autoteka.specification.create_by_plate_number",
            request,
        )

    def create_by_vehicle_id(self, request: VehicleIdRequest) -> AutotekaSpecificationInfo:
        return self._post_specification(
            "/autoteka/v1/specifications/by-vehicle-id",
            "autoteka.specification.create_by_vehicle_id",
            request,
        )

    def get_by_id(self, *, specification_id: int | str) -> AutotekaSpecificationInfo:
        payload = self.transport.request_json(
            "GET",
            f"/autoteka/v1/specifications/specification/{specification_id}",
            context=self._context("autoteka.specification.get_by_id"),
        )
        return map_specification(payload)

    def _post_specification(
        self,
        path: str,
        operation: str,
        request: PlateNumberRequest | VehicleIdRequest,
    ) -> AutotekaSpecificationInfo:
        payload = self.transport.request_json(
            "POST",
            path,
            context=self._context(operation, allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_specification(payload)


@dataclass(slots=True)
class TeaserClient(AutotekaBaseClient):
    """Выполняет HTTP-операции тизеров."""

    def create(self, request: TeaserCreateRequest) -> AutotekaTeaserInfo:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/teasers",
            context=self._context("autoteka.teaser.create", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_teaser(payload)

    def get(self, *, teaser_id: int | str) -> AutotekaTeaserInfo:
        payload = self.transport.request_json(
            "GET",
            f"/autoteka/v1/teasers/{teaser_id}",
            context=self._context("autoteka.teaser.get"),
        )
        return map_teaser(payload)


@dataclass(slots=True)
class ValuationClient(AutotekaBaseClient):
    """Выполняет HTTP-операции оценки стоимости."""

    def get_by_specification(
        self, request: ValuationBySpecificationRequest
    ) -> AutotekaValuationInfo:
        payload = self.transport.request_json(
            "POST",
            "/autoteka/v1/valuation/by-specification",
            context=self._context("autoteka.valuation.by_specification", allow_retry=True),
            json_body=request.to_payload(),
        )
        return map_valuation(payload)
