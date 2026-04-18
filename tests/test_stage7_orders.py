from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.orders import DeliveryOrder, DeliveryTask, Order, OrderLabel, SandboxDelivery, Stock
from avito.orders.models import (
    AddSortingCentersRequest,
    AddTariffV2Request,
    CancelParcelRequest,
    CancelSandboxParcelRequest,
    ChangeParcelRequest,
    CustomAreaScheduleEntry,
    CustomAreaScheduleRequest,
    DeliveryAddress,
    DeliveryAnnouncementRequest,
    DeliveryDateInterval,
    DeliveryDirection,
    DeliveryDirectionZone,
    DeliveryParcelIdsRequest,
    DeliveryParcelRequest,
    DeliveryParcelResultRequest,
    DeliveryRestriction,
    DeliveryTariffItem,
    DeliveryTariffValue,
    DeliveryTariffZone,
    DeliveryTerms,
    DeliveryTermsZone,
    DeliveryTrackingRequest,
    GetChangeParcelInfoRequest,
    GetRegisteredParcelIdRequest,
    GetSandboxParcelInfoRequest,
    OrderAcceptReturnRequest,
    OrderApplyTransitionRequest,
    OrderCncDetailsRequest,
    OrderConfirmationCodeRequest,
    OrderCourierRangeRequest,
    OrderDeliveryProperties,
    OrderLabelsRequest,
    OrderMarkingsRequest,
    OrderTrackingNumberRequest,
    ProhibitOrderAcceptanceRequest,
    RealAddress,
    SandboxAnnouncementDelivery,
    SandboxAnnouncementPackage,
    SandboxAnnouncementParticipant,
    SandboxArea,
    SandboxAreasRequest,
    SandboxCancelAnnouncementOptions,
    SandboxCancelAnnouncementRequest,
    SandboxConfirmationCodeRequest,
    SandboxCreateAnnouncementOptions,
    SandboxCreateAnnouncementRequest,
    SandboxDeliveryPoint,
    SandboxGetAnnouncementEventRequest,
    SetOrderPropertiesRequest,
    SetOrderRealAddressRequest,
    SortingCenterUpload,
    StockInfoRequest,
    StockUpdateEntry,
    StockUpdateRequest,
    TaggedSortingCenter,
    TaggedSortingCentersRequest,
    UpdateTermsRequest,
    WeeklySchedule,
)


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


def test_order_management_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/order-management/1/orders":
            return httpx.Response(
                200,
                json={
                    "orders": [{"id": "ord-1", "status": "new", "buyerInfo": {"fullName": "Иван"}}],
                    "total": 1,
                },
            )
        if path == "/order-management/1/markings":
            assert payload == {"orderId": "ord-1", "codes": ["abc"]}
            return httpx.Response(
                200, json={"result": {"success": True, "orderId": "ord-1", "status": "marked"}}
            )
        if path == "/order-management/1/order/applyTransition":
            assert payload == {"orderId": "ord-1", "transition": "confirm"}
            return httpx.Response(
                200, json={"result": {"success": True, "orderId": "ord-1", "status": "confirmed"}}
            )
        if path == "/order-management/1/order/checkConfirmationCode":
            assert payload == {"orderId": "ord-1", "code": "1234"}
            return httpx.Response(
                200, json={"result": {"success": True, "orderId": "ord-1", "status": "code-valid"}}
            )
        if path == "/order-management/1/order/cncSetDetails":
            assert payload == {"orderId": "ord-1", "pickupPointId": "pvz-1"}
            return httpx.Response(
                200, json={"result": {"success": True, "orderId": "ord-1", "status": "pickup-set"}}
            )
        if path == "/order-management/1/order/getCourierDeliveryRange":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "address": "Москва",
                        "timeIntervals": [
                            {
                                "id": "int-1",
                                "date": "2026-04-18",
                                "startAt": "10:00",
                                "endAt": "12:00",
                            }
                        ],
                    }
                },
            )
        if path == "/order-management/1/order/setCourierDeliveryRange":
            assert payload == {"orderId": "ord-1", "intervalId": "int-1"}
            return httpx.Response(200, json={"result": {"success": True, "status": "range-set"}})
        if path == "/order-management/1/order/setTrackingNumber":
            assert payload == {"orderId": "ord-1", "trackingNumber": "TRK-1"}
            return httpx.Response(200, json={"result": {"success": True, "status": "tracking-set"}})
        assert path == "/order-management/1/order/acceptReturnOrder"
        assert payload == {"orderId": "ord-1", "postalOfficeId": "ops-1"}
        return httpx.Response(200, json={"result": {"success": True, "status": "return-accepted"}})

    order = Order(make_transport(httpx.MockTransport(handler)), resource_id="ord-1")

    orders = order.list()
    marked = order.update_markings(request=OrderMarkingsRequest(order_id="ord-1", codes=["abc"]))
    applied = order.apply(
        request=OrderApplyTransitionRequest(order_id="ord-1", transition="confirm")
    )
    code_checked = order.check_confirmation_code(
        request=OrderConfirmationCodeRequest(order_id="ord-1", code="1234")
    )
    cnc = order.set_cnc_details(
        request=OrderCncDetailsRequest(order_id="ord-1", pickup_point_id="pvz-1")
    )
    courier_ranges = order.get_courier_delivery_range()
    courier_set = order.set_courier_delivery_range(
        request=OrderCourierRangeRequest(order_id="ord-1", interval_id="int-1")
    )
    tracking = order.update_tracking_number(
        request=OrderTrackingNumberRequest(order_id="ord-1", tracking_number="TRK-1")
    )
    returned = order.accept_return_order(
        request=OrderAcceptReturnRequest(order_id="ord-1", postal_office_id="ops-1")
    )

    assert orders.items[0].buyer_name == "Иван"
    assert marked.status == "marked"
    assert applied.status == "confirmed"
    assert code_checked.status == "code-valid"
    assert cnc.status == "pickup-set"
    assert courier_ranges.items[0].interval_id == "int-1"
    assert courier_set.status == "range-set"
    assert tracking.status == "tracking-set"
    assert returned.status == "return-accepted"


def test_labels_binary_download_flow() -> None:
    pdf_bytes = b"%PDF-1.4 fake"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/order-management/1/orders/labels":
            assert json.loads(request.content.decode()) == {"orderIds": ["ord-1"]}
            return httpx.Response(200, json={"result": {"taskId": 42, "status": "created"}})
        assert request.url.path == "/order-management/1/orders/labels/42/download"
        return httpx.Response(
            200,
            content=pdf_bytes,
            headers={
                "content-type": "application/pdf",
                "content-disposition": 'attachment; filename="label-42.pdf"',
            },
        )

    label = OrderLabel(make_transport(httpx.MockTransport(handler)), resource_id="42")

    task = label.create(request=OrderLabelsRequest(order_ids=["ord-1"]))
    pdf = label.download()

    assert task.task_id == "42"
    assert pdf.filename == "label-42.pdf"
    assert pdf.binary.content == pdf_bytes


def test_delivery_production_and_sandbox_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/createAnnouncement":
            assert payload == {"orderId": "ord-1"}
            return httpx.Response(
                200, json={"data": {"taskId": 11, "status": "announcement-created"}}
            )
        if path == "/createParcel":
            assert payload == {"orderId": "ord-1", "parcelId": "par-1"}
            return httpx.Response(
                200, json={"data": {"parcelId": "par-1", "status": "parcel-created"}}
            )
        if path == "/cancelAnnouncement":
            assert payload == {"orderId": "ord-1"}
            return httpx.Response(200, json={"data": {"status": "announcement-cancelled"}})
        if path == "/delivery/order/changeParcelResult":
            assert payload == {"parcelId": "par-1", "result": "ok"}
            return httpx.Response(200, json={"data": {"status": "callback-accepted"}})
        if path == "/sandbox/changeParcels":
            assert payload == {"parcelIds": ["par-1"]}
            return httpx.Response(200, json={"data": {"status": "parcels-updated"}})
        if path == "/delivery-sandbox/announcements/create":
            assert payload == {"orderId": "sand-1"}
            return httpx.Response(
                200, json={"data": {"taskId": 51, "status": "sandbox-announcement-created"}}
            )
        if path == "/delivery-sandbox/announcements/track":
            assert payload == {"orderId": "sand-1"}
            return httpx.Response(200, json={"data": {"status": "tracked"}})
        if path == "/delivery-sandbox/areas/custom-schedule":
            assert payload == [
                {
                    "providerAreaNumber": ["area-1"],
                    "services": ["delivery"],
                    "customSchedule": [{"date": "2026-04-20", "intervals": ["10:00:00/18:00:00"]}],
                }
            ]
            return httpx.Response(200, json={"data": {"status": "schedule-updated"}})
        if path == "/delivery-sandbox/cancelParcel":
            assert payload == {"parcelID": "spar-1", "actor": "receiver"}
            return httpx.Response(200, json={"data": {"status": "parcel-cancelled"}})
        if path == "/delivery-sandbox/order/checkConfirmationCode":
            assert payload == {"parcelID": "spar-1", "confirmCode": "1234"}
            return httpx.Response(200, json={"data": {"status": "success"}})
        if path == "/delivery-sandbox/order/properties":
            assert payload == {
                "orderId": "sand-1",
                "properties": {
                    "delivery": {"cost": 19900},
                    "dimensions": [10, 20, 30],
                    "weight": 500,
                },
            }
            return httpx.Response(200, json={"data": {"status": "properties-set"}})
        if path == "/delivery-sandbox/order/realAddress":
            assert payload == {
                "orderId": "sand-1",
                "address": {"addressType": "SENDER_SEND", "terminalNumber": "term-1"},
            }
            return httpx.Response(200, json={"data": {"status": "real-address-set"}})
        if path == "/delivery-sandbox/order/tracking":
            assert payload == {
                "orderId": "sand-1",
                "avitoStatus": "IN_TRANSIT",
                "avitoEventType": "RECEIVED_AT_TRANSIT_TERMINAL",
                "providerEventCode": "evt-1",
                "date": "2026-04-20T10:00:00Z",
                "location": "Москва",
            }
            return httpx.Response(200, json={"data": {"status": "tracking-saved"}})
        if path == "/delivery-sandbox/prohibitOrderAcceptance":
            assert payload == {"orderId": "sand-1"}
            return httpx.Response(200, json={"data": {"status": "acceptance-prohibited"}})
        if path == "/delivery-sandbox/sorting-center":
            return httpx.Response(
                200,
                json={
                    "data": {
                        "sortingCenters": [{"id": "sc-1", "name": "Центр 1", "city": "Москва"}]
                    }
                },
            )
        if path == "/delivery-sandbox/tariffs/sorting-center":
            assert payload == [
                {
                    "deliveryProviderId": "sc-1",
                    "name": "Центр 1",
                    "address": {
                        "country": "Россия",
                        "region": "Москва",
                        "locality": "Москва",
                        "fias": "fias-1",
                        "zipCode": "101000",
                        "lat": 55.75,
                        "lng": 37.61,
                    },
                    "phones": ["79990000000"],
                    "itinerary": "Вход справа",
                    "photos": [],
                    "schedule": {
                        "mon": ["09:00:00/18:00:00"],
                        "tue": ["09:00:00/18:00:00"],
                        "wed": ["09:00:00/18:00:00"],
                        "thu": ["09:00:00/18:00:00"],
                        "fri": ["09:00:00/18:00:00"],
                        "sat": [],
                        "sun": [],
                    },
                    "restriction": {
                        "maxWeight": 10000,
                        "maxDimensions": [100, 50, 50],
                        "maxDeclaredCost": 100000,
                    },
                    "directionTag": "moscow",
                }
            ]
            return httpx.Response(
                200, json={"data": {"taskId": 62, "status": "sorting-centers-added"}}
            )
        if path == "/delivery-sandbox/tariffs/tf-1/areas":
            assert payload == {"areas": [{"city": "Москва"}]}
            return httpx.Response(200, json={"data": {"taskId": 61, "status": "areas-added"}})
        if path == "/delivery-sandbox/tariffs/tf-1/tagged-sorting-centers":
            assert payload == [{"deliveryProviderId": "sc-1", "directionTag": "moscow"}]
            return httpx.Response(200, json={"data": {"status": "tags-added"}})
        if path == "/delivery-sandbox/tariffs/tf-1/terms":
            assert payload == [
                {
                    "deliveryProviderZoneId": "zone-1",
                    "minTerm": 1,
                    "maxTerm": 2,
                    "name": "zone",
                }
            ]
            return httpx.Response(200, json={"data": {"status": "terms-updated"}})
        if path == "/delivery-sandbox/tariffsV2":
            assert payload == {
                "name": "Tariff",
                "deliveryProviderTariffId": "tariff-1",
                "directions": [
                    {
                        "providerDirectionId": "dir-1",
                        "tagFrom": "moscow",
                        "tagTo": "spb",
                        "zones": [{"tariffZoneId": "tz-1", "termsZoneId": "term-1", "type": "0"}],
                    }
                ],
                "tariffZones": [
                    {
                        "name": "Zone",
                        "deliveryProviderZoneId": "tz-1",
                        "items": [
                            {
                                "calculationMechanic": "GAP_TO_COST",
                                "chargeableParameter": "WEIGHT",
                                "serviceName": "DELIVERY",
                                "values": [{"cost": 10000, "maxWeight": 3000}],
                            }
                        ],
                    }
                ],
                "termsZones": [
                    {
                        "deliveryProviderZoneId": "term-1",
                        "minTerm": 1,
                        "maxTerm": 2,
                        "name": "term",
                    }
                ],
            }
            return httpx.Response(200, json={"data": {"taskId": 63, "status": "tariff-added"}})
        if path == "/delivery-sandbox/v1/cancelAnnouncement":
            assert payload == {
                "announcementID": "ann-1",
                "date": "2026-04-20T10:00:00Z",
                "options": {"urlToCancelAnnouncement": "https://example.com/cancel"},
            }
            return httpx.Response(200, json={"data": {"status": "announcement-cancel-requested"}})
        if path == "/delivery-sandbox/v1/cancelParcel":
            assert payload == {"parcelID": "spar-1"}
            return httpx.Response(200, json={"data": {"status": "sandbox-parcel-cancelled"}})
        if path == "/delivery-sandbox/v1/changeParcel":
            assert payload == {"type": "changeReceiver", "parcelID": "spar-1"}
            return httpx.Response(200, json={"data": {"status": "change-created"}})
        if path == "/delivery-sandbox/v1/createAnnouncement":
            assert payload == {
                "announcementID": "ann-1",
                "barcode": "barcode-1",
                "sender": {
                    "type": "3PL",
                    "phones": ["79990000000"],
                    "email": "sender@example.com",
                    "name": "Sender",
                    "delivery": {
                        "type": "TERMINAL",
                        "terminal": {"provider": "avito", "id": "term-1"},
                    },
                },
                "receiver": {
                    "type": "ABD",
                    "phones": ["79990000001"],
                    "email": "receiver@example.com",
                    "name": "Receiver",
                    "delivery": {
                        "type": "TERMINAL",
                        "terminal": {"provider": "avito", "id": "term-2"},
                    },
                },
                "announcementType": "DELIVERY",
                "date": "2026-04-20T10:00:00Z",
                "packages": [{"id": "pkg-1", "parcelIDs": ["spar-1"]}],
                "options": {"urlToSendAnnouncement": "https://example.com/announce"},
            }
            return httpx.Response(200, json={"data": {"status": "announcement-created-v1"}})
        if path == "/delivery-sandbox/v1/getAnnouncementEvent":
            assert payload == {"announcementID": "ann-1"}
            return httpx.Response(200, json={"data": {"status": "event-ready"}})
        if path == "/delivery-sandbox/v1/getChangeParcelInfo":
            assert payload == {"applicationID": "app-1"}
            return httpx.Response(200, json={"data": {"status": "change-info-ready"}})
        if path == "/delivery-sandbox/v1/getParcelInfo":
            assert payload == {"parcelID": "spar-1"}
            return httpx.Response(200, json={"data": {"status": "parcel-info-ready"}})
        if path == "/delivery-sandbox/v1/getRegisteredParcelID":
            assert payload == {"orderID": "sand-1"}
            return httpx.Response(200, json={"data": {"parcelId": "reg-1", "status": "registered"}})
        if path == "/delivery-sandbox/v2/createParcel":
            assert payload == {"orderId": "sand-1", "parcelId": "spar-1"}
            return httpx.Response(
                200, json={"data": {"parcelId": "spar-1", "status": "sandbox-parcel-created"}}
            )
        assert path == "/delivery-sandbox/tasks/51"
        return httpx.Response(200, json={"data": {"taskId": 51, "status": "done"}})

    transport = make_transport(httpx.MockTransport(handler))
    delivery = DeliveryOrder(transport, resource_id="ord-1")
    sandbox = SandboxDelivery(transport, resource_id="sand-1")
    task = DeliveryTask(transport, resource_id="51")

    announcement = delivery.create_announcement(
        request=DeliveryAnnouncementRequest(order_id="ord-1")
    )
    parcel = delivery.create(request=DeliveryParcelRequest(order_id="ord-1", parcel_id="par-1"))
    cancelled = delivery.delete(request=DeliveryAnnouncementRequest(order_id="ord-1"))
    callback = delivery.create_change_parcel_result(
        request=DeliveryParcelResultRequest(parcel_id="par-1", result="ok")
    )
    changed = delivery.update_change_parcels(request=DeliveryParcelIdsRequest(parcel_ids=["par-1"]))
    sandbox_announcement = sandbox.create_announcement(
        request=DeliveryAnnouncementRequest(order_id="sand-1")
    )
    tracked = sandbox.track_announcement(request=DeliveryAnnouncementRequest(order_id="sand-1"))
    schedule = sandbox.update_custom_area_schedule(
        request=CustomAreaScheduleRequest(
            items=[
                CustomAreaScheduleEntry(
                    provider_area_numbers=["area-1"],
                    services=["delivery"],
                    custom_schedule=[
                        DeliveryDateInterval(
                            date="2026-04-20",
                            intervals=["10:00:00/18:00:00"],
                        )
                    ],
                )
            ]
        )
    )
    cancelled_parcel = sandbox.cancel_parcel(
        request=CancelParcelRequest(parcel_id="spar-1", actor="receiver")
    )
    sandbox_code_checked = sandbox.check_confirmation_code(
        request=SandboxConfirmationCodeRequest(parcel_id="spar-1", confirm_code="1234")
    )
    props = sandbox.set_order_properties(
        request=SetOrderPropertiesRequest(
            order_id="sand-1",
            properties=OrderDeliveryProperties(
                delivery=DeliveryTerms(cost=19900),
                dimensions=[10, 20, 30],
                weight=500,
            ),
        )
    )
    real_address = sandbox.set_order_real_address(
        request=SetOrderRealAddressRequest(
            order_id="sand-1",
            address=RealAddress(address_type="SENDER_SEND", terminal_number="term-1"),
        )
    )
    tracking = sandbox.tracking(
        request=DeliveryTrackingRequest(
            order_id="sand-1",
            avito_status="IN_TRANSIT",
            avito_event_type="RECEIVED_AT_TRANSIT_TERMINAL",
            provider_event_code="evt-1",
            date="2026-04-20T10:00:00Z",
            location="Москва",
        )
    )
    prohibited = sandbox.prohibit_order_acceptance(
        request=ProhibitOrderAcceptanceRequest(order_id="sand-1")
    )
    centers = sandbox.list_sorting_center()
    address = DeliveryAddress(
        country="Россия",
        region="Москва",
        locality="Москва",
        fias="fias-1",
        zip_code="101000",
        lat=55.75,
        lng=37.61,
    )
    schedule_model = WeeklySchedule(
        mon=["09:00:00/18:00:00"],
        tue=["09:00:00/18:00:00"],
        wed=["09:00:00/18:00:00"],
        thu=["09:00:00/18:00:00"],
        fri=["09:00:00/18:00:00"],
        sat=[],
        sun=[],
    )
    restriction = DeliveryRestriction(
        max_weight=10000,
        max_dimensions=[100, 50, 50],
        max_declared_cost=100000,
    )
    sorting_centers_added = sandbox.add_sorting_center(
        request=AddSortingCentersRequest(
            items=[
                SortingCenterUpload(
                    delivery_provider_id="sc-1",
                    name="Центр 1",
                    address=address,
                    phones=["79990000000"],
                    itinerary="Вход справа",
                    photos=[],
                    schedule=schedule_model,
                    restriction=restriction,
                    direction_tag="moscow",
                )
            ]
        )
    )
    added_areas = sandbox.add_areas(
        tariff_id="tf-1",
        request=SandboxAreasRequest(areas=[SandboxArea(city="Москва")]),
    )
    tagged = sandbox.add_tags_to_sorting_center(
        tariff_id="tf-1",
        request=TaggedSortingCentersRequest(
            items=[TaggedSortingCenter(delivery_provider_id="sc-1", direction_tag="moscow")]
        ),
    )
    updated_terms = sandbox.update_terms(
        tariff_id="tf-1",
        request=UpdateTermsRequest(
            items=[
                DeliveryTermsZone(
                    delivery_provider_zone_id="zone-1", min_term=1, max_term=2, name="zone"
                )
            ]
        ),
    )
    tariff = sandbox.add_tariff_v2(
        request=AddTariffV2Request(
            name="Tariff",
            delivery_provider_tariff_id="tariff-1",
            directions=[
                DeliveryDirection(
                    provider_direction_id="dir-1",
                    tag_from="moscow",
                    tag_to="spb",
                    zones=[
                        DeliveryDirectionZone(
                            tariff_zone_id="tz-1", terms_zone_id="term-1", type="0"
                        )
                    ],
                )
            ],
            tariff_zones=[
                DeliveryTariffZone(
                    name="Zone",
                    delivery_provider_zone_id="tz-1",
                    items=[
                        DeliveryTariffItem(
                            calculation_mechanic="GAP_TO_COST",
                            chargeable_parameter="WEIGHT",
                            service_name="DELIVERY",
                            values=[DeliveryTariffValue(cost=10000, max_weight=3000)],
                        )
                    ],
                )
            ],
            terms_zones=[
                DeliveryTermsZone(
                    delivery_provider_zone_id="term-1", min_term=1, max_term=2, name="term"
                )
            ],
        )
    )
    cancelled_announcement_v1 = sandbox.cancel_announcement_v1(
        request=SandboxCancelAnnouncementRequest(
            announcement_id="ann-1",
            date="2026-04-20T10:00:00Z",
            options=SandboxCancelAnnouncementOptions(
                url_to_cancel_announcement="https://example.com/cancel"
            ),
        )
    )
    cancelled_parcel_v1 = sandbox.cancel_parcel_v1(
        request=CancelSandboxParcelRequest(parcel_id="spar-1")
    )
    changed_parcel_v1 = sandbox.change_parcel_v1(
        request=ChangeParcelRequest(type="changeReceiver", parcel_id="spar-1")
    )
    created_announcement_v1 = sandbox.create_announcement_v1(
        request=SandboxCreateAnnouncementRequest(
            announcement_id="ann-1",
            barcode="barcode-1",
            sender=SandboxAnnouncementParticipant(
                type="3PL",
                phones=["79990000000"],
                email="sender@example.com",
                name="Sender",
                delivery=SandboxAnnouncementDelivery(
                    type="TERMINAL",
                    terminal=SandboxDeliveryPoint(provider="avito", point_id="term-1"),
                ),
            ),
            receiver=SandboxAnnouncementParticipant(
                type="ABD",
                phones=["79990000001"],
                email="receiver@example.com",
                name="Receiver",
                delivery=SandboxAnnouncementDelivery(
                    type="TERMINAL",
                    terminal=SandboxDeliveryPoint(provider="avito", point_id="term-2"),
                ),
            ),
            announcement_type="DELIVERY",
            date="2026-04-20T10:00:00Z",
            packages=[SandboxAnnouncementPackage(package_id="pkg-1", parcel_ids=["spar-1"])],
            options=SandboxCreateAnnouncementOptions(
                url_to_send_announcement="https://example.com/announce"
            ),
        )
    )
    event_v1 = sandbox.get_announcement_event_v1(
        request=SandboxGetAnnouncementEventRequest(announcement_id="ann-1")
    )
    change_info_v1 = sandbox.get_change_parcel_info_v1(
        request=GetChangeParcelInfoRequest(application_id="app-1")
    )
    parcel_info_v1 = sandbox.get_parcel_info_v1(
        request=GetSandboxParcelInfoRequest(parcel_id="spar-1")
    )
    registered_parcel_id_v1 = sandbox.get_registered_parcel_id_v1(
        request=GetRegisteredParcelIdRequest(order_id="sand-1")
    )
    sandbox_parcel = sandbox.create_parcel(
        request=DeliveryParcelRequest(order_id="sand-1", parcel_id="spar-1")
    )
    task_info = task.get()

    assert announcement.task_id == "11"
    assert parcel.parcel_id == "par-1"
    assert cancelled.status == "announcement-cancelled"
    assert callback.status == "callback-accepted"
    assert changed.status == "parcels-updated"
    assert sandbox_announcement.task_id == "51"
    assert tracked.status == "tracked"
    assert schedule.status == "schedule-updated"
    assert cancelled_parcel.status == "parcel-cancelled"
    assert sandbox_code_checked.status == "success"
    assert props.status == "properties-set"
    assert real_address.status == "real-address-set"
    assert tracking.status == "tracking-saved"
    assert prohibited.status == "acceptance-prohibited"
    assert centers.items[0].city == "Москва"
    assert sorting_centers_added.task_id == "62"
    assert added_areas.status == "areas-added"
    assert tagged.status == "tags-added"
    assert updated_terms.status == "terms-updated"
    assert tariff.task_id == "63"
    assert cancelled_announcement_v1.status == "announcement-cancel-requested"
    assert cancelled_parcel_v1.status == "sandbox-parcel-cancelled"
    assert changed_parcel_v1.status == "change-created"
    assert created_announcement_v1.status == "announcement-created-v1"
    assert event_v1.status == "event-ready"
    assert change_info_v1.status == "change-info-ready"
    assert parcel_info_v1.status == "parcel-info-ready"
    assert registered_parcel_id_v1.parcel_id == "reg-1"
    assert sandbox_parcel.parcel_id == "spar-1"
    assert task_info.status == "done"


def test_stock_management_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/stock-management/1/info":
            assert json.loads(request.content.decode()) == {"itemIds": [123321]}
            return httpx.Response(
                200,
                json={
                    "stocks": [
                        {
                            "item_id": 123321,
                            "quantity": 5,
                            "is_multiple": True,
                            "is_unlimited": False,
                            "is_out_of_stock": False,
                        }
                    ]
                },
            )
        assert request.url.path == "/stock-management/1/stocks"
        assert request.method == "PUT"
        assert json.loads(request.content.decode()) == {
            "stocks": [{"item_id": 123321, "quantity": 7}]
        }
        return httpx.Response(
            200,
            json={
                "stocks": [
                    {"item_id": 123321, "external_id": "AB123456", "success": True, "errors": []}
                ]
            },
        )

    stock = Stock(make_transport(httpx.MockTransport(handler)), resource_id="123321")

    info = stock.get(request=StockInfoRequest(item_ids=[123321]))
    updated = stock.update(
        request=StockUpdateRequest(stocks=[StockUpdateEntry(item_id=123321, quantity=7)])
    )

    assert info.items[0].quantity == 5
    assert updated.items[0].external_id == "AB123456"
    assert updated.items[0].success is True
