from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from avito.accounts.domain import Account, AccountHierarchy
from avito.ads.domain import AutoloadArchive
from avito.core.swagger import SwaggerOperationBinding
from avito.core.swagger_discovery import (
    DiscoveredSwaggerBinding,
    SwaggerBindingDiscovery,
    discover_swagger_bindings,
)
from avito.core.swagger_linter import lint_swagger_bindings
from avito.core.swagger_registry import (
    SwaggerOperation,
    SwaggerRegistry,
    SwaggerRequestBody,
    SwaggerResponse,
    SwaggerSpec,
    load_swagger_registry,
)


@contextmanager
def _temporary_binding(
    cls: type[object],
    method_name: str,
    binding: SwaggerOperationBinding,
    *,
    spec: str | None = "Информацияопользователе.json",
    factory: str | None = "account",
) -> Iterator[None]:
    method = getattr(cls, method_name)
    original_binding = getattr(method, "__swagger_binding__", None)
    original_domain = getattr(cls, "__swagger_domain__", None)
    original_spec = getattr(cls, "__swagger_spec__", None)
    original_factory = getattr(cls, "__sdk_factory__", None)
    method.__swagger_binding__ = binding
    cls.__swagger_domain__ = "accounts"
    _set_optional_class_attribute(cls, "__swagger_spec__", spec)
    _set_optional_class_attribute(cls, "__sdk_factory__", factory)
    try:
        yield
    finally:
        if original_binding is None:
            delattr(method, "__swagger_binding__")
        else:
            method.__swagger_binding__ = original_binding
        _restore_class_attribute(cls, "__swagger_domain__", original_domain)
        _restore_class_attribute(cls, "__swagger_spec__", original_spec)
        _restore_class_attribute(cls, "__sdk_factory__", original_factory)


@contextmanager
def _temporary_account_bindings(
    bindings: dict[str, SwaggerOperationBinding],
) -> Iterator[None]:
    original_bindings = {
        method_name: getattr(getattr(Account, method_name), "__swagger_binding__", None)
        for method_name in bindings
    }
    original_domain = getattr(Account, "__swagger_domain__", None)
    original_spec = getattr(Account, "__swagger_spec__", None)
    original_factory = getattr(Account, "__sdk_factory__", None)
    Account.__swagger_domain__ = "accounts"
    Account.__swagger_spec__ = "Информацияопользователе.json"
    Account.__sdk_factory__ = "account"
    for method_name, binding in bindings.items():
        getattr(Account, method_name).__swagger_binding__ = binding
    try:
        yield
    finally:
        for method_name, original_binding in original_bindings.items():
            method = getattr(Account, method_name)
            if original_binding is None:
                delattr(method, "__swagger_binding__")
            else:
                method.__swagger_binding__ = original_binding
        _restore_class_attribute(Account, "__swagger_domain__", original_domain)
        _restore_class_attribute(Account, "__swagger_spec__", original_spec)
        _restore_class_attribute(Account, "__sdk_factory__", original_factory)


def _set_optional_class_attribute(cls: type[object], name: str, value: str | None) -> None:
    if value is None:
        if hasattr(cls, name):
            delattr(cls, name)
        return
    setattr(cls, name, value)


def _restore_class_attribute(cls: type[object], name: str, value: object) -> None:
    if value is None:
        if hasattr(cls, name):
            delattr(cls, name)
        return
    setattr(cls, name, value)


def test_lint_swagger_bindings_allows_empty_discovery_in_non_strict_mode() -> None:
    registry = load_swagger_registry()
    discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert errors == ()


def test_lint_swagger_bindings_rejects_unknown_spec() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(method="GET", path="/core/v1/accounts/self")

    with _temporary_binding(Account, "get_self", binding, spec="НетТакогоSpec.json"):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert [error.code for error in errors] == ["SWAGGER_BINDING_SPEC_NOT_FOUND"]


def test_lint_swagger_bindings_rejects_missing_operation() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(method="GET", path="/missing")

    with _temporary_binding(Account, "get_self", binding):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert [error.code for error in errors] == ["SWAGGER_BINDING_NOT_FOUND"]


def test_lint_swagger_bindings_rejects_duplicate_operation_bindings() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(method="GET", path="/core/v1/accounts/self")

    with _temporary_account_bindings({"get_self": binding, "get_balance": binding}):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert [error.code for error in errors] == [
        "SWAGGER_BINDING_DUPLICATE",
        "SWAGGER_BINDING_DUPLICATE",
    ]


def test_lint_swagger_bindings_rejects_one_sdk_method_bound_to_multiple_operations() -> None:
    registry = load_swagger_registry()
    discovery = discover_swagger_bindings(registry=registry)
    first = discovery.bindings[0]
    duplicate_sdk_method = type(first)(
        module=first.module,
        class_name=first.class_name,
        method_name=first.method_name,
        domain=first.domain,
        operation_key="Информацияопользователе.json GET /core/v1/accounts/{user_id}/balance",
        spec="Информацияопользователе.json",
        method="GET",
        path="/core/v1/accounts/{user_id}/balance",
        operation_id="getUserBalance",
        factory=first.factory,
        factory_args=first.factory_args,
        method_args=first.method_args,
        deprecated=first.deprecated,
        legacy=first.legacy,
    )
    patched_discovery = type(discovery)(
        bindings=(first, duplicate_sdk_method),
        legacy_binding_methods=(),
    )

    errors = lint_swagger_bindings(registry, patched_discovery)

    assert _codes_for(errors, first.sdk_method, exclude={"SWAGGER_BINDING_DUPLICATE"}) == [
        "SWAGGER_BINDING_METHOD_MULTIPLE",
        "SWAGGER_BINDING_METHOD_MULTIPLE",
    ]


def test_lint_swagger_bindings_rejects_legacy_stacked_metadata() -> None:
    registry = load_swagger_registry()
    discovery = type(discover_swagger_bindings(registry=registry))(
        bindings=(),
        legacy_binding_methods=("avito.accounts.domain.Account.get_self",),
    )

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(errors, "avito.accounts.domain.Account.get_self") == [
        "SWAGGER_BINDING_METHOD_MULTIPLE"
    ]


def test_lint_swagger_bindings_rejects_metadata_mismatches() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="GET",
        path="/core/v1/accounts/self",
        operation_id="wrongOperationId",
        deprecated=True,
        legacy=True,
    )

    with _temporary_binding(Account, "get_self", binding):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert [error.code for error in errors] == [
        "SWAGGER_BINDING_OPERATION_ID_MISMATCH",
        "SWAGGER_BINDING_DEPRECATED_MISMATCH",
        "SWAGGER_BINDING_LEGACY_MISMATCH",
    ]


def test_lint_swagger_bindings_rejects_missing_and_unknown_factory() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(method="GET", path="/core/v1/accounts/self")

    with _temporary_binding(Account, "get_self", binding, factory=None):
        discovery = discover_swagger_bindings(registry=registry)
    missing_errors = lint_swagger_bindings(registry, discovery)

    with _temporary_binding(Account, "get_self", binding, factory="missing_factory"):
        discovery = discover_swagger_bindings(registry=registry)
    unknown_errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(missing_errors, "avito.accounts.domain.Account.get_self") == [
        "SWAGGER_BINDING_FACTORY_MISSING"
    ]
    assert _codes_for(unknown_errors, "avito.accounts.domain.Account.get_self") == [
        "SWAGGER_BINDING_FACTORY_NOT_FOUND"
    ]


def test_lint_swagger_bindings_validates_factory_and_method_signatures() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="POST",
        path="/linkItemsV1",
        spec="ИерархияАккаунтов.json",
        factory_args={"unknown": "constant.value"},
        method_args={"employee_id": "body.employee_id", "unknown": "constant.value"},
    )

    with _temporary_binding(
        AccountHierarchy,
        "link_items",
        binding,
        spec=None,
        factory="account_hierarchy",
    ):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(
        errors,
        "avito.accounts.domain.AccountHierarchy.link_items",
        exclude={"SWAGGER_BINDING_DUPLICATE"},
    ) == [
        "SWAGGER_BINDING_FACTORY_ARG_UNKNOWN",
        "SWAGGER_BINDING_METHOD_ARG_UNKNOWN",
        "SWAGGER_BINDING_METHOD_ARG_REQUIRED",
    ]


def test_lint_swagger_bindings_validates_parameter_expressions_against_swagger() -> None:
    registry = load_swagger_registry()
    cases = {
        "path": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "path.missing"},
            ),
            "SWAGGER_BINDING_PATH_PARAMETER_NOT_FOUND",
        ),
        "query": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "query.missing"},
            ),
            "SWAGGER_BINDING_QUERY_PARAMETER_NOT_FOUND",
        ),
        "header": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "header.missing"},
            ),
            "SWAGGER_BINDING_HEADER_PARAMETER_NOT_FOUND",
        ),
    }

    for case_name, (binding, expected_code) in cases.items():
        with _temporary_binding(Account, "get_balance", binding):
            discovery = discover_swagger_bindings(registry=registry)

        errors = lint_swagger_bindings(registry, discovery)

        assert _codes_for(
            errors,
            "avito.accounts.domain.Account.get_balance",
            exclude={"SWAGGER_BINDING_DUPLICATE"},
        ) == [expected_code], case_name


def test_lint_swagger_bindings_validates_body_and_constant_expressions() -> None:
    registry = load_swagger_registry()
    cases = {
        "body": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "body.user_id"},
            ),
            "SWAGGER_BINDING_BODY_MISSING",
        ),
        "constant": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "constant.missing"},
            ),
            "SWAGGER_BINDING_CONSTANT_NOT_FOUND",
        ),
        "unknown_prefix": (
            SwaggerOperationBinding(
                method="GET",
                path="/core/v1/accounts/{user_id}/balance",
                method_args={"user_id": "cookie.user_id"},
            ),
            "SWAGGER_BINDING_EXPRESSION_UNKNOWN",
        ),
    }

    for case_name, (binding, expected_code) in cases.items():
        with _temporary_binding(Account, "get_balance", binding):
            discovery = discover_swagger_bindings(registry=registry)

        errors = lint_swagger_bindings(registry, discovery)

        assert _codes_for(
            errors,
            "avito.accounts.domain.Account.get_balance",
            exclude={"SWAGGER_BINDING_DUPLICATE"},
        ) == [expected_code], case_name


def test_lint_swagger_bindings_allows_valid_body_and_constant_expressions() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="POST",
        path="/core/v1/accounts/operations_history",
        method_args={"date_from": "body.date_time_from"},
        factory_args={"user_id": "constant.user_id"},
    )

    with _temporary_binding(Account, "get_operations_history", binding):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(
        errors,
        "avito.accounts.domain.Account.get_operations_history",
        exclude={"SWAGGER_BINDING_DUPLICATE"},
    ) == []


def test_lint_swagger_bindings_rejects_unknown_body_field() -> None:
    registry, discovery = _single_body_field_discovery(
        expression="body.missing",
        request_body=SwaggerRequestBody(
            required=True,
            content_types=("application/json",),
            field_names=("employeeId", "employee_id"),
            schema_extracted=True,
        ),
    )

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(errors, "avito.accounts.domain.AccountHierarchy.link_items") == [
        "SWAGGER_BINDING_BODY_FIELD_NOT_FOUND"
    ]


def test_lint_swagger_bindings_rejects_unsupported_body_schema_for_field_expression() -> None:
    registry, discovery = _single_body_field_discovery(
        expression="body.employee_id",
        item_ids_expression="body",
        request_body=SwaggerRequestBody(
            required=True,
            content_types=("application/json",),
            field_names=(),
            schema_extracted=False,
        ),
    )

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(errors, "avito.accounts.domain.AccountHierarchy.link_items") == [
        "SWAGGER_BINDING_BODY_SCHEMA_UNSUPPORTED"
    ]


def test_lint_swagger_bindings_allows_whole_body_expression_with_unsupported_schema() -> None:
    registry, discovery = _single_body_field_discovery(
        expression="body",
        item_ids_expression="body",
        request_body=SwaggerRequestBody(
            required=True,
            content_types=("application/json",),
            field_names=(),
            schema_extracted=False,
        ),
    )

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(errors, "avito.accounts.domain.AccountHierarchy.link_items") == []


def test_lint_swagger_bindings_requires_legacy_for_deprecated_operation() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="GET",
        path="/autoload/v1/profile",
        spec="Автозагрузка.json",
        operation_id="getProfile",
        factory="autoload_archive",
        deprecated=True,
    )

    with _temporary_binding(
        AutoloadArchive,
        "get_profile",
        binding,
        spec=None,
        factory=None,
    ):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(errors, "avito.ads.domain.AutoloadArchive.get_profile") == [
        "SWAGGER_BINDING_LEGACY_REQUIRED"
    ]


def test_lint_swagger_bindings_requires_runtime_warning_for_deprecated_operation() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="GET",
        path="/autoload/v1/profile",
        spec="Автозагрузка.json",
        operation_id="getProfile",
        factory="account",
        deprecated=True,
        legacy=True,
    )

    with _temporary_binding(
        Account,
        "get_self",
        binding,
        spec=None,
        factory=None,
    ):
        discovery = discover_swagger_bindings(registry=registry)

    errors = lint_swagger_bindings(registry, discovery)

    assert _codes_for(
        errors,
        "avito.accounts.domain.Account.get_self",
        exclude={"SWAGGER_BINDING_DUPLICATE"},
    ) == ["SWAGGER_BINDING_DEPRECATION_WARNING_MISSING"]


def _codes_for(
    errors: object,
    sdk_method: str,
    *,
    exclude: set[str] | None = None,
) -> list[str]:
    excluded = exclude or set()
    return [
        error.code
        for error in errors
        if error.sdk_method == sdk_method and error.code not in excluded
    ]


def _single_body_field_discovery(
    *,
    expression: str,
    item_ids_expression: str = "body.employee_id",
    request_body: SwaggerRequestBody,
) -> tuple[SwaggerRegistry, SwaggerBindingDiscovery]:
    operation = SwaggerOperation(
        spec="ИерархияАккаунтов.json",
        method="POST",
        path="/linkItemsV1",
        operation_id="linkItemsV1",
        deprecated=False,
        parameters=(),
        request_body=request_body,
        responses=(SwaggerResponse(status_code="204", content_types=()),),
    )
    registry = SwaggerRegistry(
        specs=(
            SwaggerSpec(
                name="ИерархияАккаунтов.json",
                path=load_swagger_registry().specs[0].path,
                operations=(operation,),
            ),
        )
    )
    discovery = SwaggerBindingDiscovery(
        bindings=(
            DiscoveredSwaggerBinding(
                module="avito.accounts.domain",
                class_name="AccountHierarchy",
                method_name="link_items",
                domain="accounts",
                operation_key=operation.key,
                spec=operation.spec,
                method=operation.method,
                path=operation.path,
                operation_id=operation.operation_id,
                factory="account_hierarchy",
                factory_args={},
                method_args={"employee_id": expression, "item_ids": item_ids_expression},
            ),
        )
    )
    return registry, discovery
