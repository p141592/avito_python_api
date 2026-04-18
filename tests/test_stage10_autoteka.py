from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.autoteka import (
    AutotekaMonitoring,
    AutotekaReport,
    AutotekaScoring,
    AutotekaValuation,
    AutotekaVehicle,
)
from avito.autoteka.models import (
    CatalogResolveRequest,
    ExternalItemPreviewRequest,
    ItemIdRequest,
    LeadsRequest,
    MonitoringBucketRequest,
    MonitoringEventsQuery,
    PlateNumberRequest,
    PreviewReportRequest,
    RegNumberRequest,
    TeaserCreateRequest,
    ValuationBySpecificationRequest,
    VehicleIdRequest,
    VinRequest,
)
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(),
        retry_policy=RetryPolicy(),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )


def test_autoteka_vehicle_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/autoteka/v1/catalogs/resolve":
            assert payload == {"brandId": 1}
            return httpx.Response(
                200,
                json={
                    "result": {
                        "fields": [
                            {
                                "id": 110000,
                                "label": "Марка",
                                "dataType": "integer",
                                "values": [{"valueId": 1, "label": "Audi"}],
                            }
                        ]
                    }
                },
            )
        if path == "/autoteka/v1/get-leads/":
            assert payload == {"limit": 1}
            return httpx.Response(
                200,
                json={
                    "pagination": {"lastId": 321},
                    "result": [
                        {
                            "id": 12,
                            "subscriptionId": 44,
                            "payload": {
                                "vin": "VIN-1",
                                "itemId": 901,
                                "brand": "Audi",
                                "model": "A4",
                                "price": 1500000,
                                "itemCreatedAt": "2026-04-18 10:00",
                                "url": "https://avito.ru/item/901",
                            },
                        }
                    ],
                },
            )
        if path == "/autoteka/v1/previews":
            assert payload == {"vin": "VIN-1"}
            return httpx.Response(200, json={"result": {"preview": {"previewId": 77}}})
        if path == "/autoteka/v1/request-preview-by-item-id":
            assert payload == {"itemId": 901}
            return httpx.Response(200, json={"result": {"preview": {"previewId": 78}}})
        if path == "/autoteka/v1/request-preview-by-regnumber":
            assert payload == {"regNumber": "A123AA77"}
            return httpx.Response(200, json={"result": {"preview": {"previewId": 79}}})
        if path == "/autoteka/v1/request-preview-by-external-item":
            assert payload == {"itemId": "ext-1", "site": "cars.example"}
            return httpx.Response(200, json={"result": {"preview": {"previewId": 80}}})
        if path == "/autoteka/v1/previews/77":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "preview": {
                            "previewId": 77,
                            "status": "success",
                            "vin": "VIN-1",
                            "regNumber": "A123AA77",
                        }
                    }
                },
            )
        if path == "/autoteka/v1/specifications/by-plate-number":
            assert payload == {"plateNumber": "A123AA77"}
            return httpx.Response(200, json={"result": {"specification": {"specificationId": 501}}})
        if path == "/autoteka/v1/specifications/by-vehicle-id":
            assert payload == {"vehicleId": "VIN-1"}
            return httpx.Response(200, json={"result": {"specification": {"specificationId": 502}}})
        if path == "/autoteka/v1/specifications/specification/501":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "specification": {
                            "specificationId": 501,
                            "status": "success",
                            "vehicleId": "VIN-1",
                            "plateNumber": "A123AA77",
                        }
                    }
                },
            )
        if path == "/autoteka/v1/teasers":
            assert payload == {"vehicleId": "VIN-1"}
            return httpx.Response(
                200, json={"result": {"teaser": {"teaserId": 601, "status": "processing"}}}
            )
        assert path == "/autoteka/v1/teasers/601"
        return httpx.Response(
            200,
            json={
                "teaserId": 601,
                "status": "success",
                "data": {"brand": "Audi", "model": "A4", "year": 2018},
            },
        )

    vehicle = AutotekaVehicle(make_transport(httpx.MockTransport(handler)), resource_id="77")

    catalog = vehicle.get_catalogs_resolve(request=CatalogResolveRequest(brand_id=1))
    leads = vehicle.get_leads(request=LeadsRequest(limit=1))
    preview_vin = vehicle.create_preview_by_vin(request=VinRequest(vin="VIN-1"))
    preview_item = vehicle.create_preview_by_item_id(request=ItemIdRequest(item_id=901))
    preview_reg = vehicle.create_preview_by_reg_number(
        request=RegNumberRequest(reg_number="A123AA77")
    )
    preview_external = vehicle.create_preview_by_external_item(
        request=ExternalItemPreviewRequest(item_id="ext-1", site="cars.example")
    )
    preview = vehicle.get_preview()
    specification_plate = vehicle.create_specification_by_plate_number(
        request=PlateNumberRequest(plate_number="A123AA77")
    )
    specification_vehicle = vehicle.create_specification_by_vehicle_id(
        request=VehicleIdRequest(vehicle_id="VIN-1")
    )
    specification = vehicle.get_specification_by_id(specification_id="501")
    teaser_create = vehicle.create_teaser(request=TeaserCreateRequest(vehicle_id="VIN-1"))
    teaser = vehicle.get_teaser(teaser_id="601")

    assert catalog.items[0].values[0].label == "Audi"
    assert leads.last_id == 321
    assert leads.items[0].brand == "Audi"
    assert preview_vin.preview_id == "77"
    assert preview_item.preview_id == "78"
    assert preview_reg.preview_id == "79"
    assert preview_external.preview_id == "80"
    assert preview.vehicle_id == "VIN-1"
    assert specification_plate.specification_id == "501"
    assert specification_vehicle.specification_id == "502"
    assert specification.status == "success"
    assert teaser_create.teaser_id == "601"
    assert teaser.brand == "Audi"


def test_autoteka_report_monitoring_scoring_and_valuation_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/autoteka/v1/packages/active_package":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "package": {
                            "createdTime": "2026-04-01",
                            "expireTime": "2026-05-01",
                            "reportsCnt": 100,
                            "reportsCntRemain": 77,
                        }
                    }
                },
            )
        if path == "/autoteka/v1/reports":
            assert payload == {"previewId": 77}
            return httpx.Response(
                200, json={"result": {"report": {"reportId": 701, "status": "processing"}}}
            )
        if path == "/autoteka/v1/reports-by-vehicle-id":
            assert payload == {"vehicleId": "VIN-1"}
            return httpx.Response(
                200, json={"result": {"report": {"reportId": 702, "status": "processing"}}}
            )
        if path == "/autoteka/v1/reports/list/":
            return httpx.Response(
                200,
                json={
                    "result": [
                        {"reportId": 701, "vin": "VIN-1", "createdAt": "2026-04-18 12:00:00"}
                    ]
                },
            )
        if path == "/autoteka/v1/reports/701":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "report": {
                            "reportId": 701,
                            "status": "success",
                            "webLink": "https://autoteka/web/701",
                            "pdfLink": "https://autoteka/pdf/701",
                            "data": {"vin": "VIN-1"},
                        }
                    }
                },
            )
        if path == "/autoteka/v1/sync/create-by-regnumber":
            assert payload == {"regNumber": "A123AA77"}
            return httpx.Response(
                200,
                json={
                    "result": {
                        "report": {"reportId": 703, "status": "success", "data": {"vin": "VIN-1"}}
                    }
                },
            )
        if path == "/autoteka/v1/sync/create-by-vin":
            assert payload == {"vin": "VIN-1"}
            return httpx.Response(
                200,
                json={
                    "result": {
                        "report": {"reportId": 704, "status": "success", "data": {"vin": "VIN-1"}}
                    }
                },
            )
        if path == "/autoteka/v1/monitoring/bucket/add":
            assert payload == {"vehicles": ["VIN-1", "bad-vin"]}
            return httpx.Response(
                200,
                json={
                    "result": {
                        "isOk": True,
                        "invalidVehicles": [{"vehicleID": "bad-vin", "description": "invalid"}],
                    }
                },
            )
        if path == "/autoteka/v1/monitoring/bucket/delete":
            return httpx.Response(200, json={"result": {"isOk": True}})
        if path == "/autoteka/v1/monitoring/bucket/remove":
            assert payload == {"vehicles": ["VIN-1"]}
            return httpx.Response(200, json={"result": {"isOk": True, "invalidVehicles": []}})
        if path == "/autoteka/v1/monitoring/get-reg-actions/":
            assert request.url.params["limit"] == "10"
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "vin": "VIN-1",
                            "brand": "Audi",
                            "model": "A4",
                            "year": 2018,
                            "operationCode": 11,
                            "operationDateFrom": "2026-04-01T00:00:00+03:00",
                        }
                    ],
                    "pagination": {
                        "hasNext": True,
                        "nextCursor": "cursor-2",
                        "nextLink": "https://api.avito.ru/next",
                    },
                },
            )
        if path == "/autoteka/v1/scoring/by-vehicle-id":
            assert payload == {"vehicleId": "VIN-1"}
            return httpx.Response(200, json={"result": {"scoring": {"scoringId": 801}}})
        if path == "/autoteka/v1/scoring/801":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "risksAssessment": {
                            "scoringId": 801,
                            "isCompleted": True,
                            "createdAt": 1713427200,
                        }
                    }
                },
            )
        assert path == "/autoteka/v1/valuation/by-specification"
        assert payload == {"specificationId": 501, "mileage": 30000}
        return httpx.Response(
            200,
            json={
                "result": {
                    "status": "success",
                    "vehicleId": "VIN-1",
                    "brand": "Audi",
                    "model": "A4",
                    "year": 2018,
                    "ownersCount": "2",
                    "mileage": 30000,
                    "valuation": {"avgPriceWithCondition": 2100000, "avgMarketPrice": 2200000},
                }
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    report = AutotekaReport(transport, resource_id="701")
    monitoring = AutotekaMonitoring(transport)
    scoring = AutotekaScoring(transport, resource_id="801")
    valuation = AutotekaValuation(transport)

    package = report.get_active_package()
    created = report.create_report(request=PreviewReportRequest(preview_id=77))
    created_by_vehicle = report.create_report_by_vehicle_id(
        request=VehicleIdRequest(vehicle_id="VIN-1")
    )
    reports = report.list_report_list()
    fetched = report.get_report()
    sync_reg = report.create_sync_report_by_reg_number(
        request=RegNumberRequest(reg_number="A123AA77")
    )
    sync_vin = report.create_sync_report_by_vin(request=VinRequest(vin="VIN-1"))
    added = monitoring.create_monitoring_bucket_add(
        request=MonitoringBucketRequest(vehicles=["VIN-1", "bad-vin"])
    )
    deleted = monitoring.list_monitoring_bucket_delete()
    removed = monitoring.delete_monitoring_bucket_remove(
        request=MonitoringBucketRequest(vehicles=["VIN-1"])
    )
    events = monitoring.get_monitoring_reg_actions(query=MonitoringEventsQuery(limit=10))
    scoring_created = scoring.create_scoring_by_vehicle_id(
        request=VehicleIdRequest(vehicle_id="VIN-1")
    )
    scoring_item = scoring.get_scoring_by_id()
    valuation_item = valuation.get_valuation_by_specification(
        request=ValuationBySpecificationRequest(specification_id=501, mileage=30000)
    )

    assert package.reports_remaining == 77
    assert created.report_id == "701"
    assert created_by_vehicle.report_id == "702"
    assert reports.items[0].vehicle_id == "VIN-1"
    assert fetched.web_link == "https://autoteka/web/701"
    assert sync_reg.status == "success"
    assert sync_vin.report_id == "704"
    assert added.invalid_vehicles[0].vehicle_id == "bad-vin"
    assert deleted.success is True
    assert removed.success is True
    assert events.has_next is True
    assert events.items[0].operation_code == 11
    assert scoring_created.scoring_id == "801"
    assert scoring_item.is_completed is True
    assert valuation_item.avg_price_with_condition == 2100000
