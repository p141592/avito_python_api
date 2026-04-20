from __future__ import annotations

from dataclasses import FrozenInstanceError

import httpx
import pytest

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import (
    AvitoError,
    AuthorizationError,
    ConflictError,
    RateLimitError,
    RequestContext,
    ServerError,
    Transport,
    UnsupportedOperationError,
    UpstreamApiError,
    ValidationError,
)
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        auth=AuthSettings(client_id="client-id", client_secret="client-secret"),
        retry_policy=RetryPolicy(max_attempts=1),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )


@pytest.mark.parametrize(
    ("status_code", "error_cls"),
    [
        (400, ValidationError),
        (422, ValidationError),
        (401, AuthorizationError),
        (403, AuthorizationError),
        (409, ConflictError),
        (429, RateLimitError),
        (405, UnsupportedOperationError),
        (418, UpstreamApiError),
        (500, ServerError),
    ],
)
def test_transport_maps_http_statuses_to_typed_sdk_errors(
    status_code: int,
    error_cls: type[Exception],
) -> None:
    transport = make_transport(
        httpx.MockTransport(
            lambda request: httpx.Response(
                status_code,
                json={
                    "message": "boom",
                    "code": "E_GENERIC",
                    "access_token": "secret-token",
                },
                headers={"Authorization": "Bearer secret-token"},
            )
        )
    )

    with pytest.raises(error_cls) as error:
        transport.request_json(
            "POST",
            "/typed-errors",
            context=RequestContext("promotion.target_action.update_manual_bid"),
        )

    assert str(error.value).find("operation=promotion.target_action.update_manual_bid") != -1
    assert error.value.status_code == status_code
    assert error.value.error_code == "E_GENERIC"
    assert error.value.metadata == {"method": "POST", "path": "/typed-errors"}
    assert "secret-token" not in str(error.value.payload)
    assert "secret-token" not in str(error.value.headers)


def test_transport_unknown_upstream_error_keeps_safe_context() -> None:
    transport = make_transport(
        httpx.MockTransport(
            lambda request: httpx.Response(
                418,
                json={
                    "detail": "teapot",
                    "client_secret": "top-secret",
                    "nested": {"refresh_token": "hidden"},
                },
            )
        )
    )

    with pytest.raises(UpstreamApiError) as error:
        transport.request_json("GET", "/teapot", context=RequestContext("ads.list_items"))

    assert error.value.operation == "ads.list_items"
    assert error.value.metadata == {"method": "GET", "path": "/teapot"}
    assert error.value.payload == {
        "detail": "teapot",
        "client_secret": "***",
        "nested": {"refresh_token": "***"},
    }
    assert "top-secret" not in str(error.value)


def test_authorization_error_is_raised_for_auth_failures() -> None:
    transport = make_transport(
        httpx.MockTransport(lambda request: httpx.Response(401, json={"message": "unauthorized"}))
    )

    with pytest.raises(AuthorizationError, match="unauthorized") as error:
        transport.request_json("GET", "/secure", context=RequestContext("accounts.get_self"))

    assert error.value.operation == "accounts.get_self"


def test_avito_error_is_frozen_dataclass() -> None:
    error = AvitoError(
        "boom",
        payload={"access_token": "secret-token"},
        headers={"Authorization": "Bearer secret-token"},
    )

    with pytest.raises(FrozenInstanceError):
        error.message = "updated"

    assert error.payload == {"access_token": "***"}
    assert error.headers == {"Authorization": "***"}
