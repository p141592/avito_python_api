from __future__ import annotations

import argparse
import importlib
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from parse_inventory import InventoryRow, parse_inventory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "inventory-coverage-report.json"


@dataclass(slots=True, frozen=True)
class InventoryGap:
    document: str
    method: str
    path: str
    sdk_package: str
    domain_object: str
    sdk_public_method: str
    reason: str


def parse_version(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    if len(parts) != 3:
        raise ValueError(value)
    return int(parts[0]), int(parts[1]), int(parts[2])


def removal_is_two_minor_later(deprecated_since: str, removal_version: str) -> bool:
    since_major, since_minor, _ = parse_version(deprecated_since)
    removal_major, removal_minor, _ = parse_version(removal_version)
    return removal_major == since_major and removal_minor >= since_minor + 2


def domain_has_public_method(row: InventoryRow) -> bool:
    if row.domain_object == "AvitoClient.auth()":
        from avito import AvitoClient

        return hasattr(AvitoClient, "auth")

    try:
        module = importlib.import_module(f"avito.{row.sdk_package}")
    except ModuleNotFoundError:
        return False

    domain_class = getattr(module, row.domain_object, None)
    if domain_class is None:
        return False
    return inspect.isclass(domain_class) and hasattr(domain_class, row.sdk_public_method)


def collect_gaps(rows: list[InventoryRow]) -> list[InventoryGap]:
    gaps: list[InventoryGap] = []
    for row in rows:
        if row.deprecated:
            missing = [
                name
                for name, value in (
                    ("deprecated_since", row.deprecated_since),
                    ("replacement", row.replacement),
                    ("removal_version", row.removal_version),
                )
                if value is None
            ]
            if missing:
                gaps.append(gap(row, f"deprecated без обязательных полей: {', '.join(missing)}"))
            elif not removal_is_two_minor_later(row.deprecated_since, row.removal_version):
                gaps.append(gap(row, "removal_version раньше чем через два minor-релиза"))

        description_marks_deprecated = "deprecated" in row.description.lower()
        if description_marks_deprecated and not row.deprecated:
            gaps.append(gap(row, "описание содержит deprecated, но deprecated=нет"))
        if row.deprecated and not domain_has_public_method(row):
            gaps.append(gap(row, "не найден публичный SDK-символ"))

    return gaps


def gap(row: InventoryRow, reason: str) -> InventoryGap:
    return InventoryGap(
        document=row.document,
        method=row.method,
        path=row.path,
        sdk_package=row.sdk_package,
        domain_object=row.domain_object,
        sdk_public_method=row.sdk_public_method,
        reason=reason,
    )


def write_report(rows: list[InventoryRow], gaps: list[InventoryGap], output: Path) -> None:
    report = {
        "total_operations": len(rows),
        "deprecated_operations": sum(row.deprecated for row in rows),
        "gaps": [asdict(item) for item in gaps],
        "gap_count": len(gaps),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить inventory coverage report-only.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    rows = parse_inventory()
    gaps = collect_gaps(rows)
    write_report(rows, gaps, args.output)
    if args.strict and gaps:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
