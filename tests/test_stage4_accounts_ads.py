from __future__ import annotations

import json

import httpx

from avito.accounts import Account, AccountHierarchy
from avito.ads import Ad, AdPromotion, AdStats, AutoloadLegacy, AutoloadProfile, AutoloadReport
from avito.auth import AuthSettings
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


def test_accounts_domain_maps_profile_balance_and_operations() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/core/v1/accounts/self":
            return httpx.Response(
                200, json={"id": 7, "name": "Иван", "email": "user@example.com", "phone": "+7999"}
            )
        if request.url.path == "/core/v1/accounts/7/balance/":
            return httpx.Response(
                200,
                json={"user_id": 7, "balance": {"real": 150.5, "bonus": 20.0, "currency": "RUB"}},
            )
        assert request.url.path == "/core/v1/accounts/operations_history/"
        assert json.loads(request.content.decode()) == {"dateFrom": "2025-01-01", "limit": 2}
        return httpx.Response(
            200,
            json={
                "total": 1,
                "operations": [
                    {
                        "id": "op-1",
                        "created_at": "2025-01-02T12:00:00Z",
                        "amount": 120.0,
                        "type": "payment",
                        "status": "done",
                    }
                ],
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    account = Account(transport, resource_id=7, user_id=7)

    profile = account.get_self()
    balance = account.get_balance()
    history = account.get_operations_history(date_from="2025-01-01", limit=2)

    assert profile.id == 7
    assert balance.total == 170.5
    assert history.total == 1
    assert history.operations[0].operation_type == "payment"


def test_account_hierarchy_domain_maps_employees_phones_and_items() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/checkAhUserV1":
            return httpx.Response(200, json={"user_id": 7, "is_active": True, "role": "manager"})
        if request.url.path == "/getEmployeesV1":
            return httpx.Response(
                200,
                json={"employees": [{"employee_id": 10, "user_id": 7, "name": "Пётр"}], "total": 1},
            )
        if request.url.path == "/listCompanyPhonesV1":
            return httpx.Response(
                200, json={"phones": [{"id": 1, "phone": "+7000", "comment": "Основной"}]}
            )
        if request.url.path == "/linkItemsV1":
            assert json.loads(request.content.decode()) == {"employeeId": 10, "itemIds": [1, 2]}
            return httpx.Response(200, json={"success": True, "message": "linked"})
        assert request.url.path == "/listItemsByEmployeeIdV1"
        assert json.loads(request.content.decode()) == {"employeeId": 10, "limit": 5}
        return httpx.Response(
            200,
            json={
                "items": [{"item_id": 1, "title": "Объявление", "status": "active", "price": 99}],
                "total": 1,
            },
        )

    hierarchy = AccountHierarchy(
        make_transport(httpx.MockTransport(handler)), resource_id=7, user_id=7
    )

    status = hierarchy.get_status()
    employees = hierarchy.list_employees()
    phones = hierarchy.list_company_phones()
    linked = hierarchy.link_items(employee_id=10, item_ids=[1, 2])
    items = hierarchy.list_items_by_employee(employee_id=10, limit=5)

    assert status.is_active is True
    assert employees.items[0].employee_id == 10
    assert phones.items[0].phone == "+7000"
    assert linked.success is True
    assert items.items[0].title == "Объявление"


def test_ads_list_uses_lazy_pagination_with_list_like_items() -> None:
    seen_offsets: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/core/v1/items"
        assert request.url.params["user_id"] == "7"
        assert request.url.params["status"] == "active"
        assert request.url.params["limit"] == "2"

        offset = request.url.params["offset"]
        seen_offsets.append(offset)
        page_items = {
            "0": [{"id": 101, "title": "Смартфон"}, {"id": 102, "title": "Ноутбук"}],
            "2": [{"id": 103, "title": "Планшет"}, {"id": 104, "title": "Наушники"}],
            "4": [{"id": 105, "title": "Камера"}],
        }
        return httpx.Response(200, json={"items": page_items[offset], "total": 5})

    transport = make_transport(httpx.MockTransport(handler))
    ad = Ad(transport, user_id=7)

    items = ad.list(status="active", limit=2)

    assert seen_offsets == ["0"]
    assert items.items.loaded_count == 2
    assert items.items.is_materialized is False
    assert items.items[0].id == 101
    assert seen_offsets == ["0"]
    assert items.items[3].id == 104
    assert seen_offsets == ["0", "2"]
    assert items.items[1].id == 102
    assert seen_offsets == ["0", "2"]
    assert [item.title for item in items.items[:3]] == ["Смартфон", "Ноутбук", "Планшет"]
    assert seen_offsets == ["0", "2"]
    assert items.items.loaded_count == 4
    assert items.items.is_materialized is False
    assert [item.title for item in items.items.materialize()] == [
        "Смартфон",
        "Ноутбук",
        "Планшет",
        "Наушники",
        "Камера",
    ]
    assert len(items.items) == 5
    assert [item.title for item in items.items] == [
        "Смартфон",
        "Ноутбук",
        "Планшет",
        "Наушники",
        "Камера",
    ]
    assert items.items.is_materialized is True
    assert seen_offsets == ["0", "2", "4"]


def test_ads_domain_covers_item_stats_spendings_and_promotion() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/core/v1/accounts/7/items/101/":
            return httpx.Response(
                200,
                json={
                    "id": 101,
                    "user_id": 7,
                    "title": "Смартфон",
                    "price": 1000,
                    "status": "active",
                },
            )
        if request.url.path == "/core/v1/items":
            assert request.url.params["user_id"] == "7"
            assert request.url.params["status"] == "active"
            return httpx.Response(
                200, json={"items": [{"id": 101, "title": "Смартфон"}], "total": 1}
            )
        if request.url.path == "/core/v1/items/101/update_price":
            assert json.loads(request.content.decode()) == {"price": 1500}
            return httpx.Response(200, json={"item_id": 101, "price": 1500, "status": "updated"})
        if request.url.path == "/stats/v1/accounts/7/items":
            body = json.loads(request.content.decode())
            assert body["itemIds"] == [101]
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]}
            )
        if request.url.path == "/core/v1/accounts/7/calls/stats/":
            return httpx.Response(
                200,
                json={
                    "items": [{"item_id": 101, "calls": 3, "answered_calls": 2, "missed_calls": 1}]
                },
            )
        if request.url.path == "/stats/v2/accounts/7/items":
            return httpx.Response(
                200, json={"period": "month", "items": [{"item_id": 101, "views": 100}]}
            )
        if request.url.path == "/stats/v2/accounts/7/spendings":
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "amount": 77.5, "service": "xl"}]}
            )
        if request.url.path == "/core/v1/accounts/7/vas/prices":
            assert json.loads(request.content.decode()) == {"itemIds": [101], "locationId": 213}
            return httpx.Response(
                200,
                json={"services": [{"code": "xl", "title": "XL", "price": 50, "available": True}]},
            )
        if request.url.path == "/core/v1/accounts/7/items/101/vas":
            assert json.loads(request.content.decode()) == {"codes": ["xl"]}
            return httpx.Response(200, json={"success": True, "status": "applied"})
        if request.url.path == "/core/v2/accounts/7/items/101/vas_packages":
            assert json.loads(request.content.decode()) == {"packageCode": "turbo"}
            return httpx.Response(200, json={"success": True, "status": "package_applied"})
        assert request.url.path == "/core/v2/items/101/vas/"
        assert json.loads(request.content.decode()) == {"codes": ["highlight"]}
        return httpx.Response(200, json={"success": True, "status": "v2_applied"})

    transport = make_transport(httpx.MockTransport(handler))
    ad = Ad(transport, resource_id=101, user_id=7)
    stats = AdStats(transport, resource_id=101, user_id=7)
    promotion = AdPromotion(transport, resource_id=101, user_id=7)

    item = ad.get()
    items = ad.list(status="active")
    price = ad.update_price(price=1500)
    item_stats = ad.get_stats()
    calls = stats.get_calls_stats()
    analytics = stats.get_item_analytics()
    spendings = stats.get_account_spendings()
    vas_prices = promotion.get_vas_prices(item_ids=[101], location_id=213)
    vas_apply = promotion.apply_vas(codes=["xl"])
    package_apply = promotion.apply_vas_package(package_code="turbo")
    vas_v2_apply = promotion.apply_vas_v2(codes=["highlight"])

    assert item.title == "Смартфон"
    assert items.total == 1
    assert price.price == 1500
    assert item_stats.items[0].views == 45
    assert calls.items[0].answered_calls == 2
    assert analytics.period == "month"
    assert spendings.total == 77.5
    assert vas_prices.items[0].code == "xl"
    assert vas_apply.applied is True
    assert package_apply.status == "package_applied"
    assert vas_v2_apply.status == "v2_applied"


def test_autoload_domains_cover_profile_report_and_legacy_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/autoload/v2/profile" and request.method == "GET":
            return httpx.Response(
                200, json={"user_id": 7, "is_enabled": True, "upload_url": "https://upload"}
            )
        if path == "/autoload/v2/profile" and request.method == "POST":
            assert json.loads(request.content.decode()) == {
                "isEnabled": True,
                "email": "feed@example.com",
            }
            return httpx.Response(200, json={"success": True, "message": "saved"})
        if path == "/autoload/v1/upload":
            assert json.loads(request.content.decode()) == {"url": "https://example.com/feed.xml"}
            return httpx.Response(200, json={"success": True, "report_id": 501})
        if path == "/autoload/v1/user-docs/tree":
            return httpx.Response(
                200, json={"tree": [{"slug": "transport", "title": "Транспорт", "children": []}]}
            )
        if path == "/autoload/v1/user-docs/node/cars/fields":
            return httpx.Response(
                200,
                json={
                    "fields": [
                        {"slug": "brand", "title": "Марка", "type": "string", "required": True}
                    ]
                },
            )
        if path == "/autoload/v2/reports":
            return httpx.Response(
                200, json={"reports": [{"report_id": 501, "status": "done"}], "total": 1}
            )
        if path == "/autoload/v3/reports/501":
            return httpx.Response(
                200,
                json={"report_id": 501, "status": "done", "errors_count": 0, "warnings_count": 1},
            )
        if path == "/autoload/v3/reports/last_completed_report":
            return httpx.Response(200, json={"report_id": 500, "status": "done"})
        if path == "/autoload/v2/reports/501/items":
            return httpx.Response(
                200,
                json={
                    "items": [
                        {"item_id": 101, "avito_id": 9001, "status": "active", "title": "Авто"}
                    ],
                    "total": 1,
                },
            )
        if path == "/autoload/v2/reports/501/items/fees":
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "amount": 42.0, "service": "xl"}]}
            )
        if path == "/autoload/v2/items/ad_ids":
            assert request.url.params["avito_ids"] == "9001,9002"
            return httpx.Response(200, json={"mappings": [{"ad_id": 1, "avito_id": 9001}]})
        if path == "/autoload/v2/items/avito_ids":
            assert request.url.params["ad_ids"] == "1,2"
            return httpx.Response(200, json={"mappings": [{"ad_id": 1, "avito_id": 9001}]})
        if path == "/autoload/v2/reports/items":
            assert request.url.params["item_ids"] == "101"
            return httpx.Response(
                200, json={"items": [{"item_id": 101, "avito_id": 9001, "status": "active"}]}
            )
        if path == "/autoload/v1/profile" and request.method == "GET":
            return httpx.Response(200, json={"user_id": 7, "is_enabled": False})
        if path == "/autoload/v1/profile" and request.method == "POST":
            return httpx.Response(200, json={"success": True, "message": "legacy_saved"})
        if path == "/autoload/v2/reports/last_completed_report":
            return httpx.Response(200, json={"report_id": 401, "status": "legacy_done"})
        assert path == "/autoload/v2/reports/401"
        return httpx.Response(200, json={"report_id": 401, "status": "legacy_done"})

    transport = make_transport(httpx.MockTransport(handler))
    profile = AutoloadProfile(transport)
    report = AutoloadReport(transport, resource_id=501)
    legacy = AutoloadLegacy(transport, resource_id=401)

    current_profile = profile.get()
    saved_profile = profile.save(is_enabled=True, email="feed@example.com")
    upload = profile.upload_by_url(url="https://example.com/feed.xml")
    tree = profile.get_tree()
    fields = profile.get_node_fields(node_slug="cars")
    reports = report.list()
    report_details = report.get()
    last_report = report.get_last_completed()
    report_items = report.get_items()
    report_fees = report.get_fees()
    ad_ids = report.get_ad_ids_by_avito_ids(avito_ids=[9001, 9002])
    avito_ids = report.get_avito_ids_by_ad_ids(ad_ids=[1, 2])
    items_info = report.get_items_info(item_ids=[101])
    legacy_profile = legacy.get_profile()
    legacy_saved = legacy.save_profile(email="legacy@example.com")
    legacy_last = legacy.get_last_completed_report()
    legacy_report = legacy.get_report()

    assert current_profile.is_enabled is True
    assert saved_profile.success is True
    assert upload.report_id == 501
    assert tree.items[0].slug == "transport"
    assert fields.items[0].required is True
    assert reports.total == 1
    assert report_details.warnings_count == 1
    assert last_report.report_id == 500
    assert report_items.items[0].avito_id == 9001
    assert report_fees.total == 42.0
    assert ad_ids.mappings[0] == (1, 9001)
    assert avito_ids.mappings[0] == (1, 9001)
    assert items_info.items[0].item_id == 101
    assert legacy_profile.is_enabled is False
    assert legacy_saved.message == "legacy_saved"
    assert legacy_last.status == "legacy_done"
    assert legacy_report.report_id == 401
