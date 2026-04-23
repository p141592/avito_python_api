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
    CatalogResolveResult,
    MonitoringBucketResult,
    MonitoringEventsQuery,
    MonitoringEventsResult,
    ValuationBySpecificationRequest,
)
from avito.core import ValidationError
from avito.core.domain import DomainObject


@dataclass(slots=True, frozen=True)
class AutotekaVehicle(DomainObject):
    """Доменный объект превью, спецификаций, тизеров и каталога."""

    vehicle_id: int | str | None = None
    user_id: int | str | None = None

    def resolve_catalog(self, *, brand_id: int) -> CatalogResolveResult:
        """Актуализирует параметры автокаталога.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return CatalogClient(self.transport).resolve_catalog(brand_id=brand_id)

    def get_leads(self, *, limit: int) -> AutotekaLeadsResult:
        """Выполняет публичную операцию `AutotekaVehicle.get_leads` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return LeadsClient(self.transport).get_leads(limit=limit)

    def create_preview_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_vin` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PreviewClient(self.transport).create_by_vin(
            vin=vin,
            idempotency_key=idempotency_key,
        )

    def get_preview(self, *, preview_id: int | str | None = None) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.get_preview` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PreviewClient(self.transport).get_preview(
            preview_id=preview_id or self._require_vehicle_id("preview_id")
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

        return PreviewClient(self.transport).create_by_external_item(
            item_id=item_id,
            site=site,
            idempotency_key=idempotency_key,
        )

    def create_preview_by_item_id(
        self, *, item_id: int, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_item_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PreviewClient(self.transport).create_by_item_id(
            item_id=item_id,
            idempotency_key=idempotency_key,
        )

    def create_preview_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaPreviewInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_preview_by_reg_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return PreviewClient(self.transport).create_by_reg_number(
            reg_number=reg_number,
            idempotency_key=idempotency_key,
        )

    def create_specification_by_plate_number(
        self, *, plate_number: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_specification_by_plate_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecificationsClient(self.transport).create_by_plate_number(
            plate_number=plate_number,
            idempotency_key=idempotency_key,
        )

    def create_specification_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaSpecificationInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_specification_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return SpecificationsClient(self.transport).create_by_vehicle_id(
            vehicle_id=vehicle_id,
            idempotency_key=idempotency_key,
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

        return SpecificationsClient(self.transport).get_by_id(
            specification_id=specification_id or self._require_vehicle_id("specification_id")
        )

    def create_teaser(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaTeaserInfo:
        """Выполняет публичную операцию `AutotekaVehicle.create_teaser` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return TeaserClient(self.transport).create(
            vehicle_id=vehicle_id,
            idempotency_key=idempotency_key,
        )

    def get_teaser(self, *, teaser_id: int | str | None = None) -> AutotekaTeaserInfo:
        """Выполняет публичную операцию `AutotekaVehicle.get_teaser` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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
        """Выполняет публичную операцию `AutotekaReport.get_active_package` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).get_active_package()

    def create_report(
        self, *, preview_id: int, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_report` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).create_report(
            preview_id=preview_id,
            idempotency_key=idempotency_key,
        )

    def create_report_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_report_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).create_report_by_vehicle_id(
            vehicle_id=vehicle_id,
            idempotency_key=idempotency_key,
        )

    def list_reports(self) -> AutotekaReportsResult:
        """Получает список отчетов Автотеки.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).list_reports()

    def get_report(self, *, report_id: int | str | None = None) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.get_report` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).get_report(
            report_id=report_id or self._require_report_id()
        )

    def create_sync_report_by_reg_number(
        self, *, reg_number: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_sync_report_by_reg_number` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).create_sync_report_by_reg_number(
            reg_number=reg_number,
            idempotency_key=idempotency_key,
        )

    def create_sync_report_by_vin(
        self, *, vin: str, idempotency_key: str | None = None
    ) -> AutotekaReportInfo:
        """Выполняет публичную операцию `AutotekaReport.create_sync_report_by_vin` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ReportClient(self.transport).create_sync_report_by_vin(
            vin=vin,
            idempotency_key=idempotency_key,
        )

    def _require_report_id(self) -> str:
        if self.report_id is None:
            raise ValidationError("Для операции требуется `report_id`.")
        return str(self.report_id)


@dataclass(slots=True, frozen=True)
class AutotekaMonitoring(DomainObject):
    """Доменный объект мониторинга Автотеки."""

    user_id: int | str | None = None

    def create_monitoring_bucket_add(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        """Выполняет публичную операцию `AutotekaMonitoring.create_monitoring_bucket_add` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MonitoringClient(self.transport).add_bucket(
            vehicles=vehicles,
            idempotency_key=idempotency_key,
        )

    def delete_bucket(self, *, idempotency_key: str | None = None) -> MonitoringBucketResult:
        """Очищает bucket мониторинга.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MonitoringClient(self.transport).delete_bucket(idempotency_key=idempotency_key)

    def remove_bucket(
        self, *, vehicles: list[str], idempotency_key: str | None = None
    ) -> MonitoringBucketResult:
        """Удаляет автомобили из bucket мониторинга.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return MonitoringClient(self.transport).remove_bucket(
            vehicles=vehicles,
            idempotency_key=idempotency_key,
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

        return MonitoringClient(self.transport).get_reg_actions(query=query)


@dataclass(slots=True, frozen=True)
class AutotekaScoring(DomainObject):
    """Доменный объект скоринга рисков."""

    scoring_id: int | str | None = None
    user_id: int | str | None = None

    def create_scoring_by_vehicle_id(
        self, *, vehicle_id: str, idempotency_key: str | None = None
    ) -> AutotekaScoringInfo:
        """Выполняет публичную операцию `AutotekaScoring.create_scoring_by_vehicle_id` и возвращает типизированную SDK-модель.

        Параметр `idempotency_key` задает ключ идемпотентности для безопасного повтора write-операции.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

        return ScoringClient(self.transport).create_by_vehicle_id(
            vehicle_id=vehicle_id,
            idempotency_key=idempotency_key,
        )

    def get_scoring_by_id(self, *, scoring_id: int | str | None = None) -> AutotekaScoringInfo:
        """Выполняет публичную операцию `AutotekaScoring.get_scoring_by_id` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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
        """Выполняет публичную операцию `AutotekaValuation.get_valuation_by_specification` и возвращает типизированную SDK-модель.

        Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода.

        Raises: AvitoError с полями operation, status, request_id, attempt, method и endpoint.
        """

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
