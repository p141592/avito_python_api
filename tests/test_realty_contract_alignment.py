from __future__ import annotations

import inspect

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.realty import RealtyBooking


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


def test_realty_bookings_requires_date_start_and_date_end() -> None:
    signature = inspect.signature(RealtyBooking.list_realty_bookings)

    assert signature.parameters["date_start"].default is inspect._empty
    assert signature.parameters["date_end"].default is inspect._empty


def test_realty_bookings_sends_required_query_params() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/realty/v1/accounts/10/items/20/bookings"
        assert request.url.params["date_start"] == "2026-05-01"
        assert request.url.params["date_end"] == "2026-05-05"
        assert request.url.params["with_unpaid"] == "true"
        return httpx.Response(200, json={"bookings": []})

    result = RealtyBooking(
        make_transport(httpx.MockTransport(handler)),
        resource_id="20",
        user_id="10",
    ).list_realty_bookings(
        date_start="2026-05-01",
        date_end="2026-05-05",
        with_unpaid=True,
    )

    assert result.to_dict() == {"items": []}


def test_realty_bookings_maps_documented_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "bookings": [
                    {
                        "avito_booking_id": 777,
                        "status": "active",
                        "check_in": "2026-05-01",
                        "check_out": "2026-05-05",
                        "guest_count": 2,
                        "nights": 4,
                        "base_price": 12000,
                        "contact": {
                            "name": "Иван",
                            "email": "ivan@example.com",
                            "phone": "9997770000",
                        },
                        "safe_deposit": {
                            "owner_amount": 4500,
                            "tax": 500,
                            "total_amount": 5000,
                        },
                    }
                ]
            },
        )

    result = RealtyBooking(
        make_transport(httpx.MockTransport(handler)),
        resource_id="20",
        user_id="10",
    ).list_realty_bookings(
        date_start="2026-05-01",
        date_end="2026-05-05",
    )

    assert result.items[0].booking_id == 777
    assert (
        result.items[0].contact is not None and result.items[0].contact.email == "ivan@example.com"
    )
    assert result.items[0].safe_deposit is not None
    assert result.to_dict() == {
        "items": [
            {
                "booking_id": 777,
                "base_price": 12000,
                "check_in": "2026-05-01",
                "check_out": "2026-05-05",
                "contact": {
                    "name": "Иван",
                    "email": "ivan@example.com",
                    "phone": "9997770000",
                },
                "guest_count": 2,
                "nights": 4,
                "safe_deposit": {
                    "owner_amount": 4500,
                    "tax": 500,
                    "total_amount": 5000,
                },
                "status": "active",
            }
        ]
    }
