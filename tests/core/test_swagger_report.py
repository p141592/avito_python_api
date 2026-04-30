from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from avito.accounts.domain import Account
from avito.core.swagger import SwaggerOperationBinding
from avito.core.swagger_discovery import discover_swagger_bindings
from avito.core.swagger_registry import load_swagger_registry
from avito.core.swagger_report import build_swagger_binding_report


@contextmanager
def _temporary_account_bindings(
    bindings: dict[str, SwaggerOperationBinding],
    *,
    spec: str | None = "Информацияопользователе.json",
) -> Iterator[None]:
    original_bindings = {
        method_name: getattr(getattr(Account, method_name), "__swagger_binding__", None)
        for method_name in bindings
    }
    original_domain = getattr(Account, "__swagger_domain__", None)
    original_spec = getattr(Account, "__swagger_spec__", None)
    original_factory = getattr(Account, "__sdk_factory__", None)
    Account.__swagger_domain__ = "accounts"
    if spec is None and hasattr(Account, "__swagger_spec__"):
        delattr(Account, "__swagger_spec__")
    elif spec is not None:
        Account.__swagger_spec__ = spec
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


def _restore_class_attribute(cls: type[object], name: str, value: object) -> None:
    if value is None:
        if hasattr(cls, name):
            delattr(cls, name)
        return
    setattr(cls, name, value)


def test_build_swagger_binding_report_marks_current_corpus_as_complete() -> None:
    registry = load_swagger_registry()
    discovery = discover_swagger_bindings(registry=registry)

    report = build_swagger_binding_report(registry, discovery).to_dict()

    assert report["summary"] == {
        "specs": 23,
        "operations_total": 204,
        "deprecated_operations": 7,
        "bound": 204,
        "unbound": 0,
        "duplicate": 0,
        "ambiguous": 0,
    }
    operations = report["operations"]
    assert isinstance(operations, list)
    assert operations[0].keys() >= {
        "spec",
        "method",
        "path",
        "operation_id",
        "deprecated",
        "status",
        "binding",
    }
    assert {operation["status"] for operation in operations} == {"bound"}


def test_build_swagger_binding_report_marks_bound_operation() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="GET",
        path="/core/v1/accounts/self",
        operation_id="getUserInfoSelf",
    )

    with _temporary_account_bindings({"get_self": binding}):
        discovery = discover_swagger_bindings(registry=registry)

    report = build_swagger_binding_report(registry, discovery).to_dict()

    assert report["summary"]["bound"] == 204
    operation = _find_operation(
        report,
        "Информацияопользователе.json GET /core/v1/accounts/self",
    )
    assert operation["status"] == "bound"
    assert operation["binding"]["sdk_method"] == "avito.accounts.domain.Account.get_self"


def test_build_swagger_binding_report_marks_duplicate_bindings() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(
        method="GET",
        path="/core/v1/accounts/self",
        operation_id="getUserInfoSelf",
    )

    with _temporary_account_bindings({"get_self": binding, "get_balance": binding}):
        discovery = discover_swagger_bindings(registry=registry)

    report = build_swagger_binding_report(registry, discovery).to_dict()

    assert report["summary"]["duplicate"] == 1
    operation = _find_operation(
        report,
        "Информацияопользователе.json GET /core/v1/accounts/self",
    )
    assert operation["status"] == "duplicate"
    assert [binding["sdk_method"] for binding in operation["binding"]] == [
        "avito.accounts.domain.Account.get_balance",
        "avito.accounts.domain.Account.get_self",
    ]


def test_build_swagger_binding_report_marks_ambiguous_binding_without_operation_key() -> None:
    registry = load_swagger_registry()
    binding = SwaggerOperationBinding(method="POST", path="/token")

    with _temporary_account_bindings({"get_self": binding}, spec=None):
        discovery = discover_swagger_bindings(registry=registry)

    report = build_swagger_binding_report(registry, discovery).to_dict()

    assert report["summary"]["ambiguous"] == 1
    binding = _find_binding(report, "avito.accounts.domain.Account.get_self")
    assert binding["status"] == "ambiguous"
    assert binding["operation_key"] is None


def _find_operation(report: dict[str, object], operation_key: str) -> dict[str, object]:
    operations = report["operations"]
    assert isinstance(operations, list)
    for operation in operations:
        key = f"{operation['spec']} {operation['method']} {operation['path']}"
        if key == operation_key:
            return operation
    raise AssertionError(f"Operation not found: {operation_key}")


def _find_binding(report: dict[str, object], sdk_method: str) -> dict[str, object]:
    bindings = report["bindings"]
    assert isinstance(bindings, list)
    for binding in bindings:
        if binding["sdk_method"] == sdk_method:
            return binding
    raise AssertionError(f"Binding not found: {sdk_method}")
