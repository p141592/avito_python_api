"""Validation rules for Swagger operation bindings."""

from __future__ import annotations

import importlib
import inspect
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence

from avito.client import AvitoClient
from avito.core.deprecation import DeprecatedSdkSymbol
from avito.core.swagger_discovery import DiscoveredSwaggerBinding, SwaggerBindingDiscovery
from avito.core.swagger_registry import SwaggerOperation, SwaggerRegistry
from avito.core.swagger_report import SwaggerReportError

_TEST_CONSTANTS = frozenset(
    {
        "account_id",
        "action_id",
        "call_id",
        "campaign_id",
        "chat_id",
        "dictionary_id",
        "item_id",
        "limit",
        "message_id",
        "order_id",
        "parcel_id",
        "report_id",
        "resume_id",
        "scoring_id",
        "tariff_id",
        "task_id",
        "user_id",
        "url",
        "vacancy_id",
        "value",
        "vehicle_id",
    }
)


def lint_swagger_bindings(
    registry: SwaggerRegistry,
    discovery: SwaggerBindingDiscovery,
    *,
    strict: bool = False,
) -> tuple[SwaggerReportError, ...]:
    """Validate discovered SDK bindings against the Swagger registry."""

    operations_by_key = {operation.key: operation for operation in registry.operations}
    spec_names = {spec.name for spec in registry.specs}
    errors: list[SwaggerReportError] = []

    errors.extend(_validate_duplicate_bindings(discovery.bindings))
    if strict:
        errors.extend(_validate_complete_bindings(registry.operations, discovery.bindings))
    for binding in discovery.bindings:
        operation = _resolve_bound_operation(
            binding=binding,
            operations_by_key=operations_by_key,
            spec_names=spec_names,
            errors=errors,
        )
        sdk_method = _load_sdk_method(binding)
        if operation is not None:
            errors.extend(_validate_operation_metadata(binding, operation, sdk_method))
            errors.extend(_validate_binding_expressions(binding, operation))
        errors.extend(_validate_factory(binding))
        errors.extend(_validate_sdk_method_signature(binding, sdk_method))

    return tuple(errors)


def _validate_complete_bindings(
    operations: Sequence[SwaggerOperation],
    bindings: Sequence[DiscoveredSwaggerBinding],
) -> tuple[SwaggerReportError, ...]:
    bound_operation_keys = {
        binding.operation_key for binding in bindings if binding.operation_key is not None
    }
    errors: list[SwaggerReportError] = []
    for operation in operations:
        if operation.key in bound_operation_keys:
            continue
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_MISSING",
                message=f"{operation.key}: для Swagger operation не найден SDK binding.",
                operation_key=operation.key,
                sdk_method=None,
            )
        )
    return tuple(errors)


def _validate_duplicate_bindings(
    bindings: Sequence[DiscoveredSwaggerBinding],
) -> tuple[SwaggerReportError, ...]:
    grouped: defaultdict[str, list[DiscoveredSwaggerBinding]] = defaultdict(list)
    for binding in bindings:
        if binding.operation_key is not None:
            grouped[binding.operation_key].append(binding)

    errors: list[SwaggerReportError] = []
    for operation_key, operation_bindings in sorted(grouped.items()):
        if len(operation_bindings) < 2:
            continue
        methods = ", ".join(binding.sdk_method for binding in operation_bindings)
        for binding in operation_bindings:
            errors.append(
                SwaggerReportError(
                    code="SWAGGER_BINDING_DUPLICATE",
                    message=(
                        f"{operation_key}: несколько SDK binding-ов указывают на одну "
                        f"Swagger operation: {methods}."
                    ),
                    operation_key=operation_key,
                    sdk_method=binding.sdk_method,
                )
            )
    return tuple(errors)


def _resolve_bound_operation(
    *,
    binding: DiscoveredSwaggerBinding,
    operations_by_key: Mapping[str, SwaggerOperation],
    spec_names: set[str],
    errors: list[SwaggerReportError],
) -> SwaggerOperation | None:
    if binding.operation_key is None:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_AMBIGUOUS",
                message=(
                    f"{binding.sdk_method}: Swagger operation нельзя определить однозначно. "
                    "Укажите `spec` в binding или class-level metadata."
                ),
                operation_key=None,
                sdk_method=binding.sdk_method,
            )
        )
        return None

    if binding.spec not in spec_names:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_SPEC_NOT_FOUND",
                message=f"{binding.sdk_method}: Swagger spec не найден: {binding.spec}.",
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            )
        )
        return None

    operation = operations_by_key.get(binding.operation_key)
    if operation is None:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_NOT_FOUND",
                message=(
                    f"{binding.sdk_method}: Swagger operation не найдена: {binding.operation_key}."
                ),
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            )
        )
    return operation


def _validate_operation_metadata(
    binding: DiscoveredSwaggerBinding,
    operation: SwaggerOperation,
    sdk_method: Callable[..., object] | None,
) -> tuple[SwaggerReportError, ...]:
    errors: list[SwaggerReportError] = []
    if binding.operation_id is not None and binding.operation_id != operation.operation_id:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_OPERATION_ID_MISMATCH",
                message=(
                    f"{binding.sdk_method}: operation_id `{binding.operation_id}` "
                    f"не совпадает со Swagger operation_id `{operation.operation_id}`."
                ),
                operation_key=operation.key,
                sdk_method=binding.sdk_method,
            )
        )
    if binding.deprecated != operation.deprecated:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_DEPRECATED_MISMATCH",
                message=(
                    f"{binding.sdk_method}: deprecated={binding.deprecated} не совпадает "
                    f"со Swagger deprecated={operation.deprecated}."
                ),
                operation_key=operation.key,
                sdk_method=binding.sdk_method,
            )
        )
    if binding.legacy and not operation.deprecated:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_LEGACY_MISMATCH",
                message=(
                    f"{binding.sdk_method}: legacy=True разрешён только для deprecated "
                    "Swagger operation или явного исключения."
                ),
                operation_key=operation.key,
                sdk_method=binding.sdk_method,
            )
        )
    if operation.deprecated and not binding.legacy:
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_LEGACY_REQUIRED",
                message=(
                    f"{binding.sdk_method}: deprecated Swagger operation должна иметь "
                    "legacy=True в binding."
                ),
                operation_key=operation.key,
                sdk_method=binding.sdk_method,
            )
        )
    if operation.deprecated and not _has_runtime_deprecation(sdk_method):
        errors.append(
            SwaggerReportError(
                code="SWAGGER_BINDING_DEPRECATION_WARNING_MISSING",
                message=(
                    f"{binding.sdk_method}: deprecated public method должен иметь runtime "
                    "DeprecationWarning через `deprecated_method`."
                ),
                operation_key=operation.key,
                sdk_method=binding.sdk_method,
            )
        )
    return tuple(errors)


def _validate_factory(binding: DiscoveredSwaggerBinding) -> tuple[SwaggerReportError, ...]:
    if binding.domain == "auth" and binding.factory is None:
        return ()
    if binding.factory is None:
        return (
            SwaggerReportError(
                code="SWAGGER_BINDING_FACTORY_MISSING",
                message=f"{binding.sdk_method}: binding должен указывать AvitoClient factory.",
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            ),
        )

    factory = getattr(AvitoClient, binding.factory, None)
    if not callable(factory):
        return (
            SwaggerReportError(
                code="SWAGGER_BINDING_FACTORY_NOT_FOUND",
                message=f"{binding.sdk_method}: AvitoClient factory не найден: {binding.factory}.",
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            ),
        )

    return _validate_signature_mapping(
        binding=binding,
        signature=inspect.signature(factory),
        mapping=binding.factory_args,
        subject=f"factory `{binding.factory}`",
        code_prefix="SWAGGER_BINDING_FACTORY",
    )


def _validate_sdk_method_signature(
    binding: DiscoveredSwaggerBinding,
    sdk_method: Callable[..., object] | None,
) -> tuple[SwaggerReportError, ...]:
    if sdk_method is None:
        return (
            SwaggerReportError(
                code="SWAGGER_BINDING_SDK_METHOD_NOT_FOUND",
                message=f"{binding.sdk_method}: SDK method не найден при signature validation.",
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            ),
        )
    return _validate_signature_mapping(
        binding=binding,
        signature=inspect.signature(sdk_method),
        mapping=binding.method_args,
        subject="SDK method",
        code_prefix="SWAGGER_BINDING_METHOD",
    )


def _validate_binding_expressions(
    binding: DiscoveredSwaggerBinding,
    operation: SwaggerOperation,
) -> tuple[SwaggerReportError, ...]:
    errors: list[SwaggerReportError] = []
    errors.extend(
        _validate_expression_mapping(
            binding=binding,
            operation=operation,
            mapping=binding.factory_args,
            subject="factory_args",
        )
    )
    errors.extend(
        _validate_expression_mapping(
            binding=binding,
            operation=operation,
            mapping=binding.method_args,
            subject="method_args",
        )
    )
    return tuple(errors)


def _validate_expression_mapping(
    *,
    binding: DiscoveredSwaggerBinding,
    operation: SwaggerOperation,
    mapping: Mapping[str, str],
    subject: str,
) -> tuple[SwaggerReportError, ...]:
    errors: list[SwaggerReportError] = []
    for argument_name, expression in sorted(mapping.items()):
        errors.extend(
            _validate_expression(
                binding=binding,
                operation=operation,
                subject=subject,
                argument_name=argument_name,
                expression=expression,
            )
        )
    return tuple(errors)


def _validate_expression(
    *,
    binding: DiscoveredSwaggerBinding,
    operation: SwaggerOperation,
    subject: str,
    argument_name: str,
    expression: str,
) -> tuple[SwaggerReportError, ...]:
    if expression == "body":
        if operation.request_body is None:
            return (
                _expression_error(
                    binding=binding,
                    code="SWAGGER_BINDING_BODY_MISSING",
                    message=(
                        f"{binding.sdk_method}: {subject}.{argument_name} указывает на "
                        "`body`, но Swagger operation не содержит requestBody."
                    ),
                ),
            )
        return ()

    prefix, separator, field_name = expression.partition(".")
    if not separator or not field_name:
        return (
            _expression_error(
                binding=binding,
                code="SWAGGER_BINDING_EXPRESSION_INVALID",
                message=(
                    f"{binding.sdk_method}: {subject}.{argument_name} содержит "
                    f"некорректное expression `{expression}`."
                ),
            ),
        )

    if prefix == "path":
        return _validate_parameter_expression(
            binding=binding,
            operation=operation,
            subject=subject,
            argument_name=argument_name,
            expression=expression,
            field_name=field_name,
            location="path",
        )
    if prefix == "query":
        return _validate_parameter_expression(
            binding=binding,
            operation=operation,
            subject=subject,
            argument_name=argument_name,
            expression=expression,
            field_name=field_name,
            location="query",
        )
    if prefix == "header":
        return _validate_parameter_expression(
            binding=binding,
            operation=operation,
            subject=subject,
            argument_name=argument_name,
            expression=expression,
            field_name=field_name,
            location="header",
        )
    if prefix == "body":
        if operation.request_body is None:
            return (
                _expression_error(
                    binding=binding,
                    code="SWAGGER_BINDING_BODY_MISSING",
                    message=(
                        f"{binding.sdk_method}: {subject}.{argument_name} указывает на "
                        f"`{expression}`, но Swagger operation не содержит requestBody."
                    ),
                ),
            )
        return ()
    if prefix == "constant":
        if field_name not in _TEST_CONSTANTS:
            return (
                _expression_error(
                    binding=binding,
                    code="SWAGGER_BINDING_CONSTANT_NOT_FOUND",
                    message=(
                        f"{binding.sdk_method}: {subject}.{argument_name} указывает на "
                        f"неизвестную test constant `{field_name}`."
                    ),
                ),
            )
        return ()
    return (
        _expression_error(
            binding=binding,
            code="SWAGGER_BINDING_EXPRESSION_UNKNOWN",
            message=(
                f"{binding.sdk_method}: {subject}.{argument_name} использует "
                f"запрещённый expression prefix `{prefix}`."
            ),
        ),
    )


def _validate_parameter_expression(
    *,
    binding: DiscoveredSwaggerBinding,
    operation: SwaggerOperation,
    subject: str,
    argument_name: str,
    expression: str,
    field_name: str,
    location: str,
) -> tuple[SwaggerReportError, ...]:
    parameter_names = {
        parameter.name for parameter in operation.parameters if parameter.location == location
    }
    if field_name in parameter_names:
        return ()
    return (
        _expression_error(
            binding=binding,
            code=f"SWAGGER_BINDING_{location.upper()}_PARAMETER_NOT_FOUND",
            message=(
                f"{binding.sdk_method}: {subject}.{argument_name} указывает на "
                f"`{expression}`, но Swagger operation не содержит {location}-parameter "
                f"`{field_name}`."
            ),
        ),
    )


def _expression_error(
    *,
    binding: DiscoveredSwaggerBinding,
    code: str,
    message: str,
) -> SwaggerReportError:
    return SwaggerReportError(
        code=code,
        message=message,
        operation_key=binding.operation_key,
        sdk_method=binding.sdk_method,
    )


def _load_sdk_method(binding: DiscoveredSwaggerBinding) -> Callable[..., object] | None:
    module = importlib.import_module(binding.module)
    cls = getattr(module, binding.class_name, None)
    method = getattr(cls, binding.method_name, None)
    return method if callable(method) else None


def _has_runtime_deprecation(method: Callable[..., object] | None) -> bool:
    metadata = getattr(method, "__sdk_deprecation__", None)
    return isinstance(metadata, DeprecatedSdkSymbol)


def _validate_signature_mapping(
    *,
    binding: DiscoveredSwaggerBinding,
    signature: inspect.Signature,
    mapping: Mapping[str, str],
    subject: str,
    code_prefix: str,
) -> tuple[SwaggerReportError, ...]:
    parameters = _mappable_parameters(signature)
    parameter_names = set(parameters)
    errors: list[SwaggerReportError] = []

    for argument_name in sorted(set(mapping) - parameter_names):
        errors.append(
            SwaggerReportError(
                code=f"{code_prefix}_ARG_UNKNOWN",
                message=(
                    f"{binding.sdk_method}: {subject} не содержит параметр `{argument_name}`."
                ),
                operation_key=binding.operation_key,
                sdk_method=binding.sdk_method,
            )
        )

    for argument_name, parameter in parameters.items():
        if parameter.default is not inspect.Parameter.empty:
            continue
        if argument_name not in mapping:
            errors.append(
                SwaggerReportError(
                    code=f"{code_prefix}_ARG_REQUIRED",
                    message=(
                        f"{binding.sdk_method}: обязательный параметр {subject} "
                        f"`{argument_name}` не покрыт mapping-ом."
                    ),
                    operation_key=binding.operation_key,
                    sdk_method=binding.sdk_method,
                )
            )
    return tuple(errors)


def _mappable_parameters(
    signature: inspect.Signature,
) -> Mapping[str, inspect.Parameter]:
    return {
        name: parameter
        for name, parameter in signature.parameters.items()
        if name != "self"
        and parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
    }


__all__ = ("lint_swagger_bindings",)
