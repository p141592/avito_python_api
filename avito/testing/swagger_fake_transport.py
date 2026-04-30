"""Swagger-aware fake transport for SDK contract tests."""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qs

import httpx

from avito.auth import AuthSettings
from avito.auth.models import ClientCredentialsRequest, RefreshTokenRequest
from avito.auth.provider import AlternateTokenClient, TokenClient
from avito.client import AvitoClient
from avito.core.swagger_discovery import DiscoveredSwaggerBinding
from avito.core.swagger_registry import SwaggerOperation, SwaggerRegistry, SwaggerResponse
from avito.testing.fake_transport import FakeTransport, JsonValue, RecordedRequest

if TYPE_CHECKING:
    from avito.orders.models import DeliveryAddress, DeliveryRestriction, WeeklySchedule

SdkValue = object

_PATH_PARAMETER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")
_SDK_CONSTANTS: Mapping[str, SdkValue] = {
    "account_id": 7,
    "action_id": 101,
    "call_id": 102,
    "campaign_id": 103,
    "chat_id": "chat-1",
    "delivery_provider_id": "provider-1",
    "dictionary_id": 104,
    "employee_id": 10,
    "grant_type": "client_credentials",
    "item_id": 105,
    "item_ids": [105],
    "limit": 2,
    "message_id": "message-1",
    "offset": 0,
    "order_id": 106,
    "parcel_id": 107,
    "price": 1500,
    "report_id": 108,
    "review_id": 115,
    "resume_id": 109,
    "scoring_id": 110,
    "tariff_id": 111,
    "teaser_id": "teaser-1",
    "task_id": 112,
    "user_id": 7,
    "url": "https://example.test/file.xml",
    "vacancy_id": 113,
    "vacancy_uuid": "vacancy-uuid-1",
    "value": "value",
    "vehicle_id": 114,
    "voice_ids": ["voice-1"],
}
_BODY_VALUES: Mapping[str, SdkValue] = {
    "action": "approve",
    "action_type_id": 1,
    "action_id": 101,
    "action_ids": [101],
    "applies": [],
    "auto_renewal": True,
    "bid_penny": 1000,
    "billing_type": "package",
    "blacklisted_user_id": 7,
    "blocked_dates": [{"date": "2026-05-01"}],
    "brand_id": 1,
    "budget_penny": 1000,
    "budget_type": "daily",
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
    "name": "Тариф",
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

    def add_success_operation(
        self,
        operation_key: str,
        *,
        payload: JsonValue | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> SwaggerFakeTransport:
        """Register a deterministic success response for one Swagger operation."""

        operation = self.operation(operation_key)
        response = _success_response(operation)
        status_code = int(response.status_code)
        return self.add_operation(
            operation_key,
            success_payload(operation) if payload is None else payload,
            status_code=status_code,
            headers=headers,
        )

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
        if binding.domain == "auth":
            target = self._build_auth_target(binding)
            method = getattr(target, binding.method_name)
            return method(**self._build_arguments(binding.method_args, method))
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

    def _build_auth_target(self, binding: DiscoveredSwaggerBinding) -> object:
        settings = AuthSettings(
            client_id="fake-client-id",
            client_secret="fake-client-secret",
            refresh_token="fake-refresh-token",
            scope="fake-scope",
            token_url=binding.path,
            alternate_token_url=binding.path,
            autoteka_token_url="/token",
            autoteka_client_id="fake-autoteka-client-id",
            autoteka_client_secret="fake-autoteka-client-secret",
            autoteka_scope="autoteka:read",
        )
        client = httpx.Client(
            transport=httpx.MockTransport(self._handle),
            base_url=self.base_url,
        )
        if binding.class_name == "AlternateTokenClient":
            return AlternateTokenClient(settings=settings, client=client)
        if binding.class_name == "TokenClient":
            return TokenClient(settings=settings, client=client)
        raise AssertionError(f"Неподдерживаемый auth binding: {binding.sdk_method}")

    def _build_arguments(
        self,
        mapping: Mapping[str, str],
        callable_object: Callable[..., object],
    ) -> dict[str, object]:
        signature = inspect.signature(callable_object)
        arguments = {}
        for argument_name, expression in mapping.items():
            parameter = signature.parameters.get(argument_name)
            arguments[argument_name] = self._value_for_argument(
                argument_name,
                expression,
                parameter,
            )
        for name, parameter in signature.parameters.items():
            if name == "self" or name in arguments:
                continue
            if (
                parameter.default is inspect.Parameter.empty
                or self._should_supply_optional_argument(name, parameter)
            ):
                arguments[name] = self._value_for_argument(name, f"constant.{name}", parameter)
        return arguments

    def _value_for_argument(
        self,
        argument_name: str,
        expression: str,
        parameter: inspect.Parameter | None,
    ) -> object:
        annotation = _annotation_name(parameter)
        if "ClientCredentialsRequest" in annotation:
            return ClientCredentialsRequest(
                client_id="fake-client-id",
                client_secret="fake-client-secret",
                scope="fake-scope",
            )
        if "RefreshTokenRequest" in annotation:
            return RefreshTokenRequest(
                client_id="fake-client-id",
                client_secret="fake-client-secret",
                refresh_token="fake-refresh-token",
                scope="fake-scope",
            )
        if argument_name == "query":
            return self._query_value(annotation)
        if argument_name == "files" or "UploadImageFile" in annotation:
            from avito.messenger.models import UploadImageFile

            return [
                UploadImageFile(
                    field_name="image",
                    filename="image.jpg",
                    content=b"image-bytes",
                    content_type="image/jpeg",
                )
            ]
        if expression == "body":
            return self._body_value(argument_name, annotation)
        return self._value_for_expression(expression, argument_name=argument_name, annotation=annotation)

    def _value_for_expression(
        self,
        expression: str,
        *,
        argument_name: str,
        annotation: str,
    ) -> object:
        if expression == "body":
            return self._body_value(argument_name, annotation)
        prefix, separator, field_name = expression.partition(".")
        if not separator:
            raise AssertionError(f"Некорректное binding expression: {expression}")
        if prefix in {"path", "query", "header", "constant"}:
            return self._value_for_name(field_name)
        if prefix == "body":
            return self._body_field_value(argument_name, field_name, annotation)
        raise AssertionError(f"Неподдерживаемое binding expression: {expression}")

    def _query_value(self, annotation: str) -> object:
        if "MonitoringEventsQuery" in annotation:
            from avito.autoteka.models import MonitoringEventsQuery

            return MonitoringEventsQuery(limit=2)
        if "ApplicationIdsQuery" in annotation:
            from avito.jobs.models import ApplicationIdsQuery

            return ApplicationIdsQuery(updated_at_from="2026-04-01T00:00:00+00:00")
        if "ResumeSearchQuery" in annotation:
            from avito.jobs.models import ResumeSearchQuery

            return ResumeSearchQuery(query="python")
        if "VacanciesQuery" in annotation:
            from avito.jobs.models import VacanciesQuery

            return VacanciesQuery(query="python")
        if "ReviewsQuery" in annotation:
            from avito.ratings.models import ReviewsQuery

            return ReviewsQuery(offset=0, limit=10)
        return self._value_for_name("query")

    def _body_value(self, argument_name: str, annotation: str) -> object:
        if "SandboxArea" in annotation:
            from avito.orders.models import SandboxArea

            return [SandboxArea(city="Москва")]
        if "SortingCenterUpload" in annotation:
            return [self._sorting_center_upload()]
        if "TaggedSortingCenter" in annotation:
            from avito.orders.models import TaggedSortingCenter

            return [TaggedSortingCenter(delivery_provider_id="provider-1", direction_tag="tag-1")]
        if "TerminalUpload" in annotation:
            return [self._terminal_upload()]
        if "DeliveryTermsZone" in annotation:
            from avito.orders.models import DeliveryTermsZone

            return [DeliveryTermsZone(delivery_provider_zone_id="zone-1", min_term=1, max_term=2)]
        if "StockUpdateEntry" in annotation:
            from avito.orders.models import StockUpdateEntry

            return [StockUpdateEntry(item_id=105, quantity=5)]
        return self._body_field_value(argument_name, argument_name, annotation)

    def _body_field_value(self, argument_name: str, field_name: str, annotation: str) -> object:
        if argument_name == "applies" or "ApplicationViewedItem" in annotation:
            from avito.jobs.models import ApplicationViewedItem

            return [ApplicationViewedItem(id="apply-1", is_viewed=True)]
        if "BbipItemInput" in annotation:
            return [{"item_id": 105, "duration": 7, "price": 1500, "old_price": 2000}]
        if "TrxItemInput" in annotation:
            return [
                {
                    "item_id": 105,
                    "commission": 10,
                    "date_from": datetime(2026, 5, 1, tzinfo=UTC),
                }
            ]
        if "BidItemInput" in annotation:
            return [{"item_id": 105, "price_penny": 1000}]
        if "StockUpdateEntry" in annotation:
            from avito.orders.models import StockUpdateEntry

            return [StockUpdateEntry(item_id=105, quantity=5)]
        if field_name == "directions":
            from avito.orders.models import DeliveryDirection, DeliveryDirectionZone

            return [
                DeliveryDirection(
                    provider_direction_id="direction-1",
                    tag_from="from",
                    tag_to="to",
                    zones=[DeliveryDirectionZone(tariff_zone_id="tariff-zone-1")],
                )
            ]
        if field_name == "tariff_zones":
            from avito.orders.models import (
                DeliveryTariffItem,
                DeliveryTariffValue,
                DeliveryTariffZone,
            )

            return [
                DeliveryTariffZone(
                    name="Зона",
                    delivery_provider_zone_id="zone-1",
                    items=[
                        DeliveryTariffItem(
                            calculation_mechanic="fixed",
                            chargeable_parameter="weight",
                            service_name="delivery",
                            values=[DeliveryTariffValue(cost=100)],
                        )
                    ],
                )
            ]
        if field_name == "terms_zones":
            from avito.orders.models import DeliveryTermsZone

            return [DeliveryTermsZone(delivery_provider_zone_id="zone-1", min_term=1, max_term=2)]
        if field_name == "periods" or "RealtyPricePeriod" in annotation:
            from avito.realty.models import RealtyPricePeriod

            return [RealtyPricePeriod(date_from="2026-05-01", price=1500)]
        if "SandboxCancelAnnouncementOptions" in annotation:
            from avito.orders.models import SandboxCancelAnnouncementOptions

            return SandboxCancelAnnouncementOptions(
                url_to_cancel_announcement="https://example.test/cancel"
            )
        if field_name == "sender" or "SandboxAnnouncementParticipant" in annotation:
            return self._sandbox_participant("sender")
        if field_name == "receiver":
            return self._sandbox_participant("receiver")
        if field_name == "packages" or "SandboxAnnouncementPackage" in annotation:
            from avito.orders.models import SandboxAnnouncementPackage

            return [SandboxAnnouncementPackage(package_id="package-1", parcel_ids=["parcel-1"])]
        if "SandboxCreateAnnouncementOptions" in annotation:
            from avito.orders.models import SandboxCreateAnnouncementOptions

            return SandboxCreateAnnouncementOptions(
                url_to_send_announcement="https://example.test/send"
            )
        if "OrderDeliveryProperties" in annotation:
            from avito.orders.models import OrderDeliveryProperties

            return OrderDeliveryProperties(dimensions=[10, 10, 10], weight=100)
        if "RealAddress" in annotation:
            from avito.orders.models import RealAddress

            return RealAddress(address_type="terminal", terminal_number="terminal-1")
        if "CustomAreaScheduleEntry" in annotation:
            from avito.orders.models import CustomAreaScheduleEntry, DeliveryDateInterval

            return [
                CustomAreaScheduleEntry(
                    provider_area_numbers=["area-1"],
                    services=["delivery"],
                    custom_schedule=[
                        DeliveryDateInterval(date="2026-05-01", intervals=["09:00-18:00"])
                    ],
                )
            ]
        return self._value_for_name(field_name)

    def _should_supply_optional_argument(
        self,
        name: str,
        parameter: inspect.Parameter,
    ) -> bool:
        if parameter.default is not None:
            return False
        return name in _SDK_CONSTANTS or name in {"item_ids", "query"}

    def _value_for_name(self, name: str) -> object:
        if name == "intervals":
            from avito.realty.models import RealtyInterval

            return [RealtyInterval(date="2026-05-01", available=True)]
        if name == "blocked_dates":
            return ["2026-05-01"]
        if name == "date_start":
            return "2026-05-01"
        if name == "date_end":
            return "2026-05-02"
        if name in _BODY_VALUES:
            return _BODY_VALUES[name]
        if name in _SDK_CONSTANTS:
            return _SDK_CONSTANTS[name]
        return f"{name}-value"

    def _sorting_center_upload(self) -> object:
        from avito.orders.models import SortingCenterUpload

        return SortingCenterUpload(
            delivery_provider_id="provider-1",
            name="СЦ",
            address=self._delivery_address(),
            phones=["+70000000000"],
            itinerary="Вход",
            photos=["photo-1"],
            schedule=self._weekly_schedule(),
            restriction=self._delivery_restriction(),
            direction_tag="tag-1",
        )

    def _terminal_upload(self) -> object:
        from avito.orders.models import TerminalUpload

        return TerminalUpload(
            delivery_provider_id="provider-1",
            name="ПВЗ",
            address=self._delivery_address(),
            phones=["+70000000000"],
            itinerary="Вход",
            photos=["photo-1"],
            direction_tag="tag-1",
            services=["pickup"],
            schedule=self._weekly_schedule(),
            restriction=self._delivery_restriction(),
        )

    def _delivery_address(self) -> DeliveryAddress:
        from avito.orders.models import DeliveryAddress

        return DeliveryAddress(
            country="RU",
            region="Москва",
            locality="Москва",
            fias="fias-1",
            zip_code="101000",
            lat=55.75,
            lng=37.62,
        )

    def _weekly_schedule(self) -> WeeklySchedule:
        from avito.orders.models import WeeklySchedule

        hours = ["09:00-18:00"]
        return WeeklySchedule(
            mon=hours,
            tue=hours,
            wed=hours,
            thu=hours,
            fri=hours,
            sat=hours,
            sun=hours,
        )

    def _delivery_restriction(self) -> DeliveryRestriction:
        from avito.orders.models import DeliveryRestriction

        return DeliveryRestriction(
            max_weight=1000,
            max_dimensions=[10, 10, 10],
            max_declared_cost=10000,
        )

    def _sandbox_participant(self, participant_type: str) -> object:
        from avito.orders.models import (
            SandboxAnnouncementDelivery,
            SandboxAnnouncementParticipant,
            SandboxDeliveryPoint,
        )

        return SandboxAnnouncementParticipant(
            type=participant_type,
            phones=["+70000000000"],
            email=f"{participant_type}@example.test",
            name=participant_type,
            delivery=SandboxAnnouncementDelivery(
                type="terminal",
                terminal=SandboxDeliveryPoint(provider="pochta", point_id="point-1"),
            ),
        )

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
        form_values = self._form_values(request)
        for parameter in operation.parameters:
            if parameter.location == "path" and parameter.required:
                if parameter.name not in path_values:
                    raise AssertionError(f"Не найден path parameter `{parameter.name}`.")
            if parameter.location == "query" and parameter.required:
                if parameter.name not in request.params and parameter.name not in form_values:
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

    def _form_values(self, request: RecordedRequest) -> Mapping[str, str]:
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" not in content_type or not request.content:
            return {}
        parsed = parse_qs(request.content.decode())
        return {name: values[-1] for name, values in parsed.items() if values}

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


def success_payload(operation: SwaggerOperation) -> JsonValue:
    """Build deterministic success payload for one operation."""

    if operation.spec in {"Авторизация.json", "Автотека.json"} and operation.path.startswith("/token"):
        return {
            "access_token": "access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh-token",
            "scope": "fake-scope",
        }
    if operation.key == "CallTracking[КТ].json POST /calltracking/v1/getCallById":
        return {"call": {"id": "call-1"}, "error": {"code": 0, "message": "ok"}}
    if operation.key == "Продвижение.json POST /promotion/v1/items/services/orders/status":
        return {"orderId": "order-1", "status": "active", "items": [], "errors": []}
    if operation.key == "Настройкаценыцелевогодействия.json GET /cpxpromo/1/getBids/{itemId}":
        return {"actionTypeID": 1, "selectedType": "manual", "manual": {}, "auto": {}}
    if operation.key == "Настройкаценыцелевогодействия.json POST /cpxpromo/1/getPromotionsByItemIds":
        return {"items": []}
    return {}


def _success_response(operation: SwaggerOperation) -> SwaggerResponse:
    for response in operation.success_responses:
        if response.status_code.isdigit():
            return response
    raise AssertionError(f"{operation.key}: Swagger operation не содержит success response.")


def _annotation_name(parameter: inspect.Parameter | None) -> str:
    if parameter is None:
        return ""
    annotation = parameter.annotation
    if annotation is inspect.Parameter.empty:
        return ""
    return str(annotation)


__all__ = ("SwaggerFakeTransport", "SwaggerRoute", "error_payload", "success_payload")
