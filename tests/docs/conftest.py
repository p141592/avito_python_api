from __future__ import annotations

from collections.abc import Iterator

import pytest

from avito import AvitoClient
from avito.testing import FakeResponse, FakeTransport


def build_docs_client() -> AvitoClient:
    fake = FakeTransport()
    fake.add_json(
        "GET",
        "/core/v1/accounts/self",
        {"id": 7, "name": "Иван", "email": "user@example.com", "phone": "+7999"},
    )
    fake.add_json(
        "GET",
        "/core/v1/accounts/7/balance/",
        {"user_id": 7, "balance": {"real": 1500.0, "bonus": 250.0, "currency": "RUB"}},
    )
    fake.add_json(
        "POST",
        "/core/v1/accounts/operations_history/",
        {
            "total": 1,
            "operations": [
                {
                    "id": "op-1",
                    "created_at": "2026-04-01T12:00:00Z",
                    "amount": -300.0,
                    "type": "payment",
                    "status": "done",
                    "description": "Оплата продвижения",
                }
            ],
        },
    )
    fake.add_json(
        "GET",
        "/checkAhUserV1",
        {"user_id": 7, "is_active": True, "role": "manager"},
    )
    fake.add_json(
        "GET",
        "/getEmployeesV1",
        {
            "employees": [
                {"employee_id": 10, "user_id": 7, "name": "Пётр", "email": "petr@example.com"}
            ],
            "total": 1,
        },
    )
    fake.add_json(
        "GET",
        "/listCompanyPhonesV1",
        {"phones": [{"id": 1, "phone": "+7000", "comment": "Основной"}]},
    )
    fake.add_json(
        "POST",
        "/listItemsByEmployeeIdV1",
        {
            "items": [{"item_id": 101, "title": "Диван", "status": "active", "price": 9900}],
            "total": 1,
        },
    )
    fake.add_json(
        "POST",
        "/linkItemsV1",
        {"success": True, "message": "linked"},
    )
    fake.add_json(
        "GET",
        "/core/v1/items",
        {
            "items": [
                {
                    "id": 101,
                    "user_id": 7,
                    "title": "Диван",
                    "description": "Угловой диван",
                    "status": "active",
                    "price": 9900,
                    "url": "https://www.avito.ru/items/101",
                },
                {
                    "id": 102,
                    "user_id": 7,
                    "title": "Кресло",
                    "status": "active",
                    "price": 3500,
                },
            ],
            "total": 2,
        },
    )
    fake.add_json(
        "GET",
        "/core/v1/accounts/7/items/101/",
        {
            "id": 101,
            "user_id": 7,
            "title": "Диван",
            "description": "Угловой диван",
            "status": "active",
            "price": 9900,
            "url": "https://www.avito.ru/items/101",
        },
    )
    fake.add_json(
        "POST",
        "/stats/v1/accounts/7/items",
        {"items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}]},
    )
    fake.add_json(
        "POST",
        "/stats/v2/accounts/7/items",
        {
            "period": "day",
            "items": [{"item_id": 101, "views": 45, "contacts": 5, "favorites": 2}],
        },
    )
    fake.add_json(
        "POST",
        "/core/v1/accounts/7/calls/stats/",
        {"items": [{"item_id": 101, "calls": 3, "answered_calls": 2, "missed_calls": 1}]},
    )
    fake.add_json(
        "POST",
        "/stats/v2/accounts/7/spendings",
        {"items": [{"item_id": 101, "amount": 77.5, "service": "xl"}], "total": 77.5},
    )
    fake.add_json(
        "POST",
        "/core/v1/accounts/7/vas/prices",
        {"items": [{"code": "xl", "title": "XL", "price": 500, "is_available": True}]},
    )
    fake.add_json(
        "POST",
        "/core/v1/items/101/update_price",
        {"item_id": 101, "price": 10900, "status": "updated"},
    )
    fake.add_json(
        "GET",
        "/messenger/v2/accounts/7/chats",
        {
            "chats": [
                {
                    "id": "chat-1",
                    "user_id": 7,
                    "title": "Покупатель",
                    "unread_count": 1,
                    "last_message": {"text": "Здравствуйте"},
                }
            ],
            "total": 1,
        },
    )
    fake.add_json(
        "GET",
        "/messenger/v2/accounts/7/chats/chat-1",
        {
            "id": "chat-1",
            "user_id": 7,
            "title": "Покупатель",
            "unread_count": 1,
            "last_message": {"text": "Здравствуйте"},
        },
    )
    fake.add_json(
        "GET",
        "/messenger/v3/accounts/7/chats/chat-1/messages/",
        {
            "messages": [
                {
                    "id": "msg-0",
                    "chat_id": "chat-1",
                    "author_id": 100,
                    "text": "Здравствуйте",
                    "created_at": "2026-04-23T10:00:00Z",
                    "direction": "in",
                    "type": "text",
                }
            ],
            "total": 1,
        },
    )
    fake.add_json(
        "POST",
        "/messenger/v1/accounts/7/chats/chat-1/messages",
        {"success": True, "message_id": "msg-1", "status": "sent"},
    )
    fake.add_json(
        "POST",
        "/messenger/v1/accounts/7/uploadImages",
        {"images": [{"image_id": "img-1", "url": "https://cdn.example/img-1.jpg"}]},
    )
    fake.add_json(
        "POST",
        "/messenger/v1/accounts/7/chats/chat-1/messages/image",
        {"success": True, "message_id": "msg-img-1", "status": "sent"},
    )
    fake.add_json(
        "POST",
        "/messenger/v1/accounts/7/chats/chat-1/read",
        {"success": True, "status": "read"},
    )
    fake.add_json(
        "GET",
        "/order-management/1/orders",
        {
            "orders": [
                {
                    "id": "ord-1",
                    "status": "new",
                    "created": "2026-04-23T09:00:00Z",
                    "buyerInfo": {"fullName": "Иван"},
                    "totalPrice": 9900,
                }
            ],
            "total": 1,
        },
    )
    fake.add_json(
        "POST",
        "/order-management/1/order/applyTransition",
        {"result": {"success": True, "orderId": "ord-1", "status": "confirmed"}},
    )
    fake.add_json(
        "POST",
        "/order-management/1/markings",
        {"result": {"success": True, "orderId": "ord-1", "status": "marked"}},
    )
    fake.add_json(
        "POST",
        "/order-management/1/orders/labels",
        {"result": {"taskId": 42, "status": "created"}},
    )
    fake.add(
        "GET",
        "/order-management/1/orders/labels/42/download",
        FakeResponse(
            200,
            content=b"%PDF-1.4 docs-label",
            headers={
                "content-type": "application/pdf",
                "content-disposition": 'attachment; filename="label-42.pdf"',
            },
        ),
    )
    fake.add_json(
        "POST",
        "/createAnnouncement",
        {"data": {"taskId": 11, "status": "announcement-created"}},
    )
    fake.add_json(
        "POST",
        "/createParcel",
        {"data": {"parcelId": "par-1", "status": "parcel-created"}},
    )
    fake.add_json(
        "GET",
        "/delivery-sandbox/tasks/11",
        {"data": {"taskId": 11, "status": "done"}},
    )
    fake.add_json(
        "POST",
        "/stock-management/1/info",
        {
            "stocks": [
                {
                    "item_id": 101,
                    "quantity": 5,
                    "is_multiple": True,
                    "is_unlimited": False,
                    "is_out_of_stock": False,
                }
            ]
        },
    )
    fake.add_json(
        "PUT",
        "/stock-management/1/stocks",
        {"stocks": [{"item_id": 101, "external_id": "SKU-101", "success": True, "errors": []}]},
    )
    fake.add_json(
        "GET",
        "/job/v1/applications/get_ids",
        {
            "items": [{"id": "app-1", "updatedAt": "2026-04-23T10:00:00+03:00"}],
            "cursor": "app-1",
        },
    )
    fake.add_json(
        "POST",
        "/job/v1/applications/get_by_ids",
        {
            "applies": [
                {
                    "id": "app-1",
                    "vacancy_id": 101,
                    "resume_id": "res-1",
                    "state": "new",
                    "is_viewed": False,
                    "applicant": {"name": "Иван"},
                }
            ]
        },
    )
    fake.add_json(
        "GET",
        "/job/v1/applications/get_states",
        {"states": [{"slug": "new", "description": "Новый отклик"}]},
    )
    fake.add_json(
        "POST",
        "/job/v1/applications/set_is_viewed",
        {"ok": True, "status": "viewed"},
    )
    fake.add_json(
        "POST",
        "/job/v1/applications/apply_actions",
        {"ok": True, "status": "invited"},
    )
    fake.add_json(
        "GET",
        "/job/v2/vacancies",
        {"vacancies": [{"id": 101, "uuid": "vac-uuid-1", "title": "Продавец", "status": "active"}], "total": 1},
    )
    fake.add_json(
        "GET",
        "/job/v2/vacancies/101",
        {
            "id": 101,
            "uuid": "vac-uuid-1",
            "title": "Продавец",
            "status": "active",
            "url": "https://avito.ru/vacancy/101",
        },
    )
    fake.add_json(
        "GET",
        "/job/v1/resumes/",
        {
            "meta": {"cursor": "2", "total": 1},
            "resumes": [
                {
                    "id": "res-1",
                    "title": "Оператор call-центра",
                    "name": "Пётр",
                    "location": "Москва",
                    "salary": 90000,
                }
            ],
        },
    )
    fake.add_json(
        "GET",
        "/job/v2/resumes/res-1",
        {
            "id": "res-1",
            "title": "Оператор call-центра",
            "fullName": "Пётр Петров",
            "address_details": {"location": "Москва"},
            "salary": {"from": 90000},
        },
    )
    fake.add_json(
        "GET",
        "/job/v1/resumes/res-1/contacts/",
        {"name": "Пётр", "phone": "+79990000000", "email": "petr@example.com"},
    )
    fake.add_json(
        "GET",
        "/job/v1/applications/webhook",
        {"url": "https://example.com/job", "is_active": True, "version": "v1"},
    )
    fake.add_json(
        "PUT",
        "/job/v1/applications/webhook",
        {"url": "https://example.com/job", "is_active": True, "version": "v1"},
    )
    fake.add_json(
        "GET",
        "/job/v2/vacancy/dict",
        [{"id": "profession", "description": "Профессия"}],
    )
    fake.add_json(
        "GET",
        "/job/v2/vacancy/dict/profession",
        [{"id": 10106, "name": "IT, интернет, телеком", "deprecated": False}],
    )
    fake.add_json(
        "GET",
        "/ratings/v1/info",
        {
            "isEnabled": True,
            "rating": {"score": 4.7, "reviewsCount": 25, "reviewsWithScoreCount": 20},
        },
    )
    fake.add_json(
        "GET",
        "/ratings/v1/reviews",
        {
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
    fake.add_json(
        "POST",
        "/ratings/v1/answers",
        {"id": 456, "createdAt": 1713427200},
    )
    fake.add_json(
        "DELETE",
        "/ratings/v1/answers/456",
        {"success": True},
    )
    fake.add_json(
        "GET",
        "/tariff/info/1",
        {
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
    return fake.as_client(user_id=7)


@pytest.fixture(autouse=True)
def docs_client_from_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("AVITO_CLIENT_ID", "docs-client-id")
    monkeypatch.setenv("AVITO_CLIENT_SECRET", "docs-client-secret")

    def from_env(
        cls: type[AvitoClient],
        *,
        env_file: str | None = ".env",
    ) -> AvitoClient:
        _ = cls
        _ = env_file
        return build_docs_client()

    monkeypatch.setattr(AvitoClient, "from_env", classmethod(from_env))
    yield
