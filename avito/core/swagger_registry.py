"""Swagger/OpenAPI registry used by binding linting tools."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

HTTP_METHODS = frozenset({"delete", "get", "head", "options", "patch", "post", "put", "trace"})
DEFAULT_SWAGGER_API_DIR = Path("docs/avito/api")

_PATH_PARAMETER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")

JsonObject = dict[str, object]


class SwaggerRegistryError(Exception):
    """Ошибка чтения или валидации локального Swagger corpus."""


@dataclass(frozen=True, slots=True)
class SwaggerValidationError:
    """Нефатальная ошибка валидации Swagger operation, найденная при разборе specs."""

    code: str
    message: str
    operation_key: str | None = None


@dataclass(frozen=True, slots=True)
class SwaggerParameter:
    """Параметр Swagger operation после разрешения локальных `$ref`."""

    name: str
    location: str
    required: bool


@dataclass(frozen=True, slots=True)
class SwaggerRequestBody:
    """Минимальная metadata request body для будущей validation binding expressions."""

    required: bool
    content_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SwaggerResponse:
    """Минимальная metadata Swagger response для contract tests."""

    status_code: str
    content_types: tuple[str, ...]

    @property
    def is_success(self) -> bool:
        return self.status_code.isdigit() and 200 <= int(self.status_code) < 300

    @property
    def is_error(self) -> bool:
        return self.status_code == "default" or (
            self.status_code.isdigit() and int(self.status_code) >= 400
        )


@dataclass(frozen=True, slots=True)
class SwaggerOperation:
    """Одна Swagger/OpenAPI operation с normalized identity."""

    spec: str
    method: str
    path: str
    operation_id: str | None
    deprecated: bool
    parameters: tuple[SwaggerParameter, ...]
    request_body: SwaggerRequestBody | None
    responses: tuple[SwaggerResponse, ...]

    @property
    def key(self) -> str:
        return f"{self.spec} {self.method} {self.path}"

    @property
    def path_parameters(self) -> tuple[SwaggerParameter, ...]:
        return tuple(parameter for parameter in self.parameters if parameter.location == "path")

    @property
    def query_parameters(self) -> tuple[SwaggerParameter, ...]:
        return tuple(parameter for parameter in self.parameters if parameter.location == "query")

    @property
    def header_parameters(self) -> tuple[SwaggerParameter, ...]:
        return tuple(parameter for parameter in self.parameters if parameter.location == "header")

    @property
    def success_responses(self) -> tuple[SwaggerResponse, ...]:
        return tuple(response for response in self.responses if response.is_success)

    @property
    def error_responses(self) -> tuple[SwaggerResponse, ...]:
        return tuple(response for response in self.responses if response.is_error)


@dataclass(frozen=True, slots=True)
class SwaggerSpec:
    """Один Swagger/OpenAPI файл и извлечённые из него операции."""

    name: str
    path: Path
    operations: tuple[SwaggerOperation, ...]


@dataclass(frozen=True, slots=True)
class SwaggerRegistry:
    """Полный локальный Swagger corpus."""

    specs: tuple[SwaggerSpec, ...]
    errors: tuple[SwaggerValidationError, ...] = ()

    @property
    def operations(self) -> tuple[SwaggerOperation, ...]:
        return tuple(operation for spec in self.specs for operation in spec.operations)

    @property
    def deprecated_operations(self) -> tuple[SwaggerOperation, ...]:
        return tuple(operation for operation in self.operations if operation.deprecated)


def load_swagger_registry(
    api_dir: Path = DEFAULT_SWAGGER_API_DIR,
    *,
    strict: bool = False,
) -> SwaggerRegistry:
    """Загружает и валидирует все Swagger/OpenAPI specs из каталога."""

    spec_paths = tuple(sorted(api_dir.glob("*.json")))
    if not spec_paths:
        raise SwaggerRegistryError(f"В каталоге {api_dir} не найдены Swagger JSON files.")

    errors: list[SwaggerValidationError] = []
    specs = tuple(_load_spec(path, errors) for path in spec_paths)
    _validate_unique_operation_keys(specs, errors)
    registry = SwaggerRegistry(specs=specs, errors=tuple(errors))
    if strict and registry.errors:
        messages = "; ".join(error.message for error in registry.errors)
        raise SwaggerRegistryError(messages)
    return registry


def normalize_swagger_method(method: str) -> str:
    """Возвращает normalized HTTP method для operation identity."""

    normalized = method.strip().upper()
    if not normalized:
        raise SwaggerRegistryError("HTTP-метод Swagger operation не может быть пустым.")
    return normalized


def normalize_swagger_path(path: str) -> str:
    """Возвращает normalized Swagger path для operation identity."""

    normalized = path.strip()
    if not normalized.startswith("/"):
        raise SwaggerRegistryError(f"Swagger path должен начинаться с `/`: {path}")
    if normalized != "/":
        normalized = normalized.rstrip("/")
    without_parameters = _PATH_PARAMETER_RE.sub("", normalized)
    if "{" in without_parameters or "}" in without_parameters:
        raise SwaggerRegistryError(
            f"Swagger path должен использовать параметры в формате `{{name}}`: {path}"
        )
    return normalized


def _load_spec(path: Path, errors: list[SwaggerValidationError]) -> SwaggerSpec:
    try:
        # `json.loads()` возвращает object на границе JSON-декодирования.
        raw = cast(object, json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        raise SwaggerRegistryError(f"Файл {path} содержит некорректный JSON: {exc}") from exc
    spec = _require_mapping(raw, f"{path}")
    paths = _require_mapping(spec.get("paths"), f"{path}: поле paths")

    operations: list[SwaggerOperation] = []
    for raw_path, raw_path_item in sorted(paths.items()):
        if not isinstance(raw_path, str):
            raise SwaggerRegistryError(f"{path}: ключ paths должен быть строкой.")
        path_item = _require_mapping(raw_path_item, f"{path}: path item {raw_path}")
        path_parameters = _extract_parameters(
            spec=spec,
            parameters=_optional_sequence(path_item.get("parameters"), f"{path}: {raw_path}.parameters"),
            source=f"{path}: {raw_path}.parameters",
        )
        for raw_method, raw_operation in sorted(path_item.items()):
            if not isinstance(raw_method, str) or raw_method.lower() not in HTTP_METHODS:
                continue
            operation = _require_mapping(raw_operation, f"{path}: {raw_path}.{raw_method}")
            operation_parameters = _extract_parameters(
                spec=spec,
                parameters=_optional_sequence(
                    operation.get("parameters"),
                    f"{path}: {raw_path}.{raw_method}.parameters",
                ),
                source=f"{path}: {raw_path}.{raw_method}.parameters",
            )
            normalized_path = normalize_swagger_path(raw_path)
            parameters = (*path_parameters, *operation_parameters)
            _validate_path_parameters(
                spec_name=path.name,
                method=normalize_swagger_method(raw_method),
                path=normalized_path,
                parameters=parameters,
                errors=errors,
            )
            operations.append(
                SwaggerOperation(
                    spec=path.name,
                    method=normalize_swagger_method(raw_method),
                    path=normalized_path,
                    operation_id=_optional_string(operation.get("operationId")),
                    deprecated=operation.get("deprecated") is True,
                    parameters=parameters,
                    request_body=_extract_request_body(operation.get("requestBody")),
                    responses=_extract_responses(operation.get("responses")),
                )
            )

    return SwaggerSpec(name=path.name, path=path, operations=tuple(operations))


def _extract_parameters(
    *,
    spec: Mapping[str, object],
    parameters: Iterable[object],
    source: str,
) -> tuple[SwaggerParameter, ...]:
    extracted: list[SwaggerParameter] = []
    for index, raw_parameter in enumerate(parameters):
        parameter = _resolve_ref(spec, raw_parameter, f"{source}[{index}]")
        name = _required_string(parameter.get("name"), f"{source}[{index}].name")
        location = _required_string(parameter.get("in"), f"{source}[{index}].in")
        extracted.append(
            SwaggerParameter(
                name=name,
                location=location,
                required=parameter.get("required") is True,
            )
        )
    return tuple(extracted)


def _extract_request_body(raw_request_body: object) -> SwaggerRequestBody | None:
    if raw_request_body is None:
        return None
    request_body = _require_mapping(raw_request_body, "requestBody")
    content = _require_mapping(request_body.get("content"), "requestBody.content")
    return SwaggerRequestBody(
        required=request_body.get("required") is True,
        content_types=tuple(sorted(str(content_type) for content_type in content)),
    )


def _extract_responses(raw_responses: object) -> tuple[SwaggerResponse, ...]:
    responses = _require_mapping(raw_responses, "responses")
    extracted: list[SwaggerResponse] = []
    for raw_status_code, raw_response in sorted(responses.items()):
        if not isinstance(raw_status_code, str):
            raise SwaggerRegistryError("responses должен использовать строковые status codes.")
        response = _require_mapping(raw_response, f"responses.{raw_status_code}")
        content = response.get("content")
        content_types: tuple[str, ...] = ()
        if isinstance(content, Mapping):
            content_types = tuple(sorted(str(content_type) for content_type in content))
        extracted.append(
            SwaggerResponse(
                status_code=raw_status_code,
                content_types=content_types,
            )
        )
    return tuple(extracted)


def _validate_path_parameters(
    *,
    spec_name: str,
    method: str,
    path: str,
    parameters: tuple[SwaggerParameter, ...],
    errors: list[SwaggerValidationError],
) -> None:
    path_parameter_names = set(_PATH_PARAMETER_RE.findall(path))
    described_path_parameter_names = {
        parameter.name for parameter in parameters if parameter.location == "path"
    }
    if path_parameter_names != described_path_parameter_names:
        missing = sorted(path_parameter_names - described_path_parameter_names)
        extra = sorted(described_path_parameter_names - path_parameter_names)
        operation_key = f"{spec_name} {method} {path}"
        errors.append(
            SwaggerValidationError(
                code="SWAGGER_PATH_PARAMETER_MISMATCH",
                message=(
                    f"{operation_key}: path parameters не совпадают с URL "
                    f"(missing={missing}, extra={extra})."
                ),
                operation_key=operation_key,
            )
        )


def _validate_unique_operation_keys(
    specs: tuple[SwaggerSpec, ...],
    errors: list[SwaggerValidationError],
) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for spec in specs:
        for operation in spec.operations:
            if operation.key in seen:
                duplicates.append(operation.key)
            seen.add(operation.key)
    if duplicates:
        for operation_key in sorted(duplicates):
            errors.append(
                SwaggerValidationError(
                    code="SWAGGER_DUPLICATE_OPERATION_KEY",
                    message=f"Найден duplicate Swagger operation key: {operation_key}",
                    operation_key=operation_key,
                )
            )


def _resolve_ref(spec: Mapping[str, object], raw_value: object, source: str) -> Mapping[str, object]:
    value = _require_mapping(raw_value, source)
    raw_ref = value.get("$ref")
    if raw_ref is None:
        return value
    ref = _required_string(raw_ref, f"{source}.$ref")
    prefix = "#/components/parameters/"
    if not ref.startswith(prefix):
        raise SwaggerRegistryError(f"{source}: поддерживаются только локальные parameter refs.")
    parameter_name = ref.removeprefix(prefix)
    components = _require_mapping(spec.get("components"), "components")
    parameters = _require_mapping(components.get("parameters"), "components.parameters")
    return _require_mapping(parameters.get(parameter_name), ref)


def _optional_sequence(value: object, source: str) -> tuple[object, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise SwaggerRegistryError(f"{source} должно быть списком.")
    return tuple(value)


def _require_mapping(value: object, source: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise SwaggerRegistryError(f"{source} должно быть JSON object.")
    return cast(JsonObject, value)


def _required_string(value: object, source: str) -> str:
    if not isinstance(value, str) or not value:
        raise SwaggerRegistryError(f"{source} должно быть непустой строкой.")
    return value


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


__all__ = (
    "DEFAULT_SWAGGER_API_DIR",
    "SwaggerOperation",
    "SwaggerParameter",
    "SwaggerRegistry",
    "SwaggerRegistryError",
    "SwaggerRequestBody",
    "SwaggerSpec",
    "SwaggerValidationError",
    "load_swagger_registry",
    "normalize_swagger_method",
    "normalize_swagger_path",
)
