from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from avito.accounts.domain import Account
from avito.client import AvitoClient
from avito.config import AvitoSettings
from avito.core.swagger import SwaggerOperationBinding
from avito.core.swagger_discovery import discover_swagger_bindings
from avito.core.swagger_registry import load_swagger_registry


@contextmanager
def _temporary_account_binding(
    binding: SwaggerOperationBinding,
) -> Iterator[None]:
    original_binding = getattr(Account.get_self, "__swagger_binding__", None)
    original_domain = getattr(Account, "__swagger_domain__", None)
    original_spec = getattr(Account, "__swagger_spec__", None)
    original_factory = getattr(Account, "__sdk_factory__", None)
    original_factory_args = getattr(Account, "__sdk_factory_args__", None)
    Account.get_self.__swagger_binding__ = binding  # type: ignore[attr-defined]
    Account.__swagger_domain__ = "accounts"
    Account.__swagger_spec__ = "Информацияопользователе.json"
    Account.__sdk_factory__ = "account"
    Account.__sdk_factory_args__ = {"user_id": "constant.user_id"}
    try:
        yield
    finally:
        if original_binding is None:
            delattr(Account.get_self, "__swagger_binding__")
        else:
            Account.get_self.__swagger_binding__ = original_binding  # type: ignore[attr-defined]
        _restore_class_attribute(Account, "__swagger_domain__", original_domain)
        _restore_class_attribute(Account, "__swagger_spec__", original_spec)
        _restore_class_attribute(Account, "__sdk_factory__", original_factory)
        _restore_class_attribute(Account, "__sdk_factory_args__", original_factory_args)


def _restore_class_attribute(cls: type[object], name: str, value: object) -> None:
    if value is None:
        if hasattr(cls, name):
            delattr(cls, name)
        return
    setattr(cls, name, value)


def test_discover_swagger_bindings_returns_empty_result_for_unmarked_sdk() -> None:
    discovery = discover_swagger_bindings()

    assert len(discovery.bindings) == 204
    assert len(discovery.canonical_map) == 204


def test_discover_swagger_bindings_does_not_create_client_or_read_env(
    monkeypatch,
) -> None:
    def fail_init(self: AvitoClient, *args: object, **kwargs: object) -> None:
        raise AssertionError("AvitoClient must not be created during discovery")

    def fail_from_env() -> AvitoSettings:
        raise AssertionError("Environment settings must not be read during discovery")

    monkeypatch.setattr(AvitoClient, "__init__", fail_init)
    monkeypatch.setattr(AvitoSettings, "from_env", fail_from_env)

    discovery = discover_swagger_bindings()

    assert len(discovery.bindings) == 204


def test_discover_swagger_bindings_uses_class_level_defaults() -> None:
    binding = SwaggerOperationBinding(
        method="get",
        path="/core/v1/accounts/self",
        operation_id="getUserInfoSelf",
    )

    with _temporary_account_binding(binding):
        discovery = discover_swagger_bindings()

    discovered = _find_binding(discovery.bindings, "avito.accounts.domain.Account.get_self")
    assert discovered.sdk_method == "avito.accounts.domain.Account.get_self"
    assert discovered.domain == "accounts"
    assert discovered.operation_key == "Информацияопользователе.json GET /core/v1/accounts/self"
    assert discovered.factory == "account"
    assert dict(discovered.factory_args) == {"user_id": "constant.user_id"}
    assert discovered.operation_id == "getUserInfoSelf"


def test_discover_swagger_bindings_auto_resolves_spec_from_registry() -> None:
    binding = SwaggerOperationBinding(
        method="GET",
        path="/core/v1/accounts/self",
        operation_id="getUserInfoSelf",
    )
    registry = load_swagger_registry()

    with _temporary_account_binding(binding):
        delattr(Account, "__swagger_spec__")
        discovery = discover_swagger_bindings(registry=registry)

    discovered = _find_binding(discovery.bindings, "avito.accounts.domain.Account.get_self")
    assert discovered.spec == "Информацияопользователе.json"
    assert discovered.operation_key == "Информацияопользователе.json GET /core/v1/accounts/self"
    assert discovery.canonical_map[discovered.operation_key] == discovered


def _find_binding(bindings: object, sdk_method: str) -> object:
    for binding in bindings:
        if binding.sdk_method == sdk_method:
            return binding
    raise AssertionError(f"Binding not found: {sdk_method}")
