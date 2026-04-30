from __future__ import annotations

from avito.client import AvitoClient
from avito.config import AvitoSettings
from avito.core.swagger_discovery import discover_swagger_bindings
from avito.core.swagger_factory_map import build_factory_domain_mapping_report
from avito.core.swagger_registry import load_swagger_registry
from avito.core.swagger_report import build_swagger_binding_report


def test_build_factory_domain_mapping_report_does_not_create_client_or_read_env(
    monkeypatch,
) -> None:
    def fail_init(self: AvitoClient, *args: object, **kwargs: object) -> None:
        raise AssertionError("AvitoClient must not be created during factory mapping")

    def fail_from_env() -> AvitoSettings:
        raise AssertionError("Environment settings must not be read during factory mapping")

    monkeypatch.setattr(AvitoClient, "__init__", fail_init)
    monkeypatch.setattr(AvitoSettings, "from_env", fail_from_env)

    report = build_factory_domain_mapping_report()

    assert report.factories


def test_build_factory_domain_mapping_report_maps_factories_to_domain_classes() -> None:
    report = build_factory_domain_mapping_report()
    factories = {mapping.factory: mapping for mapping in report.factories}

    assert factories["account"].domain_class == "Account"
    assert factories["account"].module == "avito.accounts.domain"
    assert factories["account"].factory_args == ("user_id",)
    assert factories["account"].spec_candidates == ("Информацияопользователе.json",)
    assert factories["chat"].domain_class == "Chat"
    assert factories["chat"].factory_args == ("chat_id", "user_id")
    assert factories["chat"].spec_candidates == ("Мессенджер.json",)
    assert factories["promotion_order"].spec_candidates == ("Продвижение.json",)


def test_build_factory_domain_mapping_report_identifies_summary_and_helper_methods() -> None:
    report = build_factory_domain_mapping_report()
    helper_methods = {helper.method: helper for helper in report.helper_methods}

    assert helper_methods["account_health"].reason == (
        "summary/helper method; no direct upstream Swagger operation"
    )
    assert helper_methods["business_summary"].reason == (
        "summary/helper method; no direct upstream Swagger operation"
    )
    assert helper_methods["capabilities"].reason == (
        "summary/helper method; no direct upstream Swagger operation"
    )
    assert "account" not in helper_methods


def test_swagger_binding_report_includes_factory_mapping_as_non_authoritative_section() -> None:
    registry = load_swagger_registry()
    discovery = discover_swagger_bindings(registry=registry)
    factory_mapping = build_factory_domain_mapping_report()

    report = build_swagger_binding_report(
        registry,
        discovery,
        factory_mapping=factory_mapping,
    ).to_dict()

    assert report["summary"]["operations_total"] == 204
    assert report["factory_mapping"] == factory_mapping.to_dict()
