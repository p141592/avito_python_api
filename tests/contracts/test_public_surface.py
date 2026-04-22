from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass
from pathlib import Path

import pytest

import avito.autoteka as autoteka
import avito.jobs as jobs
import avito.orders as orders
import avito.realty as realty
from avito import (
    AuthenticationError,
    AuthorizationError,
    AvitoError,
    ConfigurationError,
    ConflictError,
    PaginatedList,
    RateLimitError,
    ResponseMappingError,
    TransportError,
    UnsupportedOperationError,
    UpstreamApiError,
    ValidationError,
)
from avito.autoteka import (
    AutotekaMonitoring,
    AutotekaReport,
    AutotekaScoring,
    AutotekaValuation,
    AutotekaVehicle,
)
from avito.jobs import Application, JobWebhook, Resume, Vacancy
from avito.messenger import ChatMedia
from avito.orders import DeliveryOrder, Order, OrderLabel, SandboxDelivery, Stock
from avito.realty import RealtyBooking, RealtyListing, RealtyPricing
from avito.testing import FakeResponse, FakeTransport

MODEL_MODULES = (
    "avito.accounts.models",
    "avito.ads.models",
    "avito.autoteka.models",
    "avito.cpa.models",
    "avito.jobs.models",
    "avito.messenger.models",
    "avito.orders.models",
    "avito.promotion.models",
    "avito.ratings.models",
    "avito.realty.models",
    "avito.tariffs.models",
)


def iter_public_dataclasses() -> list[tuple[str, str, type[object]]]:
    classes: list[tuple[str, str, type[object]]] = []
    for module_name in MODEL_MODULES:
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not inspect.isclass(value) or getattr(value, "__module__", None) != module_name:
                continue
            if not is_dataclass(value):
                continue
            classes.append((module_name, name, value))
    return classes


def test_removed_generic_request_wrappers_are_not_exported() -> None:
    assert "RealtyRequest" not in realty.__all__
    assert "JobsRequest" not in jobs.__all__
    assert "JobsQuery" not in jobs.__all__
    assert "AutotekaRequest" not in autoteka.__all__
    assert "AutotekaQuery" not in autoteka.__all__
    assert "OrdersRequest" not in orders.__all__


def test_top_level_package_exports_canonical_error_contract() -> None:
    assert AvitoError.__module__ == "avito.core.exceptions"
    assert TransportError.__module__ == "avito.core.exceptions"
    assert ValidationError.__module__ == "avito.core.exceptions"
    assert AuthenticationError.__module__ == "avito.core.exceptions"
    assert AuthorizationError.__module__ == "avito.core.exceptions"
    assert RateLimitError.__module__ == "avito.core.exceptions"
    assert ConflictError.__module__ == "avito.core.exceptions"
    assert UnsupportedOperationError.__module__ == "avito.core.exceptions"
    assert UpstreamApiError.__module__ == "avito.core.exceptions"
    assert ResponseMappingError.__module__ == "avito.core.exceptions"
    assert ConfigurationError.__module__ == "avito.core.exceptions"
    assert PaginatedList.__module__ == "avito.core.pagination"


def test_testing_package_exports_fake_transport_contract() -> None:
    assert FakeTransport.__module__ == "avito.testing.fake_transport"
    assert FakeResponse.__module__ == "httpx"


def test_public_signatures_use_typed_requests_instead_of_generic_wrappers() -> None:
    methods = (
        RealtyBooking.update_bookings_info,
        RealtyListing.get_intervals,
        RealtyPricing.update_realty_prices,
        Order.update_markings,
        Order.apply,
        Order.check_confirmation_code,
        OrderLabel.create,
        DeliveryOrder.create_announcement,
        SandboxDelivery.add_areas,
        Stock.update,
        Application.apply,
        Application.list,
        JobWebhook.update,
        Resume.list,
        Vacancy.create,
        Vacancy.update,
        AutotekaVehicle.create_preview_by_vin,
        AutotekaReport.create_report,
        AutotekaMonitoring.get_monitoring_reg_actions,
        AutotekaScoring.create_scoring_by_vehicle_id,
        AutotekaValuation.get_valuation_by_specification,
    )
    banned_tokens = (
        "RealtyRequest",
        "JobsRequest",
        "JobsQuery",
        "AutotekaRequest",
        "AutotekaQuery",
        "OrdersRequest",
    )

    for method in methods:
        public_text = str(inspect.signature(method))
        for token in banned_tokens:
            assert token not in public_text


def test_public_surface_avoids_raw_dict_signatures_and_legacy_suffixes() -> None:
    module_names = (
        "avito.accounts.domain",
        "avito.accounts.client",
        "avito.ads.domain",
        "avito.ads.client",
        "avito.autoteka.domain",
        "avito.autoteka.client",
        "avito.cpa.domain",
        "avito.cpa.client",
        "avito.jobs.domain",
        "avito.jobs.client",
        "avito.messenger.domain",
        "avito.messenger.client",
        "avito.orders.domain",
        "avito.orders.client",
        "avito.promotion.domain",
        "avito.promotion.client",
        "avito.ratings.domain",
        "avito.ratings.client",
        "avito.realty.domain",
        "avito.realty.client",
        "avito.tariffs.domain",
        "avito.tariffs.client",
    )
    banned_signature_tokens = ("Mapping[str, object]", "dict[str, object]", "object]")
    banned_name_fragments = ("legacy_",)
    banned_suffixes = ("_v1", "_v2")
    offenders: list[str] = []

    for module_name in module_names:
        module = importlib.import_module(module_name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module_name or cls.__name__.startswith("_"):
                continue
            for method_name, method in inspect.getmembers(cls, inspect.isfunction):
                if method_name.startswith("_"):
                    continue
                signature_text = str(inspect.signature(method))
                if any(token in signature_text for token in banned_signature_tokens):
                    offenders.append(f"{module_name}.{cls.__name__}.{method_name}")
                if any(fragment in method_name for fragment in banned_name_fragments):
                    offenders.append(f"{module_name}.{cls.__name__}.{method_name}")
                if method_name.endswith(banned_suffixes):
                    offenders.append(f"{module_name}.{cls.__name__}.{method_name}")

    assert offenders == []


def test_public_surface_does_not_raise_valueerror_in_domain_or_client_layers() -> None:
    root = Path(__file__).resolve().parents[2] / "avito"
    offenders: list[str] = []

    for path in root.glob("*/domain.py"):
        if "raise ValueError" in path.read_text(encoding="utf-8"):
            offenders.append(path.as_posix())
    for path in root.glob("*/client.py"):
        if "raise ValueError" in path.read_text(encoding="utf-8"):
            offenders.append(path.as_posix())

    assert offenders == []


def test_public_models_do_not_expose_raw_payload_fields() -> None:
    offenders = []
    for module_name, name, cls in iter_public_dataclasses():
        if any(field.name in {"raw_payload", "_payload"} for field in fields(cls)):
            offenders.append(f"{module_name}:{name}")

    assert offenders == []


def test_chat_media_upload_images_no_longer_accepts_raw_dict() -> None:
    signature_text = str(inspect.signature(ChatMedia.upload_images))
    assert "dict[str, object]" not in signature_text
    assert "UploadImageFile" in signature_text


def test_section_clients_are_frozen_dataclasses() -> None:
    module_names = (
        "avito.accounts.client",
        "avito.ads.client",
        "avito.autoteka.client",
        "avito.cpa.client",
        "avito.jobs.client",
        "avito.messenger.client",
        "avito.orders.client",
        "avito.promotion.client",
        "avito.ratings.client",
        "avito.realty.client",
        "avito.tariffs.client",
    )
    offenders: list[str] = []

    for module_name in module_names:
        module = importlib.import_module(module_name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module_name or cls.__name__.startswith("_"):
                continue
            if not is_dataclass(cls):
                continue
            params = getattr(cls, "__dataclass_params__", None)
            if params is None or not params.frozen:
                offenders.append(f"{module_name}.{cls.__name__}")

    assert offenders == []


def test_avito_error_is_frozen_after_initialization() -> None:
    error = AvitoError(message="Ошибка", metadata={"token": "secret"})

    with pytest.raises(FrozenInstanceError):
        error.message = "Другое сообщение"  # type: ignore[misc]
