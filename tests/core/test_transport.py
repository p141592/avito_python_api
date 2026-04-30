from __future__ import annotations

import random as random_module
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx
import pytest

from avito.auth import AccessToken, AuthProvider, AuthSettings
from avito.config import AvitoSettings
from avito.core import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    JsonPage,
    PaginatedList,
    Paginator,
    RateLimitError,
    RequestContext,
    ResponseMappingError,
    ServerError,
    Transport,
    UnsupportedOperationError,
    UpstreamApiError,
    ValidationError,
)
from avito.core.rate_limit import RateLimiter
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.testing import FakeTransport


def make_settings(
    *,
    retry_policy: RetryPolicy | None = None,
    timeouts: ApiTimeouts | None = None,
    user_agent_suffix: str | None = None,
) -> AvitoSettings:
    return AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(client_id="client-id", client_secret="client-secret"),
        user_agent_suffix=user_agent_suffix,
        retry_policy=retry_policy or RetryPolicy(),
        timeouts=timeouts or ApiTimeouts(),
    )


def test_transport_retries_timeout_and_returns_json() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ReadTimeout("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    payload = transport.request_json("GET", "/items", context=RequestContext("list_items"))

    assert payload == {"ok": True}
    assert calls["count"] == 2


def test_transport_sends_user_agent_on_every_request() -> None:
    fake_transport = FakeTransport()
    fake_transport.add_json("GET", "/items", {"ok": True})
    fake_transport.add_json("POST", "/items", {"created": True})
    transport = fake_transport.build()

    transport.request_json("GET", "/items", context=RequestContext("list_items"))
    transport.request_json(
        "POST",
        "/items",
        context=RequestContext("create_item", allow_retry=True),
        json_body={"name": "item"},
    )

    assert len(fake_transport.requests) == 2
    for request in fake_transport.requests:
        user_agent = request.headers.get("user-agent")
        assert user_agent is not None
        assert user_agent.startswith("avito-py/")
        assert "python/" in user_agent
        assert "httpx/" in user_agent


def test_transport_appends_user_agent_suffix() -> None:
    fake_transport = FakeTransport()
    fake_transport.add_json("GET", "/items", {"ok": True})
    transport = Transport(
        make_settings(user_agent_suffix="ci/transport-tests"),
        client=httpx.Client(
            transport=httpx.MockTransport(fake_transport._handle),
            base_url=fake_transport.base_url,
        ),
        sleep=lambda _: None,
    )

    transport.request_json("GET", "/items", context=RequestContext("list_items"))

    assert fake_transport.last(path="/items").headers["user-agent"].endswith("ci/transport-tests")


def test_transport_refreshes_token_after_401() -> None:
    issued_tokens: Iterator[AccessToken] = iter(
        (
            AccessToken("expired-token", datetime.now(UTC) + timedelta(minutes=5)),
            AccessToken("fresh-token", datetime.now(UTC) + timedelta(minutes=5)),
        )
    )
    auth_provider = AuthProvider(
        AuthSettings(client_id="client-id", client_secret="client-secret"),
        token_fetcher=lambda _: next(issued_tokens),
    )
    seen_authorization_headers: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        authorization = request.headers["Authorization"]
        seen_authorization_headers.append(authorization)
        if authorization == "Bearer expired-token":
            return httpx.Response(401, json={"message": "expired"})
        return httpx.Response(200, json={"ok": True})

    transport = Transport(
        make_settings(),
        auth_provider=auth_provider,
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    payload = transport.request_json("GET", "/secure", context=RequestContext("secure_call"))

    assert payload == {"ok": True}
    assert seen_authorization_headers == ["Bearer expired-token", "Bearer fresh-token"]


def test_retry_policy_uses_full_jitter_with_cap() -> None:
    policy = RetryPolicy(
        backoff_factor=2.0,
        max_delay=3.0,
        random_source=random_module.Random(7),
    )

    first_delay = policy.compute_backoff(3)
    second_delay = policy.compute_backoff(3)

    assert 0.0 <= first_delay <= 3.0
    assert 0.0 <= second_delay <= 3.0
    assert first_delay != second_delay


def test_rate_limiter_waits_before_bucket_overflow() -> None:
    now = {"value": 0.0}
    sleeps: list[float] = []

    def sleep(delay: float) -> None:
        sleeps.append(delay)
        now["value"] += delay

    limiter = RateLimiter(
        RetryPolicy(
            rate_limit_enabled=True,
            rate_limit_requests_per_second=2.0,
            rate_limit_burst=1,
        ),
        clock=lambda: now["value"],
        sleep=sleep,
    )

    assert limiter.acquire() == 0.0
    assert limiter.acquire() == pytest.approx(0.5)
    assert sleeps == [pytest.approx(0.5)]


def test_rate_limiter_uses_remaining_header_as_short_cooldown() -> None:
    now = {"value": 0.0}
    sleeps: list[float] = []

    def sleep(delay: float) -> None:
        sleeps.append(delay)
        now["value"] += delay

    limiter = RateLimiter(
        RetryPolicy(
            rate_limit_enabled=True,
            rate_limit_requests_per_second=4.0,
            rate_limit_burst=10,
        ),
        clock=lambda: now["value"],
        sleep=sleep,
    )

    limiter.observe_response(headers={"X-RateLimit-Remaining": "0"})

    assert limiter.acquire() == pytest.approx(0.25)
    assert sleeps == [pytest.approx(0.25)]


def test_transport_does_not_retry_non_idempotent_request_without_explicit_permission() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("offline", request=request)

    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(Exception, match="offline"):
        transport.request_json("POST", "/items", context=RequestContext("create_item"))

    assert calls["count"] == 1


def test_transport_retries_post_with_same_idempotency_key_for_whole_retry_chain() -> None:
    calls = {"count": 0}
    seen_keys: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        seen_keys.append(request.headers.get("Idempotency-Key"))
        if calls["count"] == 1:
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(200, json={"ok": True})

    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    payload = transport.request_json(
        "POST",
        "/items",
        context=RequestContext("create_item", allow_retry=True),
        json_body={"name": "item"},
        idempotency_key="idem-123",
    )

    assert payload == {"ok": True}
    assert calls["count"] == 2
    assert seen_keys == ["idem-123", "idem-123"]


def test_transport_does_not_retry_post_without_idempotency_key_even_with_allow_retry() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("offline", request=request)

    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(Exception, match="offline"):
        transport.request_json(
            "POST",
            "/items",
            context=RequestContext("create_item", allow_retry=True),
            json_body={"name": "item"},
        )

    assert calls["count"] == 1


@pytest.mark.parametrize(
    ("status_code", "error_cls"),
    (
        (400, ValidationError),
        (401, AuthenticationError),
        (403, AuthorizationError),
        (405, UnsupportedOperationError),
        (409, ConflictError),
        (418, UpstreamApiError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
    ),
)
def test_transport_maps_http_statuses_to_typed_sdk_errors(
    status_code: int, error_cls: type[Exception]
) -> None:
    transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status_code, json={"message": "boom"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(error_cls):
        transport.request_json("GET", "/broken", context=RequestContext("broken"))


def test_transport_exposes_structured_error_fields() -> None:
    transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    429,
                    json={
                        "message": "Слишком много запросов.",
                        "code": "rate_limit",
                        "details": {"limit": "minute"},
                    },
                    headers={"Retry-After": "15", "X-Request-Id": "req-123"},
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(RateLimitError) as error:
        transport.request_json("GET", "/limited", context=RequestContext("limited"))

    assert error.value.operation == "limited"
    assert error.value.status == 429
    assert error.value.error_code == "rate_limit"
    assert error.value.details == {"limit": "minute"}
    assert error.value.retry_after == 15
    assert error.value.request_id == "req-123"


def test_transport_preserves_retry_after_header_value() -> None:
    transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    429,
                    json={"message": "Слишком много запросов."},
                    headers={"Retry-After": "0.01"},
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(RateLimitError) as error:
        transport.request_json("GET", "/limited", context=RequestContext("limited"))

    assert error.value.retry_after == 0.01


def test_transport_parses_retry_after_http_date() -> None:
    retry_at = datetime.now(UTC) + timedelta(seconds=10)
    transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    429,
                    json={"message": "Слишком много запросов."},
                    headers={"Retry-After": format_datetime(retry_at, usegmt=True)},
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(RateLimitError) as error:
        transport.request_json("GET", "/limited", context=RequestContext("limited"))

    assert error.value.retry_after is not None
    assert 0 < error.value.retry_after <= 10


def test_transport_uses_half_second_retry_after_default_without_header() -> None:
    transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    429,
                    json={"message": "Слишком много запросов."},
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(RateLimitError) as error:
        transport.request_json("GET", "/limited", context=RequestContext("limited"))

    assert error.value.retry_after == 0.5


def test_transport_retries_rate_limit_without_retry_after_using_backoff() -> None:
    responses = iter(
        (
            httpx.Response(429, json={"message": "Слишком много запросов."}),
            httpx.Response(200, json={"ok": True}),
        )
    )
    sleeps: list[float] = []
    transport = Transport(
        make_settings(
            retry_policy=RetryPolicy(
                max_attempts=2,
                backoff_factor=1.0,
                random_source=random_module.Random(2),
            )
        ),
        client=httpx.Client(
            transport=httpx.MockTransport(lambda request: next(responses)),
            base_url="https://api.avito.ru",
        ),
        sleep=sleeps.append,
    )

    payload = transport.request_json("GET", "/limited", context=RequestContext("limited"))

    assert payload == {"ok": True}
    assert sleeps == [pytest.approx(random_module.Random(2).random())]


def test_transport_raises_mapping_error_for_invalid_json() -> None:
    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, text="not-json", headers={"content-type": "application/json"}
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(ResponseMappingError):
        transport.request_json("GET", "/broken", context=RequestContext("broken"))


def test_transport_supports_binary_download_and_multipart_upload() -> None:
    uploaded_content_types: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/upload":
            uploaded_content_types.append(request.headers["Content-Type"])
            return httpx.Response(200, json={"uploaded": True})
        return httpx.Response(
            200,
            content=b"%PDF-1.7",
            headers={
                "content-type": "application/pdf",
                "content-disposition": 'attachment; filename="label.pdf"',
            },
        )

    transport = Transport(
        make_settings(),
        client=httpx.Client(
            transport=httpx.MockTransport(handler), base_url="https://api.avito.ru"
        ),
        sleep=lambda _: None,
    )

    upload_result = transport.request_json(
        "POST",
        "/upload",
        context=RequestContext("upload_file", allow_retry=True),
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    binary_result = transport.download_binary("/download", context=RequestContext("download_file"))

    assert upload_result == {"uploaded": True}
    assert uploaded_content_types[0].startswith("multipart/form-data")
    assert binary_result.content == b"%PDF-1.7"
    assert binary_result.content_type == "application/pdf"
    assert binary_result.filename == "label.pdf"


def test_paginator_and_paginated_list_keep_lazy_contract() -> None:
    pages = {
        1: JsonPage(items=[1, 2], page=1, per_page=2, total=5),
        2: JsonPage(items=[3, 4], page=2, per_page=2, total=5),
        3: JsonPage(items=[5], page=3, per_page=2, total=5),
    }
    calls: list[int] = []

    paginator = Paginator(lambda page, cursor: pages[page or 1])
    assert paginator.collect() == [1, 2, 3, 4, 5]

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        return pages[resolved_page]

    items = PaginatedList(fetch, first_page=pages[1])

    assert items.loaded_count == 2
    assert items[0] == 1
    assert items[3] == 4
    assert calls == [2]
    assert list(item for _, item in zip(range(3), items, strict=False)) == [1, 2, 3]
    assert items.materialize() == [1, 2, 3, 4, 5]
    assert items.is_materialized is True


def test_paginated_list_handles_empty_pages_and_failing_follow_up_page() -> None:
    empty = PaginatedList(
        lambda page, cursor: JsonPage(items=[], page=1, per_page=10, total=0),
        first_page=JsonPage(items=[], page=1, per_page=10, total=0),
    )
    assert empty.materialize() == []

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        if (page or 1) == 2:
            raise RateLimitError("page 2 failed")
        return JsonPage(items=[1, 2], page=1, per_page=2, total=4)

    items = PaginatedList(fetch, first_page=JsonPage(items=[1, 2], page=1, per_page=2, total=4))
    with pytest.raises(RateLimitError, match="page 2 failed"):
        _ = items[2]


def test_transport_raises_authentication_error_after_failed_refresh() -> None:
    issued_tokens: Iterator[AccessToken] = iter(
        (
            AccessToken("token-1", datetime.now(UTC) + timedelta(minutes=5)),
            AccessToken("token-2", datetime.now(UTC) + timedelta(minutes=5)),
        )
    )
    auth_provider = AuthProvider(
        AuthSettings(client_id="client-id", client_secret="client-secret"),
        token_fetcher=lambda _: next(issued_tokens),
    )
    transport = Transport(
        make_settings(),
        auth_provider=auth_provider,
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(401, json={"message": "unauthorized"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(AuthenticationError):
        transport.request_json("GET", "/secure", context=RequestContext("secure_call"))
