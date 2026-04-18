from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.orders import DeliveryOrder, DeliveryTask, Order, OrderLabel, SandboxDelivery, Stock


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
            return httpx.Response(200, json={"orders": [{"id": "ord-1", "status": "new", "buyerInfo": {"fullName": "Иван"}}], "total": 1})
        if path == "/order-management/1/markings":
            assert payload == {"orderId": "ord-1", "codes": ["abc"]}
            return httpx.Response(200, json={"result": {"success": True, "orderId": "ord-1", "status": "marked"}})
        if path == "/order-management/1/order/applyTransition":
            assert payload == {"orderId": "ord-1", "transition": "confirm"}
            return httpx.Response(200, json={"result": {"success": True, "orderId": "ord-1", "status": "confirmed"}})
        if path == "/order-management/1/order/checkConfirmationCode":
            assert payload == {"orderId": "ord-1", "code": "1234"}
            return httpx.Response(200, json={"result": {"success": True, "orderId": "ord-1", "status": "code-valid"}})
        if path == "/order-management/1/order/cncSetDetails":
            assert payload == {"orderId": "ord-1", "pickupPointId": "pvz-1"}
            return httpx.Response(200, json={"result": {"success": True, "orderId": "ord-1", "status": "pickup-set"}})
        if path == "/order-management/1/order/getCourierDeliveryRange":
            return httpx.Response(200, json={"result": {"address": "Москва", "timeIntervals": [{"id": "int-1", "date": "2026-04-18", "startAt": "10:00", "endAt": "12:00"}]}})
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
    marked = order.update_markings(payload={"orderId": "ord-1", "codes": ["abc"]})
    applied = order.apply(payload={"orderId": "ord-1", "transition": "confirm"})
    code_checked = order.check_confirmation_code(payload={"orderId": "ord-1", "code": "1234"})
    cnc = order.set_cnc_details(payload={"orderId": "ord-1", "pickupPointId": "pvz-1"})
    courier_ranges = order.get_courier_delivery_range()
    courier_set = order.set_courier_delivery_range(payload={"orderId": "ord-1", "intervalId": "int-1"})
    tracking = order.update_tracking_number(payload={"orderId": "ord-1", "trackingNumber": "TRK-1"})
    returned = order.accept_return_order(payload={"orderId": "ord-1", "postalOfficeId": "ops-1"})

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

    task = label.create(payload={"orderIds": ["ord-1"]})
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
            return httpx.Response(200, json={"data": {"taskId": 11, "status": "announcement-created"}})
        if path == "/createParcel":
            assert payload == {"orderId": "ord-1", "parcelId": "par-1"}
            return httpx.Response(200, json={"data": {"parcelId": "par-1", "status": "parcel-created"}})
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
            return httpx.Response(200, json={"data": {"taskId": 51, "status": "sandbox-announcement-created"}})
        if path == "/delivery-sandbox/announcements/track":
            assert payload == {"orderId": "sand-1"}
            return httpx.Response(200, json={"data": {"status": "tracked"}})
        if path == "/delivery-sandbox/sorting-center":
            return httpx.Response(200, json={"data": {"sortingCenters": [{"id": "sc-1", "name": "Центр 1", "city": "Москва"}]}})
        if path == "/delivery-sandbox/tariffs/tf-1/areas":
            assert payload == {"areas": [{"city": "Москва"}]}
            return httpx.Response(200, json={"data": {"taskId": 61, "status": "areas-added"}})
        if path == "/delivery-sandbox/v2/createParcel":
            assert payload == {"orderId": "sand-1", "parcelId": "spar-1"}
            return httpx.Response(200, json={"data": {"parcelId": "spar-1", "status": "sandbox-parcel-created"}})
        assert path == "/delivery-sandbox/tasks/51"
        return httpx.Response(200, json={"data": {"taskId": 51, "status": "done"}})

    transport = make_transport(httpx.MockTransport(handler))
    delivery = DeliveryOrder(transport, resource_id="ord-1")
    sandbox = SandboxDelivery(transport, resource_id="sand-1")
    task = DeliveryTask(transport, resource_id="51")

    announcement = delivery.create_announcement(payload={"orderId": "ord-1"})
    parcel = delivery.create(payload={"orderId": "ord-1", "parcelId": "par-1"})
    cancelled = delivery.delete(payload={"orderId": "ord-1"})
    callback = delivery.create_change_parcel_result(payload={"parcelId": "par-1", "result": "ok"})
    changed = delivery.update_change_parcels(payload={"parcelIds": ["par-1"]})
    sandbox_announcement = sandbox.create_announcement(payload={"orderId": "sand-1"})
    tracked = sandbox.track_announcement(payload={"orderId": "sand-1"})
    centers = sandbox.list_sorting_center()
    added_areas = sandbox.add_areas(tariff_id="tf-1", payload={"areas": [{"city": "Москва"}]})
    sandbox_parcel = sandbox.create_parcel(payload={"orderId": "sand-1", "parcelId": "spar-1"})
    task_info = task.get()

    assert announcement.task_id == "11"
    assert parcel.parcel_id == "par-1"
    assert cancelled.status == "announcement-cancelled"
    assert callback.status == "callback-accepted"
    assert changed.status == "parcels-updated"
    assert sandbox_announcement.task_id == "51"
    assert tracked.status == "tracked"
    assert centers.items[0].city == "Москва"
    assert added_areas.status == "areas-added"
    assert sandbox_parcel.parcel_id == "spar-1"
    assert task_info.status == "done"


def test_stock_management_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/stock-management/1/info":
            assert json.loads(request.content.decode()) == {"itemIds": [123321]}
            return httpx.Response(
                200,
                json={"stocks": [{"item_id": 123321, "quantity": 5, "is_multiple": True, "is_unlimited": False, "is_out_of_stock": False}]},
            )
        assert request.url.path == "/stock-management/1/stocks"
        assert request.method == "PUT"
        assert json.loads(request.content.decode()) == {"stocks": [{"item_id": 123321, "quantity": 7}]}
        return httpx.Response(
            200,
            json={"stocks": [{"item_id": 123321, "external_id": "AB123456", "success": True, "errors": []}]},
        )

    stock = Stock(make_transport(httpx.MockTransport(handler)), resource_id="123321")

    info = stock.get(payload={"itemIds": [123321]})
    updated = stock.update(payload={"stocks": [{"item_id": 123321, "quantity": 7}]})

    assert info.items[0].quantity == 5
    assert updated.items[0].external_id == "AB123456"
    assert updated.items[0].success is True
