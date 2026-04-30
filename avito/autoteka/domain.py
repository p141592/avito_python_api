"""Доменные объекты пакета autoteka."""

from __future__ import annotations

from dataclasses import dataclass

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
from avito.autoteka.operations import (
    ADD_MONITORING_BUCKET,
    CATALOG_RESOLVE,
    CREATE_PREVIEW_BY_EXTERNAL_ITEM,
    CREATE_PREVIEW_BY_ITEM_ID,
    CREATE_PREVIEW_BY_REG_NUMBER,
    CREATE_PREVIEW_BY_VIN,
    CREATE_REPORT,
    CREATE_REPORT_BY_VEHICLE_ID,
    CREATE_SCORING_BY_VEHICLE_ID,
    CREATE_SPECIFICATION_BY_PLATE_NUMBER,
    CREATE_SPECIFICATION_BY_VEHICLE_ID,
    CREATE_SYNC_REPORT_BY_REG_NUMBER,
    CREATE_SYNC_REPORT_BY_VIN,
    CREATE_TEASER,
    DELETE_MONITORING_BUCKET,
    GET_ACTIVE_PACKAGE,
    GET_LEADS,
    GET_MONITORING_REG_ACTIONS,
    GET_PREVIEW,
    GET_REPORT,
    GET_SCORING_BY_ID,
    GET_SPECIFICATION_BY_ID,
    GET_TEASER,
    GET_VALUATION_BY_SPECIFICATION,
    LIST_REPORTS,
    REMOVE_MONITORING_BUCKET,
)
from avito.core import ValidationError
from avito.core.domain import DomainObject
from avito.core.swagger import swagger_operation
from avito.core.transport import Transport


def _autoteka_headers(transport: Transport) -> dict[str, str]:
    auth_provider = transport.auth_provider
    if auth_provider is None:
        return {}
    return {"Authorization": f"Bearer {auth_provider.get_autoteka_access_token()}"}


@dataclass(slots=True, frozen=True)
class AutotekaVehicle(DomainObject):
    """Доменный объект превью, спецификаций, тизеров и каталога."""

    __swagger_domain__ = "autoteka"
    __sdk_factory__ = "autoteka_vehicle"
    __sdk_factory_args__ = {"vehicle_id": "path.vehicle_id"}

    vehicle_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/autoteka/v1/catalogs/resolve",
        spec="Автотека.json",
        operation_id="catalogsResolve",
        method_args={"brand_id": "body.fields_value_ids"},
    )
    def resolve_catalog(self, *, brand_id: int) -> CatalogResolveResult:
        """Актуализирует параметры автокаталога.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CATALOG_RESOLVE,
            request=CatalogResolveRequest(brand_id=brand_id),
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/get-leads",
        spec="Автотека.json",
        operation_id="getLeads",
        method_args={"limit": "body.limit"},
    )
    def get_leads(self, *, limit: int) -> AutotekaLeadsResult:
        """Выполняет публичную операцию `AutotekaVehicle.get_leads` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_LEADS,
            request=LeadsRequest(limit=limit),
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/previews",
        spec="Автотека.json",
        operation_id="postPreviewByVin",
        method_args={"vin": "body.vin"},
    )
    def create_preview_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_vin` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_PREVIEW_BY_VIN,
            request=VinRequest(vin=vin),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/previews/{previewId}",
        spec="Автотека.json",
        operation_id="getPreview",
    )
    def get_preview(self, *, preview_id: int | str | None = None) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.get_preview` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_PREVIEW,
            path_params={"previewId": preview_id or self._require_vehicle_id("preview_id")},
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/request-preview-by-external-item",
        spec="Автотека.json",
        operation_id="postPreviewByExternalItem",
        method_args={"item_id": "body.item_id", "site": "body.site"},
    )
    def create_preview_by_external_item(
        self,
        *,
        item_id: str,
        site: str,
        idempotency_key: str | None = None,
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_external_item` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_PREVIEW_BY_EXTERNAL_ITEM,
            request=ExternalItemPreviewRequest(item_id=item_id, site=site),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/request-preview-by-item-id",
        spec="Автотека.json",
        operation_id="postPreviewByItemId",
        method_args={"item_id": "body.item_id"},
    )
    def create_preview_by_item_id(
        self, *, item_id: int, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_item_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_PREVIEW_BY_ITEM_ID,
            request=ItemIdRequest(item_id=item_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/request-preview-by-regnumber",
        spec="Автотека.json",
        operation_id="postPreviewByRegNumber",
        method_args={"reg_number": "body.reg_number"},
    )
    def create_preview_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_reg_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_PREVIEW_BY_REG_NUMBER,
            request=RegNumberRequest(reg_number=reg_number),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/specifications/by-plate-number",
        spec="Автотека.json",
        operation_id="specificationByPlateNumber",
        method_args={"plate_number": "body.plate_number"},
    )
    def create_specification_by_plate_number(
        self, *, plate_number: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_specification_by_plate_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_SPECIFICATION_BY_PLATE_NUMBER,
            request=PlateNumberRequest(plate_number=plate_number),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/specifications/by-vehicle-id",
        spec="Автотека.json",
        operation_id="specificationByVehicleId",
        method_args={"vehicle_id": "body.vehicle_id"},
    )
    def create_specification_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_specification_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_SPECIFICATION_BY_VEHICLE_ID,
            request=VehicleIdRequest(vehicle_id=vehicle_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/specifications/specification/{specificationID}",
        spec="Автотека.json",
        operation_id="specificationGetById",
    )
    def get_specification_by_id(
        self,
        *,
        specification_id: int | str | None = None,
    ) -> AutotekaSpecificationInfo:
        """Выполняет публичную операцию `AutotekaVehicle.get_specification_by_id` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_SPECIFICATION_BY_ID,
            path_params={
                "specificationID": specification_id
                or self._require_vehicle_id("specification_id")
            },
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/teasers",
        spec="Автотека.json",
        operation_id="postTeaser",
        method_args={"vehicle_id": "body.vehicle_id"},
    )
    def create_teaser(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaTeaserInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_teaser` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_TEASER,
            request=TeaserCreateRequest(vehicle_id=vehicle_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/teasers/{teaser_id}",
        spec="Автотека.json",
        operation_id="getTeaser",
    )
    def get_teaser(self, *, teaser_id: int | str | None = None) -> AutotekaTeaserInfo:
        """Выполняет публичную операцию `AutotekaVehicle.get_teaser` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_TEASER,
            path_params={"teaser_id": teaser_id or self._require_vehicle_id("teaser_id")},
            headers=_autoteka_headers(self.transport),
        )

    def _require_vehicle_id(self, field_name: str) -> str:
        if self.vehicle_id is None:
            raise ValidationError(f"Для операции требуется `{field_name}`.")
        return str(self.vehicle_id)


@dataclass(slots=True, frozen=True)
class AutotekaReport(DomainObject):
    """Доменный объект отчетов и пакетов Автотеки."""

    __swagger_domain__ = "autoteka"
    __sdk_factory__ = "autoteka_report"
    __sdk_factory_args__ = {"report_id": "path.report_id"}

    report_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "GET",
        "/autoteka/v1/packages/active_package",
        spec="Автотека.json",
        operation_id="getActivePackage",
    )
    def get_active_package(self) -> AutotekaPackageInfo:
        """Выполняет публичную операцию `AutotekaReport.get_active_package` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_ACTIVE_PACKAGE,
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/reports",
        spec="Автотека.json",
        operation_id="postReport",
        method_args={"preview_id": "body.preview_id"},
    )
    def create_report(
        self, *, preview_id: int, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_report` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_REPORT,
            request=PreviewReportRequest(preview_id=preview_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/reports-by-vehicle-id",
        spec="Автотека.json",
        operation_id="postReportByVehicleId",
        method_args={"vehicle_id": "body.vehicle_id"},
    )
    def create_report_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_report_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_REPORT_BY_VEHICLE_ID,
            request=VehicleIdRequest(vehicle_id=vehicle_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/reports/list",
        spec="Автотека.json",
        operation_id="getReportList",
    )
    def list_reports(self) -> AutotekaReportsResult:
        """Получает список отчетов Автотеки.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            LIST_REPORTS,
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/reports/{report_id}",
        spec="Автотека.json",
        operation_id="getReport",
    )
    def get_report(self, *, report_id: int | str | None = None) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.get_report` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_REPORT,
            path_params={"report_id": report_id or self._require_report_id()},
            headers=_autoteka_headers(self.transport),
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/sync/create-by-regnumber",
        spec="Автотека.json",
        operation_id="postSyncCreateReportByRegNumber",
        method_args={"reg_number": "body.reg_number"},
    )
    def create_sync_report_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_sync_report_by_reg_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_SYNC_REPORT_BY_REG_NUMBER,
            request=RegNumberRequest(reg_number=reg_number),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/sync/create-by-vin",
        spec="Автотека.json",
        operation_id="postSyncCreateReportByVin",
        method_args={"vin": "body.vin"},
    )
    def create_sync_report_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_sync_report_by_vin` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_SYNC_REPORT_BY_VIN,
            request=VinRequest(vin=vin),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    def _require_report_id(self) -> str:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return str(self.report_id)


@dataclass(slots=True, frozen=True)
class AutotekaMonitoring(DomainObject):
    """Доменный объект мониторинга Автотеки."""

    __swagger_domain__ = "autoteka"
    __sdk_factory__ = "autoteka_monitoring"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/autoteka/v1/monitoring/bucket/add",
        spec="Автотека.json",
        operation_id="monitoringBucketAdd",
        method_args={"vehicles": "body.data"},
    )
    def create_monitoring_bucket_add(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        """Выполняет публичную операцию `AutotekaMonitoring.create_monitoring_bucket_add` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            ADD_MONITORING_BUCKET,
            request=MonitoringBucketRequest(vehicles=vehicles),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/monitoring/bucket/delete",
        spec="Автотека.json",
        operation_id="monitoringBucketDelete",
    )
    def delete_bucket(self, *, idempotency_key: str | None = None) -> MonitoringBucketResult:
        """Очищает bucket мониторинга.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            DELETE_MONITORING_BUCKET,
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "POST",
        "/autoteka/v1/monitoring/bucket/remove",
        spec="Автотека.json",
        operation_id="monitoringBucketRemove",
        method_args={"vehicles": "body.data"},
    )
    def remove_bucket(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        """Удаляет автомобили из bucket мониторинга.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            REMOVE_MONITORING_BUCKET,
            request=MonitoringBucketRequest(vehicles=vehicles),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/monitoring/get-reg-actions",
        spec="Автотека.json",
        operation_id="monitoringGetRegActions",
    )
    def get_monitoring_reg_actions(
        self,
        *,
        query: MonitoringEventsQuery | None = None,
    ) -> MonitoringEventsResult:
        """Выполняет публичную операцию `AutotekaMonitoring.get_monitoring_reg_actions` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_MONITORING_REG_ACTIONS,
            query=query,
            headers=_autoteka_headers(self.transport),
        )


@dataclass(slots=True, frozen=True)
class AutotekaScoring(DomainObject):
    """Доменный объект скоринга рисков."""

    __swagger_domain__ = "autoteka"
    __sdk_factory__ = "autoteka_scoring"
    __sdk_factory_args__ = {"scoring_id": "path.scoring_id"}

    scoring_id: int | str | None = None
    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/autoteka/v1/scoring/by-vehicle-id",
        spec="Автотека.json",
        operation_id="scoringByVehicleId",
        method_args={"vehicle_id": "body.vehicle_id"},
    )
    def create_scoring_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaScoringInfo:
        """Выполняет публичную операцию `AutotekaScoring.create_scoring_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            CREATE_SCORING_BY_VEHICLE_ID,
            request=VehicleIdRequest(vehicle_id=vehicle_id),
            headers=_autoteka_headers(self.transport),
            idempotency_key=idempotency_key,
        )

    @swagger_operation(
        "GET",
        "/autoteka/v1/scoring/{scoring_id}",
        spec="Автотека.json",
        operation_id="scoringGetById",
    )
    def get_scoring_by_id(self, *, scoring_id: int | str | None = None) -> AutotekaScoringInfo:
        """Выполняет публичную операцию `AutotekaScoring.get_scoring_by_id` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_SCORING_BY_ID,
            path_params={"scoring_id": scoring_id or self._require_scoring_id()},
            headers=_autoteka_headers(self.transport),
        )

    def _require_scoring_id(self) -> str:
        if self.scoring_id is None:
            raise ValidationError("Для операции требуется `scoring_id`.")
        return str(self.scoring_id)


@dataclass(slots=True, frozen=True)
class AutotekaValuation(DomainObject):
    """Доменный объект оценки автомобиля."""

    __swagger_domain__ = "autoteka"
    __sdk_factory__ = "autoteka_valuation"

    user_id: int | str | None = None

    @swagger_operation(
        "POST",
        "/autoteka/v1/valuation/by-specification",
        spec="Автотека.json",
        operation_id="valuationBySpecification",
        method_args={"specification_id": "body.specification", "mileage": "body.mileage"},
    )
    def get_valuation_by_specification(
        self, *, specification_id: int, mileage: int
    ) -> AutotekaValuationInfo:
        """Выполняет публичную операцию `AutotekaValuation.get_valuation_by_specification` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return self._execute(
            GET_VALUATION_BY_SPECIFICATION,
            request=ValuationBySpecificationRequest(
                specification_id=specification_id,
                mileage=mileage,
            ),
            headers=_autoteka_headers(self.transport),
        )


__all__ = (
    "AutotekaMonitoring",
    "AutotekaReport",
    "AutotekaScoring",
    "AutotekaValuation",
    "AutotekaVehicle",
)
