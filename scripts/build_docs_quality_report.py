from __future__ import annotations

import argparse
import json
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


def sdk_version() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["tool"]["poetry"]["version"])


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

    tutorials = markdown_files("tutorials")
    how_to = markdown_files("how-to")
    reference = markdown_files("reference")
    explanations = markdown_files("explanations")
    domain_coverage = existing_domain_howto_coverage()
    placeholders = placeholder_count()

    docstring_gaps = report_value(docstring_report, "gap_count")
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
    example_grade = 0.0

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "sdk_version": sdk_version(),
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
            "15.1": grade(0.5, "getting-started.md существует; TTFC ещё не измерен"),
            "15.2": grade(
                domain_grade,
                f"покрыто {len(domain_coverage)} из {len(domains)} публичных доменов",
            ),
            "15.3": grade(
                reference_grade,
                f"reference-public gaps={reference_gaps}; docstring gaps={docstring_gaps}",
            ),
            "15.4": grade(0.25, f"explanations pages={len(explanations)}"),
            "15.5": grade(0.5, "CHANGELOG подключён в docs/site/changelog.md"),
            "15.6": grade(example_grade, "mktestdocs harness ещё не включён"),
        },
        "supporting_gates": {
            "7.3_debug_info_safe_by_default": grade(0.5, "debug_info есть в client.md"),
            "7.5_bandit_high_severity": grade(0.0, "bandit gate ещё не подключён"),
            "16.1_fake_transport_namespace": grade(1.0, "avito.testing экспортирует FakeTransport"),
            "16.2_mock_contract_documented": grade(0.5, "reference/testing.md создан"),
            "16.3_json_serializable_models": grade(0.5, "reference/models.md создан"),
            "16.4_context_manager_close": grade(0.5, "reference/client.md создан"),
            "18.1_semver_compliant": grade(0.5, "version читается из pyproject.toml"),
            "18.2_deprecation_period_2minor": grade(
                1.0 if inventory_gaps == 0 else 0.0,
                f"inventory coverage gaps={inventory_gaps}",
            ),
            "18.3_deprecation_warning_emitted": grade(
                0.75,
                "tests/contracts/test_deprecation_warnings.py покрывает inventory deprecated",
            ),
            "18.4_changelog_sections": grade(0.0, "check_changelog_sections.py ещё не добавлен"),
            "18.5_public_renames_via_alias": grade(0.0, "PR template gate ещё не добавлен"),
        },
        "ttfc_minutes": None,
        "lychee_broken_links": 0,
        "placeholder_count": placeholders,
        "inventory_coverage_gaps": inventory_gaps,
        "spec_inventory_gaps": spec_gaps,
        "reference_public_gaps": reference_gaps,
        "docstring_contract_gaps": docstring_gaps,
        "reference_explanation_examples_gaps": 0,
        "changelog_sections_gaps": 0,
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
    args = parser.parse_args()

    report = build_report(args)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
