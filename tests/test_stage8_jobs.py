from __future__ import annotations

import json

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.jobs import Application, JobDictionary, JobWebhook, Resume, Vacancy
from avito.jobs.models import JobsQuery, JobsRequest


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


def test_applications_and_webhooks_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/job/v1/applications/get_ids":
            assert request.url.params["updatedAtFrom"] == "2026-04-18"
            return httpx.Response(
                200,
                json={
                    "items": [{"id": "app-1", "updatedAt": "2026-04-18T10:00:00+03:00"}],
                    "cursor": "app-1",
                },
            )
        if path == "/job/v1/applications/get_by_ids":
            assert json.loads(request.content.decode()) == {"ids": ["app-1"]}
            return httpx.Response(
                200,
                json={
                    "applies": [
                        {
                            "id": "app-1",
                            "vacancy_id": 101,
                            "state": "new",
                            "is_viewed": False,
                            "applicant": {"name": "Иван"},
                        }
                    ]
                },
            )
        if path == "/job/v1/applications/get_states":
            return httpx.Response(
                200, json={"states": [{"slug": "new", "description": "Новый отклик"}]}
            )
        if path == "/job/v1/applications/set_is_viewed":
            assert json.loads(request.content.decode()) == {
                "applies": [{"id": "app-1", "is_viewed": True}]
            }
            return httpx.Response(200, json={"ok": True, "status": "viewed"})
        if path == "/job/v1/applications/apply_actions":
            assert json.loads(request.content.decode()) == {"ids": ["app-1"], "action": "invited"}
            return httpx.Response(200, json={"ok": True, "status": "invited"})
        if path == "/job/v1/applications/webhook" and request.method == "GET":
            return httpx.Response(
                200, json={"url": "https://example.com/job", "is_active": True, "version": "v1"}
            )
        if path == "/job/v1/applications/webhook" and request.method == "PUT":
            assert json.loads(request.content.decode()) == {"url": "https://example.com/job"}
            return httpx.Response(
                200, json={"url": "https://example.com/job", "is_active": True, "version": "v1"}
            )
        if path == "/job/v1/applications/webhook" and request.method == "DELETE":
            assert request.url.params["url"] == "https://example.com/job"
            return httpx.Response(200, json={"ok": True})
        assert path == "/job/v1/applications/webhooks"
        return httpx.Response(
            200, json=[{"url": "https://example.com/job", "is_active": True, "version": "v1"}]
        )

    transport = make_transport(httpx.MockTransport(handler))
    application = Application(transport, resource_id="app-1")
    webhook = JobWebhook(transport)

    ids = application.list(query=JobsQuery(params={"updatedAtFrom": "2026-04-18"}))
    applications = application.list(request=JobsRequest(payload={"ids": ["app-1"]}))
    states = application.get_states()
    viewed = application.update(request=JobsRequest(payload={"applies": [{"id": "app-1", "is_viewed": True}]}))
    applied = application.apply(request=JobsRequest(payload={"ids": ["app-1"], "action": "invited"}))
    current_hook = webhook.get()
    updated_hook = webhook.update(request=JobsRequest(payload={"url": "https://example.com/job"}))
    deleted_hook = webhook.delete(url="https://example.com/job")
    hooks = webhook.list()

    assert ids.items[0].id == "app-1"
    assert applications.items[0].applicant_name == "Иван"
    assert states.items[0].slug == "new"
    assert viewed.status == "viewed"
    assert applied.status == "invited"
    assert current_hook.url == "https://example.com/job"
    assert updated_hook.is_active is True
    assert deleted_hook.success is True
    assert hooks.items[0].version == "v1"


def test_resume_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/job/v1/resumes/":
            assert request.url.params["query"] == "оператор"
            return httpx.Response(
                200,
                json={
                    "meta": {"cursor": "2", "total": 1},
                    "resumes": [
                        {
                            "id": "res-1",
                            "title": "Оператор call-центра",
                            "name": "Петр",
                            "location": "Москва",
                            "salary": 90000,
                        }
                    ],
                },
            )
        if request.url.path == "/job/v1/resumes/res-1/contacts/":
            return httpx.Response(
                200, json={"name": "Петр", "phone": "+79990000000", "email": "petr@example.com"}
            )
        assert request.url.path == "/job/v2/resumes/res-1"
        return httpx.Response(
            200,
            json={
                "id": "res-1",
                "title": "Оператор call-центра",
                "fullName": "Петр Петров",
                "address_details": {"location": "Москва"},
                "salary": {"from": 90000},
            },
        )

    resume = Resume(make_transport(httpx.MockTransport(handler)), resource_id="res-1")

    results = resume.list(query=JobsQuery(params={"query": "оператор"}))
    contacts = resume.get_contacts()
    item = resume.get()

    assert results.cursor == "2"
    assert results.items[0].candidate_name == "Петр"
    assert contacts.phone == "+79990000000"
    assert item.location == "Москва"


def test_vacancy_v1_v2_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/job/v1/vacancies":
            assert json.loads(request.content.decode()) == {"title": "Продавец"}
            return httpx.Response(201, json={"id": 101, "status": "created"})
        if path == "/job/v1/vacancies/101":
            assert request.method == "PUT"
            assert json.loads(request.content.decode()) == {"title": "Старший продавец"}
            return httpx.Response(200, json={"ok": True, "status": "updated"})
        if path == "/job/v1/vacancies/archived/101":
            assert json.loads(request.content.decode()) == {"employee_id": 7}
            return httpx.Response(200, json={"ok": True, "status": "archived"})
        if path == "/job/v1/vacancies/101/prolongate":
            assert json.loads(request.content.decode()) == {"billing_type": "package"}
            return httpx.Response(200, json={"ok": True, "status": "prolongated"})
        if path == "/job/v2/vacancies":
            if request.method == "GET":
                return httpx.Response(
                    200,
                    json={
                        "vacancies": [
                            {
                                "id": 101,
                                "uuid": "vac-uuid-1",
                                "title": "Продавец",
                                "status": "active",
                            }
                        ],
                        "total": 1,
                    },
                )
            assert json.loads(request.content.decode()) == {"title": "Вакансия v2"}
            return httpx.Response(202, json={"vacancy_uuid": "vac-uuid-1", "status": "created"})
        if path == "/job/v2/vacancies/batch":
            assert json.loads(request.content.decode()) == {"ids": [101]}
            return httpx.Response(
                200,
                json={
                    "vacancies": [
                        {"id": 101, "uuid": "vac-uuid-1", "title": "Продавец", "status": "active"}
                    ]
                },
            )
        if path == "/job/v2/vacancies/statuses":
            assert json.loads(request.content.decode()) == {"ids": [101]}
            return httpx.Response(
                200, json={"items": [{"id": 101, "uuid": "vac-uuid-1", "status": "active"}]}
            )
        if path == "/job/v2/vacancies/update/vac-uuid-1":
            assert json.loads(request.content.decode()) == {"title": "Вакансия v2 updated"}
            return httpx.Response(202, json={"vacancy_uuid": "vac-uuid-1", "status": "updated"})
        if path == "/job/v2/vacancies/101":
            return httpx.Response(
                200,
                json={
                    "id": 101,
                    "uuid": "vac-uuid-1",
                    "title": "Продавец",
                    "status": "active",
                    "url": "https://avito.ru/vacancy/101",
                },
            )
        assert path == "/job/v2/vacancies/vac-uuid-1/auto_renewal"
        assert json.loads(request.content.decode()) == {"auto_renewal": True}
        return httpx.Response(200, json={"ok": True, "status": "auto-renewal-updated"})

    vacancy = Vacancy(make_transport(httpx.MockTransport(handler)), resource_id="101")

    created_v1 = vacancy.create(request=JobsRequest(payload={"title": "Продавец"}), version=1)
    updated_v1 = vacancy.update(
        request=JobsRequest(payload={"title": "Старший продавец"}),
        version=1,
    )
    archived_v1 = vacancy.delete(request=JobsRequest(payload={"employee_id": 7}))
    prolonged_v1 = vacancy.prolongate(request=JobsRequest(payload={"billing_type": "package"}))
    list_v2 = vacancy.list()
    created_v2 = vacancy.create(request=JobsRequest(payload={"title": "Вакансия v2"}))
    batch_v2 = vacancy.get_by_ids(request=JobsRequest(payload={"ids": [101]}))
    statuses_v2 = vacancy.get_statuses(request=JobsRequest(payload={"ids": [101]}))
    updated_v2 = vacancy.update(
        request=JobsRequest(payload={"title": "Вакансия v2 updated"}),
        version=2,
        vacancy_uuid="vac-uuid-1",
    )
    item_v2 = vacancy.get()
    auto_renewal = vacancy.update_auto_renewal(
        request=JobsRequest(payload={"auto_renewal": True}),
        vacancy_uuid="vac-uuid-1",
    )

    assert created_v1.id == "101"
    assert updated_v1.status == "updated"
    assert archived_v1.status == "archived"
    assert prolonged_v1.status == "prolongated"
    assert list_v2.items[0].uuid == "vac-uuid-1"
    assert created_v2.id == "vac-uuid-1"
    assert batch_v2.items[0].title == "Продавец"
    assert statuses_v2.items[0].status == "active"
    assert updated_v2.status == "updated"
    assert item_v2.url == "https://avito.ru/vacancy/101"
    assert auto_renewal.status == "auto-renewal-updated"


def test_job_dictionary_flows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/job/v2/vacancy/dict":
            return httpx.Response(200, json=[{"id": "profession", "description": "Профессия"}])
        assert request.url.path == "/job/v2/vacancy/dict/profession"
        return httpx.Response(
            200, json=[{"id": 10106, "name": "IT, интернет, телеком", "deprecated": True}]
        )

    dictionary = JobDictionary(
        make_transport(httpx.MockTransport(handler)), resource_id="profession"
    )

    dictionaries = dictionary.list()
    values = dictionary.get()

    assert dictionaries.items[0].id == "profession"
    assert values.items[0].deprecated is True
