from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.ratings import RatingProfile, Review, ReviewAnswer
from avito.realty import RealtyAnalyticsReport, RealtyBooking, RealtyListing, RealtyPricing
from avito.tariffs import Tariff


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


def test_realty_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = json.loads(request.content.decode()) if request.content else None
        if path == "/core/v1/accounts/10/items/20/bookings":
            assert payload == {"blockedDates": ["2026-04-18"]}
            return httpx.Response(200, json={"result": "success"})
        if path == "/realty/v1/accounts/10/items/20/bookings":
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
                            "base_price": 12000,
                            "contact": {"name": "Иван", "email": "ivan@example.com"},
                        }
                    ]
                },
            )
        if path == "/realty/v1/accounts/10/items/20/prices":
            assert payload == {"periods": [{"dateFrom": "2026-05-01", "price": 5000}]}
            return httpx.Response(200, json={"result": "success"})
        if path == "/realty/v1/items/intervals":
            assert payload == {
                "itemId": 20,
                "intervals": [{"date": "2026-05-01", "available": True}],
            }
            return httpx.Response(200, json={"result": "success"})
        if path == "/realty/v1/items/20/base":
            assert payload == {"minStayDays": 2}
            return httpx.Response(200, json={"result": "success"})
        if path == "/realty/v1/marketPriceCorrespondence/20/5000000":
            return httpx.Response(200, json={"correspondence": "normal"})
        assert path == "/realty/v1/report/create/20"
        return httpx.Response(
            200,
            json={"success": {"success": {"reportLink": "https://example.com/realty-report/20"}}},
        )

    transport = make_transport(httpx.MockTransport(handler))
    booking = RealtyBooking(transport, resource_id="20", user_id="10")
    pricing = RealtyPricing(transport, resource_id="20", user_id="10")
    listing = RealtyListing(transport, resource_id="20")
    analytics = RealtyAnalyticsReport(transport, resource_id="20")

    updated_bookings = booking.update_bookings_info(payload={"blockedDates": ["2026-04-18"]})
    bookings = booking.list_realty_bookings()
    updated_prices = pricing.update_realty_prices(
        payload={"periods": [{"dateFrom": "2026-05-01", "price": 5000}]}
    )
    intervals = listing.get_intervals(
        payload={"itemId": 20, "intervals": [{"date": "2026-05-01", "available": True}]}
    )
    base = listing.update_base_params(payload={"minStayDays": 2})
    market = analytics.get_market_price_correspondence_v1(price=5000000)
    report = analytics.get_report_for_classified()

    assert updated_bookings.success is True
    assert bookings.items[0].guest_name == "Иван"
    assert updated_prices.status == "success"
    assert intervals.success is True
    assert base.success is True
    assert market.correspondence == "normal"
    assert report.report_link == "https://example.com/realty-report/20"


def test_ratings_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/ratings/v1/answers":
            assert json.loads(request.content.decode()) == {
                "reviewId": 123,
                "text": "Спасибо за отзыв",
            }
            return httpx.Response(200, json={"id": 456, "createdAt": 1713427200})
        if path == "/ratings/v1/answers/456":
            return httpx.Response(200, json={"success": True})
        if path == "/ratings/v1/info":
            return httpx.Response(
                200,
                json={
                    "isEnabled": True,
                    "rating": {"score": 4.7, "reviewsCount": 25, "reviewsWithScoreCount": 20},
                },
            )
        assert path == "/ratings/v1/reviews"
        assert request.url.params["page"] == "2"
        return httpx.Response(
            200,
            json={
                "total": 25,
                "reviews": [
                    {
                        "id": 123,
                        "score": 5,
                        "stage": "done",
                        "text": "Все отлично",
                        "createdAt": 1713427200,
                        "canAnswer": True,
                        "usedInScore": True,
                    }
                ],
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    answer = ReviewAnswer(transport, resource_id="456")
    profile = RatingProfile(transport)
    review = Review(transport)

    created = answer.create_review_answer_v1(payload={"reviewId": 123, "text": "Спасибо за отзыв"})
    deleted = answer.delete_review_answer_v1()
    info = profile.get_ratings_info_v1()
    reviews = review.list_reviews_v1(params={"page": 2})

    assert created.answer_id == "456"
    assert deleted.success is True
    assert info.score == 4.7
    assert reviews.total == 25
    assert reviews.items[0].text == "Все отлично"


def test_tariff_flow() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tariff/info/1"
        return httpx.Response(
            200,
            json={
                "current": {
                    "level": "Тариф Максимальный",
                    "isActive": True,
                    "startTime": 1713427200,
                    "closeTime": 1716029200,
                    "bonus": 10,
                    "packages": [{"id": 1}, {"id": 2}],
                    "price": {"price": 1990, "originalPrice": 2490},
                },
                "scheduled": {
                    "level": "Тариф Базовый",
                    "isActive": False,
                    "startTime": 1716029300,
                    "closeTime": None,
                    "bonus": 0,
                    "packages": [],
                    "price": {"price": 990, "originalPrice": 990},
                },
            },
        )

    tariff = Tariff(make_transport(httpx.MockTransport(handler)))

    info = tariff.get_tariff_info()

    assert info.current is not None
    assert info.current.level == "Тариф Максимальный"
    assert info.current.packages_count == 2
    assert info.current.price == 1990
    assert info.scheduled is not None
    assert info.scheduled.is_active is False
