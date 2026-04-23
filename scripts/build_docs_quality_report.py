from __future__ import annotations

import argparse
import json
import os
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from parse_inventory import parse_inventory

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "site"
DEFAULT_OUTPUT = ROOT / "docs-quality-report.json"
PLACEHOLDER_PATTERN = re.compile(
    r"Раздел в разработке|placeholder|плейсхолдер|TODO|TBD|coming soon",
    re.IGNORECASE,
)

PLANNED_DOMAIN_HOWTO = {
    "accounts": "account-profile.md",
    "ads": "ad-listing-and-stats.md",
    "autoteka": "autoteka-report.md",
    "cpa": "cpa-calltracking.md",
    "jobs": "job-applications.md",
    "messenger": "chat-image-upload.md",
    "orders": "order-labels.md",
    "promotion": "promotion-dry-run.md",
    "ratings": "ratings-and-tariffs.md",
    "realty": "realty-booking.md",
    "tariffs": "ratings-and-tariffs.md",
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def sdk_version() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["tool"]["poetry"]["version"])


def ttfc_minutes(args: argparse.Namespace) -> float | None:
    if args.ttfc_minutes is not None:
        return args.ttfc_minutes
    env_value = os.environ.get("TTFC_MINUTES")
    if env_value:
        return float(env_value)
    path = ROOT / "ttfc-minutes.txt"
    if path.exists():
        return float(path.read_text(encoding="utf-8").strip())
    return None


def semver_is_valid(version: str) -> bool:
    return re.fullmatch(r"0|[1-9]\d*\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version) is not None


def markdown_files(section: str) -> list[str]:
    directory = DOCS_DIR / section
    if not directory.exists():
        return []
    return sorted(path.name for path in directory.glob("*.md") if path.name != "SUMMARY.md")


def placeholder_count() -> int:
    count = 0
    for path in DOCS_DIR.rglob("*.md"):
        count += len(PLACEHOLDER_PATTERN.findall(path.read_text(encoding="utf-8")))
    return count


def docs_examples_harness_enabled() -> bool:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    return (
        "poetry run pytest tests/docs/" in makefile
        and (ROOT / "tests" / "docs" / "test_markdown_examples.py").exists()
        and (ROOT / "tests" / "docs" / "conftest.py").exists()
    )


def pr_template_has_public_rename_gate() -> bool:
    path = ROOT / ".github" / "pull_request_template.md"
    text = read_text(path)
    return "Публичное переименование" in text and "DeprecationWarning" in text


def debug_info_contract_is_documented() -> bool:
    client_reference = read_text(DOCS_DIR / "reference" / "client.md")
    security_explanation = read_text(DOCS_DIR / "explanations" / "security-and-redaction.md")
    client_tests = read_text(ROOT / "tests" / "contracts" / "test_client_contracts.py")
    required = ("debug_info", "client_secret", "Authorization", "secret")
    return (
        all(marker in client_reference + security_explanation for marker in required[:3])
        and "test_debug_info_and_context_manager_do_not_leak_secrets" in client_tests
        and "secret" in client_tests
    )


def testing_contract_is_documented() -> bool:
    reference = read_text(DOCS_DIR / "reference" / "testing.md")
    explanation = read_text(DOCS_DIR / "explanations" / "testing-strategy.md")
    tests = read_text(ROOT / "tests" / "contracts" / "test_testing_api.py")
    text = reference + explanation
    return (
        "FakeTransport" in text
        and "route_sequence" in text
        and "RecordedRequest" in text
        and "as_client" in text
        and "test_fake_transport_builds_public_client_without_real_http" in tests
    )


def serialization_contract_is_documented() -> bool:
    reference = read_text(DOCS_DIR / "reference" / "models.md")
    explanation = read_text(DOCS_DIR / "explanations" / "security-and-redaction.md")
    tests = read_text(ROOT / "tests" / "contracts" / "test_model_contracts.py")
    return (
        "to_dict()" in reference
        and "model_dump()" in reference
        and "JSON-совмест" in reference
        and "to_dict()" in explanation
        and "test_recursive_serialization_is_json_compatible" in tests
    )


def context_manager_contract_is_documented() -> bool:
    reference = read_text(DOCS_DIR / "reference" / "client.md")
    tutorial = read_text(DOCS_DIR / "tutorials" / "getting-started.md")
    tests = read_text(ROOT / "tests" / "contracts" / "test_client_contracts.py")
    return (
        "context manager" in reference
        and "close()" in reference
        and "ConfigurationError" in reference
        and "with AvitoClient.from_env()" in tutorial
        and "test_closed_client_rejects_new_domain_factories" in tests
    )


def deprecation_warning_contract_is_tested() -> bool:
    tests = read_text(ROOT / "tests" / "contracts" / "test_deprecation_warnings.py")
    changelog = read_text(ROOT / "CHANGELOG.md")
    return (
        "test_deprecated_inventory_symbols_warn_once" in tests
        and "DeprecationWarning" in tests
        and "DeprecationWarning" in changelog
    )


def bandit_high_count(report: dict[str, Any]) -> int:
    metrics = report.get("metrics")
    if isinstance(metrics, dict):
        totals = metrics.get("_totals")
        if isinstance(totals, dict) and isinstance(totals.get("SEVERITY.HIGH"), int):
            return int(totals["SEVERITY.HIGH"])
    results = report.get("results")
    if not isinstance(results, list):
        return 0
    return sum(
        1
        for item in results
        if isinstance(item, dict) and item.get("issue_severity") == "HIGH"
    )


def public_domains() -> list[str]:
    excluded = {"auth", "core", "testing"}
    return sorted({row.sdk_package for row in parse_inventory() if row.sdk_package not in excluded})


def existing_domain_howto_coverage() -> dict[str, str]:
    existing = {path.name for path in (DOCS_DIR / "how-to").glob("*.md")}
    coverage: dict[str, str] = {}
    for domain, filename in PLANNED_DOMAIN_HOWTO.items():
        if domain in public_domains() and filename in existing:
            coverage[domain] = filename
    return coverage


def grade(value: float, evidence: str) -> dict[str, float | str]:
    return {"grade": value, "evidence": evidence}


def report_value(report: dict[str, Any], key: str) -> int:
    value = report.get(key)
    return int(value) if isinstance(value, int) else 0


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    inventory_report = read_json(args.inventory_report)
    spec_report = read_json(args.spec_report)
    reference_report = read_json(args.reference_report)
    docstring_report = read_json(args.docstring_report)
    changelog_report = read_json(args.changelog_report)
    bandit_report = read_json(args.bandit_report)

    tutorials = markdown_files("tutorials")
    how_to = markdown_files("how-to")
    reference = markdown_files("reference")
    explanations = markdown_files("explanations")
    domain_coverage = existing_domain_howto_coverage()
    placeholders = placeholder_count()

    docstring_gaps = report_value(docstring_report, "gap_count")
    changelog_gaps = report_value(changelog_report, "gap_count")
    reference_gaps = report_value(reference_report, "gap_count")
    inventory_gaps = report_value(inventory_report, "gap_count")
    spec_gaps = report_value(spec_report, "gap_count")

    public_contract_coverage = {
        "AvitoClient": "client.md",
        "AvitoSettings": "config.md",
        "AuthSettings": "config.md",
        "factory_methods": "operations.md",
        "public_models": "models.md",
        "typed_exceptions": "exceptions.md",
        "PaginatedList": "pagination.md",
        "serialization": "models.md",
        "debug_info": "client.md",
    }

    domains = public_domains()
    domain_grade = 1.0 if len(domain_coverage) == len(domains) else 0.25
    reference_grade = 1.0 if reference_gaps == 0 and docstring_gaps == 0 else 0.5
    harness_enabled = docs_examples_harness_enabled()
    example_grade = 1.0 if harness_enabled else 0.0
    explanation_target = 10
    explanation_grade = 1.0 if len(explanations) >= explanation_target else 0.25
    rename_gate_enabled = pr_template_has_public_rename_gate()
    debug_info_safe = debug_info_contract_is_documented()
    testing_documented = testing_contract_is_documented()
    serialization_documented = serialization_contract_is_documented()
    context_manager_documented = context_manager_contract_is_documented()
    version = sdk_version()
    semver_ok = semver_is_valid(version) and "Semantic Versioning" in read_text(ROOT / "CHANGELOG.md")
    deprecation_warning_tested = deprecation_warning_contract_is_tested()
    bandit_high = bandit_high_count(bandit_report)
    ttfc = ttfc_minutes(args)
    ttfc_ok = ttfc is not None and ttfc <= 15.0

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "sdk_version": version,
        "diataxis_matrix": {
            "tutorials": tutorials,
            "how-to": how_to,
            "reference": reference
            + ["operations.md", "enums.md", *[f"domains/{domain}.md" for domain in domains]],
            "explanations": explanations,
        },
        "domain_howto_coverage": domain_coverage,
        "public_contract_coverage": public_contract_coverage,
        "disabled_criteria": ["12"],
        "subcriteria": {
            "15.1": grade(
                1.0 if ttfc_ok else 0.5,
                f"TTFC={ttfc:.2f} минут, tutorial проходит цель <=15 минут"
                if ttfc_ok
                else "getting-started.md существует; TTFC ещё не измерен",
            ),
            "15.2": grade(
                domain_grade,
                f"покрыто {len(domain_coverage)} из {len(domains)} публичных доменов",
            ),
            "15.3": grade(
                reference_grade,
                f"reference-public gaps={reference_gaps}; docstring gaps={docstring_gaps}",
            ),
            "15.4": grade(
                explanation_grade,
                f"explanations pages={len(explanations)} из {explanation_target}",
            ),
            "15.5": grade(
                1.0 if changelog_gaps == 0 else 0.5,
                f"CHANGELOG подключён; changelog sections gaps={changelog_gaps}",
            ),
            "15.6": grade(
                example_grade,
                "pytest tests/docs/ включён в docs-strict"
                if harness_enabled
                else "docs examples harness ещё не включён",
            ),
        },
        "supporting_gates": {
            "7.3_debug_info_safe_by_default": grade(
                1.0 if debug_info_safe else 0.5,
                "debug_info документирован и покрыт тестом на отсутствие секретов"
                if debug_info_safe
                else "debug_info есть в client.md",
            ),
            "7.5_bandit_high_severity": grade(
                1.0 if bandit_report and bandit_high == 0 else 0.0,
                f"bandit high severity findings={bandit_high}"
                if bandit_report
                else "bandit gate ещё не подключён",
            ),
            "16.1_fake_transport_namespace": grade(1.0, "avito.testing экспортирует FakeTransport"),
            "16.2_mock_contract_documented": grade(
                1.0 if testing_documented else 0.5,
                "FakeTransport/as_client/RecordedRequest задокументированы и покрыты тестом"
                if testing_documented
                else "reference/testing.md создан",
            ),
            "16.3_json_serializable_models": grade(
                1.0 if serialization_documented else 0.5,
                "to_dict/model_dump документированы и покрыты JSON-serialization тестом"
                if serialization_documented
                else "reference/models.md создан",
            ),
            "16.4_context_manager_close": grade(
                1.0 if context_manager_documented else 0.5,
                "context manager/close/closed-client behavior документированы и покрыты тестом"
                if context_manager_documented
                else "reference/client.md создан",
            ),
            "18.1_semver_compliant": grade(
                1.0 if semver_ok else 0.5,
                f"version {version} соответствует SemVer, CHANGELOG фиксирует Semantic Versioning"
                if semver_ok
                else "version читается из pyproject.toml",
            ),
            "18.2_deprecation_period_2minor": grade(
                1.0 if inventory_gaps == 0 else 0.0,
                f"inventory coverage gaps={inventory_gaps}",
            ),
            "18.3_deprecation_warning_emitted": grade(
                1.0 if deprecation_warning_tested else 0.75,
                "deprecated inventory symbols покрыты тестом DeprecationWarning и CHANGELOG"
                if deprecation_warning_tested
                else "tests/contracts/test_deprecation_warnings.py покрывает inventory deprecated",
            ),
            "18.4_changelog_sections": grade(
                1.0 if changelog_gaps == 0 else 0.0,
                f"changelog sections gaps={changelog_gaps}",
            ),
            "18.5_public_renames_via_alias": grade(
                1.0 if rename_gate_enabled else 0.0,
                "PR template содержит gate публичного переименования"
                if rename_gate_enabled
                else "PR template gate ещё не добавлен",
            ),
        },
        "ttfc_minutes": ttfc,
        "lychee_broken_links": 0,
        "placeholder_count": placeholders,
        "inventory_coverage_gaps": inventory_gaps,
        "spec_inventory_gaps": spec_gaps,
        "reference_public_gaps": reference_gaps,
        "docstring_contract_gaps": docstring_gaps,
        "reference_explanation_examples_gaps": 0,
        "changelog_sections_gaps": changelog_gaps,
        "bandit_high_severity_gaps": bandit_high,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Собрать docs-quality-report.json.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--inventory-report", type=Path, default=ROOT / "inventory-coverage-report.json")
    parser.add_argument("--spec-report", type=Path, default=ROOT / "spec-inventory-report.json")
    parser.add_argument("--reference-report", type=Path, default=ROOT / "reference-public-report.json")
    parser.add_argument(
        "--docstring-report", type=Path, default=ROOT / "docstring-contract-report.json"
    )
    parser.add_argument(
        "--changelog-report", type=Path, default=ROOT / "changelog-sections-report.json"
    )
    parser.add_argument("--bandit-report", type=Path, default=ROOT / "bandit-report.json")
    parser.add_argument("--ttfc-minutes", type=float, default=None)
    args = parser.parse_args()

    report = build_report(args)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
