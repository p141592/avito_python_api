from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from avito.ads import AdPromotion
from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport, ValidationError
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import BbipOrderItem, BbipPromotion, TargetActionPricing, TrxPromotion
from avito.promotion.models import TrxPromotionApplyItem


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


def _json(request: httpx.Request) -> dict[str, object]:
    return json.loads(request.content.decode()) if request.content else {}


def test_write_methods_dry_run_skip_transport_and_return_preview() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise AssertionError("dry_run must not call transport")

    transport = make_transport(httpx.MockTransport(handler))
    ad_promotion = AdPromotion(transport, resource_id=101, user_id=7)
    bbip = BbipPromotion(transport, resource_id=101)
    trx = TrxPromotion(transport, resource_id=101)
    pricing = TargetActionPricing(transport, resource_id=101)

    results = [
        ad_promotion.apply_vas(codes=["xl"], dry_run=True),
        ad_promotion.apply_vas_package(package_code="turbo", dry_run=True),
        ad_promotion.apply_vas_v2(codes=["highlight"], dry_run=True),
        bbip.create_order(
            items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)],
            dry_run=True,
        ),
        trx.apply(
            items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")],
            dry_run=True,
        ),
        trx.delete(dry_run=True),
        pricing.update_auto(
            action_type_id=5,
            budget_penny=8000,
            budget_type="7d",
            dry_run=True,
        ),
        pricing.update_manual(
            action_type_id=5,
            bid_penny=1500,
            limit_penny=15000,
            dry_run=True,
        ),
        pricing.delete(dry_run=True),
    ]

    assert calls == []
    assert [result.status for result in results] == ["preview"] * len(results)
    assert all(result.applied is False for result in results)
    assert all(result.details == {"validated": True} for result in results)
    assert all(result.request_payload for result in results)
    assert results[0].to_dict() == {
        "action": "apply_vas",
        "target": {"item_id": 101, "user_id": 7},
        "status": "preview",
        "applied": False,
        "request_payload": {"codes": ["xl"]},
        "warnings": [],
        "upstream_reference": None,
        "details": {"validated": True},
    }


def test_write_methods_dry_run_and_apply_build_identical_payloads() -> None:
    seen: list[tuple[str, dict[str, object]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        payload = _json(request)
        seen.append((path, payload))

        if path == "/core/v1/accounts/7/items/101/vas":
            return httpx.Response(200, json={"success": True, "status": "applied"})
        if path == "/core/v2/accounts/7/items/101/vas_packages":
            return httpx.Response(200, json={"success": True, "status": "package_applied"})
        if path == "/core/v2/items/101/vas/":
            return httpx.Response(200, json={"success": True, "status": "v2_applied"})
        if path == "/promotion/v1/items/services/bbip/orders/create":
            return httpx.Response(
                200,
                json={"items": [{"itemId": 101, "success": True, "status": "created", "orderId": "ord-1"}]},
            )
        if path == "/trx-promo/1/apply":
            return httpx.Response(200, json={"success": {"items": [{"itemID": 101, "success": True}]}})
        if path == "/trx-promo/1/cancel":
            return httpx.Response(200, json={"success": {"items": [{"itemID": 101, "success": True}]}})
        if path == "/cpxpromo/1/setAuto":
            return httpx.Response(200, json={"items": [{"itemID": 101, "success": True, "status": "auto"}]})
        if path == "/cpxpromo/1/setManual":
            return httpx.Response(200, json={"items": [{"itemID": 101, "success": True, "status": "manual"}]})
        assert path == "/cpxpromo/1/remove"
        return httpx.Response(200, json={"items": [{"itemID": 101, "success": True, "status": "removed"}]})

    transport = make_transport(httpx.MockTransport(handler))
    ad_promotion = AdPromotion(transport, resource_id=101, user_id=7)
    bbip = BbipPromotion(transport, resource_id=101)
    trx = TrxPromotion(transport, resource_id=101)
    pricing = TargetActionPricing(transport, resource_id=101)

    vas_preview = ad_promotion.apply_vas(codes=["xl"], dry_run=True)
    package_preview = ad_promotion.apply_vas_package(package_code="turbo", dry_run=True)
    vas_v2_preview = ad_promotion.apply_vas_v2(codes=["highlight"], dry_run=True)
    bbip_preview = bbip.create_order(
        items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)],
        dry_run=True,
    )
    trx_apply_preview = trx.apply(
        items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")],
        dry_run=True,
    )
    trx_delete_preview = trx.delete(dry_run=True)
    auto_preview = pricing.update_auto(
        action_type_id=5,
        budget_penny=8000,
        budget_type="7d",
        dry_run=True,
    )
    manual_preview = pricing.update_manual(
        action_type_id=5,
        bid_penny=1500,
        limit_penny=15000,
        dry_run=True,
    )
    delete_preview = pricing.delete(dry_run=True)

    vas_apply = ad_promotion.apply_vas(codes=["xl"])
    package_apply = ad_promotion.apply_vas_package(package_code="turbo")
    vas_v2_apply = ad_promotion.apply_vas_v2(codes=["highlight"])
    bbip_apply = bbip.create_order(
        items=[BbipOrderItem(item_id=101, duration=7, price=1000, old_price=1200)]
    )
    trx_apply = trx.apply(
        items=[TrxPromotionApplyItem(item_id=101, commission=1500, date_from="2026-04-18")]
    )
    trx_delete = trx.delete()
    auto_apply = pricing.update_auto(action_type_id=5, budget_penny=8000, budget_type="7d")
    manual_apply = pricing.update_manual(action_type_id=5, bid_penny=1500, limit_penny=15000)
    delete_apply = pricing.delete()

    assert seen == [
        ("/core/v1/accounts/7/items/101/vas", vas_preview.request_payload),
        ("/core/v2/accounts/7/items/101/vas_packages", package_preview.request_payload),
        ("/core/v2/items/101/vas/", vas_v2_preview.request_payload),
        ("/promotion/v1/items/services/bbip/orders/create", bbip_preview.request_payload),
        ("/trx-promo/1/apply", trx_apply_preview.request_payload),
        ("/trx-promo/1/cancel", trx_delete_preview.request_payload),
        ("/cpxpromo/1/setAuto", auto_preview.request_payload),
        ("/cpxpromo/1/setManual", manual_preview.request_payload),
        ("/cpxpromo/1/remove", delete_preview.request_payload),
    ]
    assert vas_apply.request_payload == vas_preview.request_payload
    assert package_apply.request_payload == package_preview.request_payload
    assert vas_v2_apply.request_payload == vas_v2_preview.request_payload
    assert bbip_apply.request_payload == bbip_preview.request_payload
    assert trx_apply.request_payload == trx_apply_preview.request_payload
    assert trx_delete.request_payload == trx_delete_preview.request_payload
    assert auto_apply.request_payload == auto_preview.request_payload
    assert manual_apply.request_payload == manual_preview.request_payload
    assert delete_apply.request_payload == delete_preview.request_payload
    assert bbip_apply.upstream_reference == "ord-1"
    assert vas_apply.status == "applied"
    assert auto_apply.status == "auto"
    assert bbip_apply.to_dict() == {
        "action": "create_order",
        "target": {"item_ids": [101]},
        "status": "created",
        "applied": True,
        "request_payload": {
            "items": [{"itemId": 101, "duration": 7, "price": 1000, "oldPrice": 1200}]
        },
        "warnings": [],
        "upstream_reference": "ord-1",
        "details": {
            "items": [
                {"item_id": 101, "success": True, "status": "created", "message": None}
            ]
        },
    }


@pytest.mark.parametrize(
    ("call", "expected"),
    [
        (lambda resource: resource.apply_vas(codes=[], dry_run=True), "`codes` must contain at least one item."),
        (
            lambda resource: resource.apply_vas_package(package_code="   ", dry_run=True),
            "`package_code` must be a non-empty string.",
        ),
        (
            lambda resource: resource.apply_vas(codes=["ok", "   "], dry_run=True),
            r"`codes\[1\]` must be a non-empty string.",
        ),
        (
            lambda resource: resource.update_auto(
                action_type_id=5,
                budget_penny=8000,
                budget_type="   ",
                dry_run=True,
            ),
            "`budget_type` must be a non-empty string.",
        ),
    ],
)
def test_write_validation_happens_before_transport(
    call: Callable[[AdPromotion | TargetActionPricing], object],
    expected: str,
) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise AssertionError("validation must fail before transport")

    transport = make_transport(httpx.MockTransport(handler))
    resource = AdPromotion(transport, resource_id=101, user_id=7)
    if "budget_type" in expected:
        resource = TargetActionPricing(transport, resource_id=101)

    with pytest.raises(ValidationError, match=expected):
        call(resource)

    assert calls == []


@pytest.mark.parametrize(
    ("call", "expected"),
    [
        (
            lambda resource: resource.create_order(
                items=[BbipOrderItem(item_id=0, duration=7, price=1000, old_price=1200)],
                dry_run=True,
            ),
            r"`items\[0\]\.item_id` must be a positive integer.",
        ),
        (
            lambda resource: resource.create_order(
                items=[BbipOrderItem(item_id=101, duration=0, price=1000, old_price=1200)],
                dry_run=True,
            ),
            r"`items\[0\]\.duration` must be a positive integer.",
        ),
        (
            lambda resource: resource.apply(
                items=[TrxPromotionApplyItem(item_id=101, commission=0, date_from="2026-04-18")],
                dry_run=True,
            ),
            r"`items\[0\]\.commission` must be a positive integer.",
        ),
        (
            lambda resource: resource.apply(
                items=[TrxPromotionApplyItem(item_id=101, commission=100, date_from="   ")],
                dry_run=True,
            ),
            r"`items\[0\]\.date_from` must be a non-empty string.",
        ),
    ],
)
def test_nested_write_validation_happens_before_transport(
    call: Callable[[BbipPromotion | TrxPromotion], object],
    expected: str,
) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        raise AssertionError("validation must fail before transport")

    transport = make_transport(httpx.MockTransport(handler))
    resource: BbipPromotion | TrxPromotion
    if "date_from" in expected or "commission" in expected:
        resource = TrxPromotion(transport, resource_id=101)
    else:
        resource = BbipPromotion(transport, resource_id=101)

    with pytest.raises(ValidationError, match=expected):
        call(resource)

    assert calls == []


def test_write_upstream_validation_error_is_mapped_to_sdk_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/cpxpromo/1/setManual"
        return httpx.Response(422, json={"message": "invalid bid"})

    transport = make_transport(httpx.MockTransport(handler))
    pricing = TargetActionPricing(transport, resource_id=101)

    with pytest.raises(ValidationError, match="invalid bid"):
        pricing.update_manual(action_type_id=5, bid_penny=1500, limit_penny=15000)
