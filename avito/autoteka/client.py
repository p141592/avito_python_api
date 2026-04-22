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


@dataclass(slots=True, frozen=True)
class AutotekaBaseClient:
    """Базовый клиент Автотеки с отдельным access token."""

    transport: Transport

    def _context(self, operation_name: str, *, allow_retry: bool = False) -> RequestContext:
        auth_provider = self.transport.auth_provider
        headers: dict[str, str] = {}
        if auth_provider is not None:
            headers["Authorization"] = f"Bearer {auth_provider.get_autoteka_access_token()}"
        return RequestContext(
            operation_name,
            allow_retry=allow_retry,
            requires_auth=False,
            headers=headers,
        )


@dataclass(slots=True, frozen=True)
class CatalogClient(AutotekaBaseClient):
    """Выполняет HTTP-операции автокаталога."""

    def resolve_catalog(self, *, brand_id: int) -> CatalogResolveResult:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/catalogs/resolve",
            context=self._context("autoteka.catalog.resolve", allow_retry=True),
            mapper=map_catalogs_resolve,
            json_body=CatalogResolveRequest(brand_id=brand_id).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class LeadsClient(AutotekaBaseClient):
    """Выполняет HTTP-операции сервиса Сигнал."""

    def get_leads(self, *, limit: int) -> AutotekaLeadsResult:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/get-leads/",
            context=self._context("autoteka.leads.get", allow_retry=True),
            mapper=map_leads,
            json_body=LeadsRequest(limit=limit).to_payload(),
        )


@dataclass(slots=True, frozen=True)
class PreviewClient(AutotekaBaseClient):
    """Выполняет HTTP-операции превью автомобиля."""

    def create_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/previews",
            "autoteka.preview.create_by_vin",
            VinRequest(vin=vin),
            idempotency_key=idempotency_key,
        )

    def create_by_external_item(
        self,
        *,
        item_id: str,
        site: str,
        idempotency_key: str | None = None,
    ) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-external-item",
            "autoteka.preview.create_by_external_item",
            ExternalItemPreviewRequest(item_id=item_id, site=site),
            idempotency_key=idempotency_key,
        )

    def create_by_item_id(
        self, *, item_id: int, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-item-id",
            "autoteka.preview.create_by_item_id",
            ItemIdRequest(item_id=item_id),
            idempotency_key=idempotency_key,
        )

    def create_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        return self._post_preview(
            "/autoteka/v1/request-preview-by-regnumber",
            "autoteka.preview.create_by_reg_number",
            RegNumberRequest(reg_number=reg_number),
            idempotency_key=idempotency_key,
        )

    def get_preview(self, *, preview_id: int | str) -> AutotekaPreviewInfo:
        return self.transport.request_public_model(
            "GET",
            f"/autoteka/v1/previews/{preview_id}",
            context=self._context("autoteka.preview.get"),
            mapper=map_preview,
        )

    def _post_preview(
        self,
        path: str,
        operation: str,
        request: VinRequest | ExternalItemPreviewRequest | ItemIdRequest | RegNumberRequest,
        idempotency_key: str | None = None,
    ) -> AutotekaPreviewInfo:
        return self.transport.request_public_model(
            "POST",
            path,
            context=self._context(operation, allow_retry=idempotency_key is not None),
            mapper=map_preview,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class ReportClient(AutotekaBaseClient):
    """Выполняет HTTP-операции отчетов Автотеки."""

    def get_active_package(self) -> AutotekaPackageInfo:
        return self.transport.request_public_model(
            "GET",
            "/autoteka/v1/packages/active_package",
            context=self._context("autoteka.report.get_active_package"),
            mapper=map_package,
        )

    def create_report(
        self, *, preview_id: int, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/reports",
            "autoteka.report.create",
            PreviewReportRequest(preview_id=preview_id),
            idempotency_key=idempotency_key,
        )

    def create_report_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/reports-by-vehicle-id",
            "autoteka.report.create_by_vehicle_id",
            VehicleIdRequest(vehicle_id=vehicle_id),
            idempotency_key=idempotency_key,
        )

    def list_reports(self) -> AutotekaReportsResult:
        return self.transport.request_public_model(
            "GET",
            "/autoteka/v1/reports/list/",
            context=self._context("autoteka.report.list"),
            mapper=map_reports,
        )

    def get_report(self, *, report_id: int | str) -> AutotekaReportInfo:
        return self.transport.request_public_model(
            "GET",
            f"/autoteka/v1/reports/{report_id}",
            context=self._context("autoteka.report.get"),
            mapper=map_report,
        )

    def create_sync_report_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/sync/create-by-regnumber",
            "autoteka.report.create_sync_by_reg_number",
            RegNumberRequest(reg_number=reg_number),
            idempotency_key=idempotency_key,
        )

    def create_sync_report_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        return self._post_report(
            "/autoteka/v1/sync/create-by-vin",
            "autoteka.report.create_sync_by_vin",
            VinRequest(vin=vin),
            idempotency_key=idempotency_key,
        )

    def _post_report(
        self,
        path: str,
        operation: str,
        request: PreviewReportRequest | VehicleIdRequest | RegNumberRequest | VinRequest,
        idempotency_key: str | None = None,
    ) -> AutotekaReportInfo:
        return self.transport.request_public_model(
            "POST",
            path,
            context=self._context(operation, allow_retry=idempotency_key is not None),
            mapper=map_report,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class MonitoringClient(AutotekaBaseClient):
    """Выполняет HTTP-операции мониторинга."""

    def add_bucket(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        return self._post_bucket(
            "/autoteka/v1/monitoring/bucket/add",
            "autoteka.monitoring.bucket_add",
            MonitoringBucketRequest(vehicles=vehicles),
            idempotency_key=idempotency_key,
        )

    def delete_bucket(self, *, idempotency_key: str | None = None) -> MonitoringBucketResult:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/monitoring/bucket/delete",
            context=self._context(
                "autoteka.monitoring.bucket_delete",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_monitoring_bucket,
            idempotency_key=idempotency_key,
        )

    def remove_bucket(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        return self._post_bucket(
            "/autoteka/v1/monitoring/bucket/remove",
            "autoteka.monitoring.bucket_remove",
            MonitoringBucketRequest(vehicles=vehicles),
            idempotency_key=idempotency_key,
        )

    def get_reg_actions(
        self, *, query: MonitoringEventsQuery | None = None
    ) -> MonitoringEventsResult:
        return self.transport.request_public_model(
            "GET",
            "/autoteka/v1/monitoring/get-reg-actions/",
            context=self._context("autoteka.monitoring.get_reg_actions"),
            mapper=map_monitoring_events,
            params=query.to_params() if query is not None else None,
        )

    def _post_bucket(
        self,
        path: str,
        operation: str,
        request: MonitoringBucketRequest,
        idempotency_key: str | None = None,
    ) -> MonitoringBucketResult:
        return self.transport.request_public_model(
            "POST",
            path,
            context=self._context(operation, allow_retry=idempotency_key is not None),
            mapper=map_monitoring_bucket,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class ScoringClient(AutotekaBaseClient):
    """Выполняет HTTP-операции скоринга рисков."""

    def create_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaScoringInfo:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/scoring/by-vehicle-id",
            context=self._context(
                "autoteka.scoring.create_by_vehicle_id",
                allow_retry=idempotency_key is not None,
            ),
            mapper=map_scoring,
            json_body=VehicleIdRequest(vehicle_id=vehicle_id).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get_by_id(self, *, scoring_id: int | str) -> AutotekaScoringInfo:
        return self.transport.request_public_model(
            "GET",
            f"/autoteka/v1/scoring/{scoring_id}",
            context=self._context("autoteka.scoring.get_by_id"),
            mapper=map_scoring,
        )


@dataclass(slots=True, frozen=True)
class SpecificationsClient(AutotekaBaseClient):
    """Выполняет HTTP-операции спецификаций автомобиля."""

    def create_by_plate_number(
        self, *, plate_number: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        return self._post_specification(
            "/autoteka/v1/specifications/by-plate-number",
            "autoteka.specification.create_by_plate_number",
            PlateNumberRequest(plate_number=plate_number),
            idempotency_key=idempotency_key,
        )

    def create_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        return self._post_specification(
            "/autoteka/v1/specifications/by-vehicle-id",
            "autoteka.specification.create_by_vehicle_id",
            VehicleIdRequest(vehicle_id=vehicle_id),
            idempotency_key=idempotency_key,
        )

    def get_by_id(self, *, specification_id: int | str) -> AutotekaSpecificationInfo:
        return self.transport.request_public_model(
            "GET",
            f"/autoteka/v1/specifications/specification/{specification_id}",
            context=self._context("autoteka.specification.get_by_id"),
            mapper=map_specification,
        )

    def _post_specification(
        self,
        path: str,
        operation: str,
        request: PlateNumberRequest | VehicleIdRequest,
        idempotency_key: str | None = None,
    ) -> AutotekaSpecificationInfo:
        return self.transport.request_public_model(
            "POST",
            path,
            context=self._context(operation, allow_retry=idempotency_key is not None),
            mapper=map_specification,
            json_body=request.to_payload(),
            idempotency_key=idempotency_key,
        )


@dataclass(slots=True, frozen=True)
class TeaserClient(AutotekaBaseClient):
    """Выполняет HTTP-операции тизеров."""

    def create(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaTeaserInfo:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/teasers",
            context=self._context("autoteka.teaser.create", allow_retry=idempotency_key is not None),
            mapper=map_teaser,
            json_body=TeaserCreateRequest(vehicle_id=vehicle_id).to_payload(),
            idempotency_key=idempotency_key,
        )

    def get(self, *, teaser_id: int | str) -> AutotekaTeaserInfo:
        return self.transport.request_public_model(
            "GET",
            f"/autoteka/v1/teasers/{teaser_id}",
            context=self._context("autoteka.teaser.get"),
            mapper=map_teaser,
        )


@dataclass(slots=True, frozen=True)
class ValuationClient(AutotekaBaseClient):
    """Выполняет HTTP-операции оценки стоимости."""

    def get_by_specification(
        self, request: ValuationBySpecificationRequest
    ) -> AutotekaValuationInfo:
        return self.transport.request_public_model(
            "POST",
            "/autoteka/v1/valuation/by-specification",
            context=self._context("autoteka.valuation.by_specification", allow_retry=True),
            mapper=map_valuation,
            json_body=request.to_payload(),
        )
