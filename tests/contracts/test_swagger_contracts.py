from __future__ import annotations

import pytest

from avito.accounts.models import AccountProfile, EmployeeItem
from avito.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UpstreamApiError,
    ValidationError,
)
from avito.core.pagination import PaginatedList
from avito.core.swagger_discovery import DiscoveredSwaggerBinding, discover_swagger_bindings
from avito.core.swagger_registry import SwaggerRegistry, load_swagger_registry
from avito.testing import SwaggerFakeTransport, error_payload


def _binding(registry: SwaggerRegistry, operation_key: str) -> DiscoveredSwaggerBinding:
    discovery = discover_swagger_bindings(registry=registry)
    matches = [binding for binding in discovery.bindings if binding.operation_key == operation_key]
    assert len(matches) == 1
    return matches[0]


def test_swagger_fake_transport_invokes_generated_read_call_and_validates_path() -> None:
    registry = load_swagger_registry()
    binding = _binding(registry, "Информацияопользователе.json GET /core/v1/accounts/{user_id}/balance")
    fake = SwaggerFakeTransport(registry=registry)
    fake.add_operation(
        binding.operation_key or "",
        {"user_id": 7, "balance": {"real": 150.0, "bonus": 20.0, "currency": "RUB"}},
    )

    result = fake.invoke_binding(binding)

    request = fake.last()
    assert request.method == "GET"
    assert request.path == "/core/v1/accounts/7/balance/"
    assert request.json_body is None
    assert result.to_dict()["total"] == 170.0


def test_swagger_fake_transport_invokes_generated_write_call_and_validates_json_body() -> None:
    registry = load_swagger_registry()
    binding = _binding(registry, "ИерархияАккаунтов.json POST /listItemsByEmployeeIdV1")
    fake = SwaggerFakeTransport(registry=registry)
    fake.add_operation(
        binding.operation_key or "",
        {
            "items": [{"item_id": 105, "title": "Объявление", "status": "active"}],
            "total": 1,
        },
    )

    result = fake.invoke_binding(binding)

    request = fake.last()
    assert request.method == "POST"
    assert request.path == "/listItemsByEmployeeIdV1"
    assert request.headers["content-type"] == "application/json"
    assert request.json_body == {"employeeId": 10, "limit": 25, "offset": 0}
    assert isinstance(result, PaginatedList)
    assert isinstance(result[0], EmployeeItem)


def test_swagger_fake_transport_validates_response_status_is_declared_in_swagger() -> None:
    registry = load_swagger_registry()
    fake = SwaggerFakeTransport(registry=registry)

    with pytest.raises(AssertionError, match="не описан в Swagger responses"):
        fake.add_operation(
            "Информацияопользователе.json GET /core/v1/accounts/self",
            {},
            status_code=418,
        )


def test_swagger_fake_transport_maps_happy_path_response_to_typed_sdk_model() -> None:
    registry = load_swagger_registry()
    binding = _binding(registry, "Информацияопользователе.json GET /core/v1/accounts/self")
    fake = SwaggerFakeTransport(registry=registry)
    fake.add_operation(
        binding.operation_key or "",
        {"id": 7, "name": "Иван", "email": "user@example.test", "phone": "+7000"},
    )

    result = fake.invoke_binding(binding)

    assert isinstance(result, AccountProfile)
    assert result.user_id == 7
    assert result.name == "Иван"


@pytest.mark.parametrize(
    ("operation_key", "status_code", "expected_error"),
    [
        (
            "Информацияопользователе.json GET /core/v1/accounts/self",
            401,
            AuthenticationError,
        ),
        (
            "Информацияопользователе.json GET /core/v1/accounts/self",
            403,
            AuthorizationError,
        ),
        (
            "АвитоРабота.json GET /job/v1/applications/get_states",
            400,
            ValidationError,
        ),
        (
            "АвитоРабота.json GET /job/v1/applications/get_states",
            402,
            UpstreamApiError,
        ),
        (
            "АвитоРабота.json GET /job/v1/applications/get_states",
            404,
            NotFoundError,
        ),
        (
            "Автостратегия.json POST /autostrategy/v1/campaign/info",
            409,
            ConflictError,
        ),
        (
            "Краткосрочнаяаренда.json POST /realty/v1/items/intervals",
            422,
            ValidationError,
        ),
        (
            "CallTracking[КТ].json GET /calltracking/v1/getRecordByCallId",
            425,
            UpstreamApiError,
        ),
        (
            "АвитоРабота.json GET /job/v1/applications/get_states",
            429,
            RateLimitError,
        ),
        (
            "Информацияопользователе.json GET /core/v1/accounts/self",
            500,
            ServerError,
        ),
        (
            "Информацияопользователе.json GET /core/v1/accounts/self",
            503,
            ServerError,
        ),
    ],
)
def test_swagger_fake_transport_validates_all_swagger_error_status_categories(
    operation_key: str,
    status_code: int,
    expected_error: type[Exception],
) -> None:
    registry = load_swagger_registry()
    binding = _binding(registry, operation_key)
    fake = SwaggerFakeTransport(registry=registry)
    fake.add_operation(operation_key, error_payload(status_code), status_code=status_code)

    with pytest.raises(expected_error) as exc_info:
        fake.invoke_binding(binding)

    assert exc_info.value.args[0] == f"Ошибка {status_code}"


def test_swagger_fake_transport_covers_all_error_statuses_declared_by_corpus() -> None:
    registry = load_swagger_registry()

    assert sorted(
        {
            response.status_code
            for operation in registry.operations
            for response in operation.error_responses
            if response.status_code.isdigit()
        }
    ) == ["400", "401", "402", "403", "404", "409", "422", "425", "429", "500", "503"]


def test_swagger_fake_transport_invokes_deprecated_legacy_operation_with_runtime_warning() -> None:
    registry = load_swagger_registry()
    binding = _binding(registry, "Автозагрузка.json GET /autoload/v1/profile")
    fake = SwaggerFakeTransport(registry=registry)
    fake.add_operation(
        binding.operation_key or "",
        {"user_id": 7, "is_enabled": True, "upload_url": "https://example.test/upload"},
    )

    with pytest.warns(DeprecationWarning):
        result = fake.invoke_binding(binding)

    request = fake.last()
    assert request.method == "GET"
    assert request.path == "/autoload/v1/profile"
    assert result.to_dict()["is_enabled"] is True
