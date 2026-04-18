from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

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
    ValidationError,
)
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


def make_settings(
    *,
    retry_policy: RetryPolicy | None = None,
    timeouts: ApiTimeouts | None = None,
) -> AvitoSettings:
    return AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(client_id="client-id", client_secret="client-secret"),
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

    with pytest.raises(Exception) as error:
        transport.request_json("POST", "/items", context=RequestContext("create_item"))

    assert "offline" in str(error.value)
    assert calls["count"] == 1


def test_transport_handles_rate_limit_and_classifies_errors() -> None:
    rate_limit_transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    429, headers={"retry-after": "60"}, json={"message": "too many"}
                )
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(RateLimitError):
        rate_limit_transport.request_json("GET", "/limited", context=RequestContext("limited"))

    server_transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(500, json={"message": "server down"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(ServerError):
        server_transport.request_json("GET", "/server", context=RequestContext("server"))

    validation_transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(422, json={"message": "invalid"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(ValidationError):
        validation_transport.request_json(
            "POST", "/validation", context=RequestContext("validation")
        )

    authorization_transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(403, json={"message": "forbidden"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(AuthorizationError):
        authorization_transport.request_json("GET", "/forbidden", context=RequestContext("forbidden"))

    conflict_transport = Transport(
        make_settings(retry_policy=RetryPolicy(max_attempts=1)),
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(409, json={"message": "conflict"})
            ),
            base_url="https://api.avito.ru",
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(ConflictError):
        conflict_transport.request_json("POST", "/conflict", context=RequestContext("conflict"))


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


def test_paginator_collects_typed_pages() -> None:
    pages = {
        1: JsonPage(items=[1, 2], page=1, per_page=2, total=5),
        2: JsonPage(items=[3, 4], page=2, per_page=2, total=5),
        3: JsonPage(items=[5], page=3, per_page=2, total=5),
    }

    paginator = Paginator(lambda page, cursor: pages[page or 1])

    assert paginator.collect() == [1, 2, 3, 4, 5]


def test_paginated_list_behaves_like_list_and_loads_pages_lazily() -> None:
    calls: list[int] = []
    pages = {
        1: JsonPage(items=[1, 2], page=1, per_page=2, total=5),
        2: JsonPage(items=[3, 4], page=2, per_page=2, total=5),
        3: JsonPage(items=[5], page=3, per_page=2, total=5),
    }

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        return pages[resolved_page]

    items = PaginatedList(fetch, first_page=pages[1])

    assert items.loaded_count == 2
    assert items.is_materialized is False

    assert items[0] == 1
    assert calls == []

    assert items[3] == 4
    assert calls == [2]
    assert items.loaded_count == 4
    assert items.is_materialized is False

    assert items[:] == [1, 2, 3, 4, 5]
    assert calls == [2, 3]
    assert items.loaded_count == 5
    assert items.is_materialized is True

    assert len(items) == 5
    assert items == [1, 2, 3, 4, 5]


def test_paginated_list_partial_iteration_fetches_only_required_pages() -> None:
    calls: list[int] = []
    pages = {
        1: JsonPage(items=[1, 2], page=1, per_page=2, total=5),
        2: JsonPage(items=[3, 4], page=2, per_page=2, total=5),
        3: JsonPage(items=[5], page=3, per_page=2, total=5),
    }

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        return pages[resolved_page]

    items = PaginatedList(fetch, first_page=pages[1])

    assert list(item for _, item in zip(range(3), items, strict=False)) == [1, 2, 3]
    assert calls == [2]
    assert items.loaded_count == 4
    assert items.is_materialized is False


def test_paginated_list_materialize_loads_all_remaining_pages_once() -> None:
    calls: list[int] = []
    pages = {
        1: JsonPage(items=[1, 2], page=1, per_page=2, total=5),
        2: JsonPage(items=[3, 4], page=2, per_page=2, total=5),
        3: JsonPage(items=[5], page=3, per_page=2, total=5),
    }

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        return pages[resolved_page]

    items = PaginatedList(fetch, first_page=pages[1])

    assert items.materialize() == [1, 2, 3, 4, 5]
    assert items.materialize() == [1, 2, 3, 4, 5]
    assert calls == [2, 3]
    assert items.is_materialized is True


def test_paginated_list_propagates_error_when_read_reaches_failing_page() -> None:
    calls: list[int] = []

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        if resolved_page == 2:
            raise RateLimitError("page 2 failed")
        return JsonPage(items=[1, 2], page=1, per_page=2, total=4)

    items = PaginatedList(fetch, first_page=JsonPage(items=[1, 2], page=1, per_page=2, total=4))

    assert items[0] == 1
    with pytest.raises(RateLimitError, match="page 2 failed"):
        _ = items[2]
    assert calls == [2]


def test_paginated_list_handles_empty_first_page_without_extra_calls() -> None:
    calls: list[int] = []

    def fetch(page: int | None, cursor: str | None) -> JsonPage[int]:
        resolved_page = page or 1
        calls.append(resolved_page)
        return JsonPage(items=[], page=resolved_page, per_page=10, total=0)

    items = PaginatedList(fetch, first_page=JsonPage(items=[], page=1, per_page=10, total=0))

    assert items.materialize() == []
    assert calls == []
    assert items.loaded_count == 0
    assert items.is_materialized is True


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
