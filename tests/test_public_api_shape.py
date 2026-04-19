from __future__ import annotations

import importlib
import inspect

import avito.autoteka as autoteka
import avito.jobs as jobs
import avito.orders as orders
import avito.realty as realty
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


def test_removed_generic_request_wrappers_are_not_exported() -> None:
    assert "RealtyRequest" not in realty.__all__
    assert "JobsRequest" not in jobs.__all__
    assert "JobsQuery" not in jobs.__all__
    assert "AutotekaRequest" not in autoteka.__all__
    assert "AutotekaQuery" not in autoteka.__all__
    assert "OrdersRequest" not in orders.__all__


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


def test_chat_media_upload_images_no_longer_accepts_raw_dict() -> None:
    signature_text = str(inspect.signature(ChatMedia.upload_images))
    assert "dict[str, object]" not in signature_text
    assert "UploadImageFile" in signature_text


def test_public_domain_and_client_methods_avoid_raw_dict_mapping_object_signatures() -> None:
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
    banned_tokens = ("Mapping[str, object]", "dict[str, object]", "object]")
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
                if any(token in signature_text for token in banned_tokens):
                    offenders.append(f"{module_name}.{cls.__name__}.{method_name}{signature_text}")

    assert offenders == []


def test_public_surface_does_not_expose_legacy_or_version_suffixed_method_names() -> None:
    module_names = (
        "avito.client.client",
        "avito.auth.provider",
        "avito.ads.domain",
        "avito.autoteka.client",
        "avito.autoteka.domain",
        "avito.cpa.domain",
        "avito.cpa.client",
        "avito.jobs.domain",
        "avito.jobs.client",
        "avito.orders.domain",
        "avito.orders.client",
        "avito.ratings.domain",
        "avito.realty.domain",
    )
    banned_fragments = ("legacy_",)
    banned_suffixes = ("_v1", "_v2")
    banned_prefixes = ("get_catalogs_", "list_report_", "list_monitoring_", "delete_monitoring_")
    offenders: list[str] = []

    for module_name in module_names:
        module = importlib.import_module(module_name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module_name or cls.__name__.startswith("_"):
                continue
            for method_name, method in inspect.getmembers(cls, inspect.isfunction):
                if method_name.startswith("_"):
                    continue
                if (
                    any(fragment in method_name for fragment in banned_fragments)
                    or method_name.endswith(banned_suffixes)
                    or method_name.startswith(banned_prefixes)
                ):
                    offenders.append(f"{module_name}.{cls.__name__}.{method_name}{inspect.signature(method)}")

    assert offenders == []
