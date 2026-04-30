from __future__ import annotations

from pathlib import Path

from inventory_architecture import build_inventory_report, render_text_report


def test_build_inventory_report_captures_phase_zero_baseline() -> None:
    report = build_inventory_report(Path("."))

    summary = report["summary"]
    assert isinstance(summary, dict)
    assert summary["api_domain_count"] == 11
    assert summary["legacy_file_count"] == 0
    assert summary["swagger_total_operation_count"] == 204
    assert summary["swagger_operation_count"] == 200

    domains = report["domains"]
    assert isinstance(domains, dict)
    tariffs = domains["tariffs"]
    assert isinstance(tariffs, dict)
    assert tariffs["legacy_files"] == []
    assert tariffs["public_method_count"] == 1
    assert tariffs["swagger_binding_count"] == 1
    assert tariffs["swagger_operation_count"] == 1


def test_render_text_report_includes_domain_table() -> None:
    report = build_inventory_report(Path("."))

    output = render_text_report(report)

    assert "Architecture inventory baseline" in output
    assert "| Domain | Legacy files | Public methods |" in output
    assert "| tariffs | 0 | 1 | 1 | 1 | - |" in output
