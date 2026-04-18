from __future__ import annotations

import inspect

import avito.orders as orders
import avito.autoteka as autoteka
import avito.jobs as jobs
import avito.messenger as messenger
import avito.realty as realty
from avito.autoteka import AutotekaMonitoring, AutotekaReport, AutotekaScoring, AutotekaValuation, AutotekaVehicle
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
