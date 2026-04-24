from __future__ import annotations

import argparse
import importlib
import inspect
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

from parse_inventory import parse_inventory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reference-public-report.json"
REFERENCE_DIR = ROOT / "docs" / "site" / "reference"
EXCLUDED_PACKAGES = {"auth", "core", "testing"}
GENERATED_PAGES = {"operations.md", "enums.md"}


@dataclass(slots=True, frozen=True)
class ReferenceGap:
    symbol: str
    expected_page: str
    reason: str


def domain_packages() -> list[str]:
    return sorted(
        {
            row.sdk_package
            for row in parse_inventory()
            if row.sdk_package and row.sdk_package not in EXCLUDED_PACKAGES
        }
    )


def public_exports(module_name: str) -> tuple[str, ...]:
    module = importlib.import_module(module_name)
    exports = getattr(module, "__all__", None)
    if not isinstance(exports, tuple):
        return ()
    return exports


def is_enum_symbol(module_name: str, name: str) -> bool:
    module = importlib.import_module(module_name)
    value = getattr(module, name, None)
    return inspect.isclass(value) and issubclass(value, Enum)


def collect_gaps() -> list[ReferenceGap]:
    gaps: list[ReferenceGap] = []

    required_files = {
        "AvitoClient": "client.md",
        "AvitoClient.debug_info": "client.md",
        "AvitoSettings": "config.md",
        "AuthSettings": "config.md",
        "factory_methods": "operations.md",
        "public_models": "models.md",
        "typed_exceptions": "exceptions.md",
        "PaginatedList": "pagination.md",
        "serialization": "models.md",
        "testing": "testing.md",
    }
    for symbol, relative_page in required_files.items():
        if not page_is_available(relative_page):
            gaps.append(ReferenceGap(symbol, relative_page, "reference-страница отсутствует"))

    from avito import AvitoClient

    if not callable(getattr(AvitoClient, "debug_info", None)):
        gaps.append(ReferenceGap("AvitoClient.debug_info", "client.md", "публичный символ отсутствует"))

    packages = domain_packages()
    for package in packages:
        module_name = f"avito.{package}"
        if not public_exports(module_name):
            gaps.append(
                ReferenceGap(module_name, f"domains/{package}.md", "__all__ отсутствует или пуст")
            )
        for name in public_exports(module_name):
            page = "enums.md" if is_enum_symbol(module_name, name) else f"domains/{package}.md"
            if not page_is_available(page):
                gaps.append(ReferenceGap(f"{module_name}.{name}", page, "reference-страница отсутствует"))

    for name in public_exports("avito.testing"):
        if not (REFERENCE_DIR / "testing.md").exists():
            gaps.append(ReferenceGap(f"avito.testing.{name}", "testing.md", "страница отсутствует"))

    for name in public_exports("avito"):
        expected = {
            "AvitoClient": "client.md",
            "AvitoSettings": "config.md",
            "AuthSettings": "config.md",
            "PaginatedList": "pagination.md",
        }.get(name, "exceptions.md")
        if not (REFERENCE_DIR / expected).exists():
            gaps.append(ReferenceGap(f"avito.{name}", expected, "страница отсутствует"))

    return gaps


def page_is_available(relative_page: str) -> bool:
    if (REFERENCE_DIR / relative_page).exists():
        return True
    if relative_page in GENERATED_PAGES:
        return (ROOT / "docs" / "site" / "assets" / "_gen_reference.py").exists()
    if relative_page.startswith("domains/"):
        return (ROOT / "docs" / "site" / "assets" / "_gen_reference.py").exists()
    return False


def write_report(gaps: list[ReferenceGap], output: Path) -> None:
    packages = domain_packages()
    report = {
        "domain_packages": packages,
        "domain_pages": [f"reference/domains/{package}.md" for package in packages],
        "top_level_exports": list(public_exports("avito")),
        "testing_exports": list(public_exports("avito.testing")),
        "gaps": [asdict(gap) for gap in gaps],
        "gap_count": len(gaps),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить покрытие public surface в reference.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    gaps = collect_gaps()
    write_report(gaps, args.output)
    if args.strict and gaps:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
