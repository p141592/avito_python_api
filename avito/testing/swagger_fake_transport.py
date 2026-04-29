"""Swagger-aware fake transport for SDK contract tests."""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import cast

import httpx

from avito.client import AvitoClient
from avito.core.swagger_discovery import DiscoveredSwaggerBinding
from avito.core.swagger_registry import SwaggerOperation, SwaggerRegistry
from avito.testing.fake_transport import FakeTransport, JsonValue, RecordedRequest

SdkValue = object

_PATH_PARAMETER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")
_SDK_CONSTANTS: Mapping[str, SdkValue] = {
    "account_id": 7,
    "action_id": 101,
    "call_id": 102,
    "campaign_id": 103,
    "chat_id": "chat-1",
    "dictionary_id": 104,
    "item_id": 105,
    "limit": 2,
    "message_id": "message-1",
    "order_id": 106,
    "parcel_id": 107,
    "report_id": 108,
    "resume_id": 109,
    "scoring_id": 110,
    "tariff_id": 111,
    "task_id": 112,
    "user_id": 7,
    "url": "https://example.test/file.xml",
    "vacancy_id": 113,
    "value": "value",
    "vehicle_id": 114,
}
_BODY_VALUES: Mapping[str, SdkValue] = {
    "action": "approve",
    "action_id": 101,
    "action_ids": [101],
    "applies": [{"resume_id": 109}],
    "auto_renewal": True,
    "billing_type": "package",
    "blacklisted_user_id": 7,
    "blocked_dates": [{"date": "2026-05-01"}],
    "brand_id": 1,
    "call_id": 102,
    "campaign_id": 103,
    "code": "1234",
    "codes": ["xl"],
    "date_time_from": "2026-04-01T00:00:00+00:00",
    "date_time_to": "2026-04-02T00:00:00+00:00",
    "employee_id": 10,
    "files": ["file-1"],
    "ids": [101],
    "image_id": "image-1",
    "intervals": [{"date_from": "2026-05-01", "date_to": "2026-05-02"}],
    "item_id": 105,
    "item_ids": [105],
    "limit": 2,
    "message": "Тестовое сообщение",
    "mileage": 10000,
    "min_stay_days": 2,
    "order_id": 106,
    "package_code": "xl",
    "periods": [{"date_from": "2026-05-01", "date_to": "2026-05-02"}],
    "pickup_point_id": 1,
    "plate_number": "А123АА77",
    "postal_office_id": 1,
    "preview_id": 1,
    "price": 1500,
    "reason": "test",
    "reg_number": "А123АА77",
    "specification_id": 1,
    "task_id": 112,
    "text": "Ответ",
    "title": "Тест",
    "transition": "confirm",
    "url": "https://example.test/file.xml",
    "vacancy_id": 113,
    "vehicle_id": 114,
    "vehicles": [{"vin": "XTA210990Y2766384"}],
    "vin": "XTA210990Y2766384",
}


@dataclass(frozen=True, slots=True)
class SwaggerRoute:
    """Registered fake route bound to one Swagger operation."""

    operation: SwaggerOperation
    payload: JsonValue
    status_code: int
    headers: Mapping[str, str]


class SwaggerFakeTransport(FakeTransport):
    """Fake transport that validates requests against local Swagger operations."""

    def __init__(
        self,
        *,
        registry: SwaggerRegistry,
        base_url: str = "https://api.avito.ru",
    ) -> None:
        super().__init__(base_url=base_url)
        self.registry = registry
        self._swagger_routes: dict[str, SwaggerRoute] = {}

    def add_operation(
        self,
        operation_key: str,
        payload: JsonValue,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> SwaggerFakeTransport:
        """Register response for one Swagger operation key."""

        operation = self.operation(operation_key)
        self._validate_declared_status(operation, status_code)
        self._swagger_routes[operation.key] = SwaggerRoute(
            operation=operation,
            payload=payload,
            status_code=status_code,
            headers=dict(headers or {}),
        )
        return self

    def operation(self, operation_key: str) -> SwaggerOperation:
        """Return operation metadata by canonical key."""

        for operation in self.registry.operations:
            if operation.key == operation_key:
                return operation
        raise AssertionError(f"Swagger operation не найдена: {operation_key}")

    def invoke_binding(
        self,
        binding: DiscoveredSwaggerBinding,
        *,
        client: AvitoClient | None = None,
    ) -> object:
        """Build and invoke SDK call from discovered Swagger binding metadata."""

        if binding.operation_key is None:
            raise AssertionError(f"Binding ambiguous: {binding.sdk_method}")
        sdk_client = client or self.as_client(user_id=cast(int, _SDK_CONSTANTS["user_id"]))
        target = self._build_target(sdk_client, binding)
        method = getattr(target, binding.method_name)
        return method(**self._build_arguments(binding.method_args, method))

    def _handle(self, request: httpx.Request) -> httpx.Response:
        recorded = RecordedRequest(
            method=request.method.upper(),
            path=request.url.path,
            params=dict(request.url.params),
            headers=dict(request.headers),
            json_body=self._decode_json(request),
            content=request.content,
        )
        self.requests.append(recorded)

        route = self._match_route(recorded)
        self._validate_request(route.operation, recorded)
        response = httpx.Response(
            route.status_code,
            json=route.payload,
            headers=dict(route.headers),
        )
        response.request = request
        return response

    def _build_target(
        self,
        client: AvitoClient,
        binding: DiscoveredSwaggerBinding,
    ) -> object:
        if binding.factory is None:
            raise AssertionError(f"Binding не содержит AvitoClient factory: {binding.sdk_method}")
        factory = getattr(client, binding.factory)
        return factory(**self._build_arguments(binding.factory_args, factory))

    def _build_arguments(
        self,
        mapping: Mapping[str, str],
        callable_object: Callable[..., object],
    ) -> dict[str, object]:
        arguments = {
            argument_name: self._value_for_expression(expression)
            for argument_name, expression in mapping.items()
        }
        signature = inspect.signature(callable_object)
        for name, parameter in signature.parameters.items():
            if name == "self" or name in arguments:
                continue
            if parameter.default is inspect.Parameter.empty:
                arguments[name] = self._value_for_name(name)
        return arguments

    def _value_for_expression(self, expression: str) -> object:
        if expression == "body":
            return {"value": "value"}
        prefix, separator, field_name = expression.partition(".")
        if not separator:
            raise AssertionError(f"Некорректное binding expression: {expression}")
        if prefix in {"path", "query", "header", "constant"}:
            return self._value_for_name(field_name)
        if prefix == "body":
            return self._value_for_name(field_name)
        raise AssertionError(f"Неподдерживаемое binding expression: {expression}")

    def _value_for_name(self, name: str) -> object:
        if name == "intervals":
            from avito.realty.models import RealtyInterval

            return [RealtyInterval(date="2026-05-01", available=True)]
        if name in _BODY_VALUES:
            return _BODY_VALUES[name]
        if name in _SDK_CONSTANTS:
            return _SDK_CONSTANTS[name]
        return f"{name}-value"

    def _match_route(self, request: RecordedRequest) -> SwaggerRoute:
        for route in self._swagger_routes.values():
            if route.operation.method != request.method:
                continue
            if self._path_matches(route.operation.path, request.path):
                return route
        available = ", ".join(
            f"{route.operation.method} {route.operation.path}"
            for route in self._swagger_routes.values()
        )
        raise AssertionError(
            f"Маршрут не соответствует Swagger operation: {request.method} "
            f"{request.path}. Доступные: {available}"
        )

    def _validate_request(self, operation: SwaggerOperation, request: RecordedRequest) -> None:
        path_values = self._extract_path_values(operation.path, request.path)
        for parameter in operation.parameters:
            if parameter.location == "path" and parameter.required:
                if parameter.name not in path_values:
                    raise AssertionError(f"Не найден path parameter `{parameter.name}`.")
            if parameter.location == "query" and parameter.required:
                if parameter.name not in request.params:
                    raise AssertionError(f"Не найден query parameter `{parameter.name}`.")
            if parameter.location == "header" and parameter.required:
                if parameter.name.lower() == "authorization":
                    continue
                headers = {name.lower() for name in request.headers}
                if parameter.name.lower() not in headers:
                    raise AssertionError(f"Не найден header parameter `{parameter.name}`.")
        if operation.request_body is None:
            return
        if operation.request_body.required and request.content == b"":
            raise AssertionError(f"{operation.key}: requestBody обязателен.")
        content_type = request.headers.get("content-type", "")
        if request.content and operation.request_body.content_types:
            if not any(expected in content_type for expected in operation.request_body.content_types):
                raise AssertionError(
                    f"{operation.key}: content-type `{content_type}` не описан в Swagger."
                )
        if "application/json" in content_type and request.content:
            try:
                json.loads(request.content.decode())
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{operation.key}: requestBody не является JSON.") from exc

    def _validate_declared_status(self, operation: SwaggerOperation, status_code: int) -> None:
        declared = {
            int(response.status_code)
            for response in operation.responses
            if response.status_code.isdigit()
        }
        if status_code not in declared:
            raise AssertionError(
                f"{operation.key}: status {status_code} не описан в Swagger responses."
            )

    def _path_matches(self, template: str, path: str) -> bool:
        return self._path_pattern(template).fullmatch(self._normalize_swagger_path(path)) is not None

    def _extract_path_values(self, template: str, path: str) -> Mapping[str, str]:
        match = self._path_pattern(template).fullmatch(self._normalize_swagger_path(path))
        return match.groupdict() if match is not None else {}

    def _path_pattern(self, template: str) -> re.Pattern[str]:
        pattern = "^"
        position = 0
        for match in _PATH_PARAMETER_RE.finditer(template):
            pattern += re.escape(template[position : match.start()])
            pattern += f"(?P<{match.group(1)}>[^/]+)"
            position = match.end()
        pattern += re.escape(template[position:])
        pattern += "$"
        return re.compile(pattern)

    def _normalize_swagger_path(self, path: str) -> str:
        if path != "/":
            return path.rstrip("/")
        return path


def error_payload(status_code: int) -> JsonValue:
    """Build deterministic JSON error payload for contract tests."""

    return {
        "message": f"Ошибка {status_code}",
        "code": f"status_{status_code}",
        "details": {"status": status_code},
    }


__all__ = ("SwaggerFakeTransport", "SwaggerRoute", "error_payload")
