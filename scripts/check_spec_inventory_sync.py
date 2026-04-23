from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from parse_inventory import normalize_text, parse_documents, parse_inventory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "spec-inventory-report.json"
SPEC_DIR = ROOT / "docs" / "avito" / "api"
HTTP_METHODS = {"get", "post", "put", "delete", "patch"}


@dataclass(slots=True, frozen=True)
class OperationKey:
    section: str
    document: str
    method: str
    path: str


def normalize_path(value: str) -> str:
    return (
        normalize_text(value)
        .replace("\u200b", "")
        .replace("\u200e", "")
        .replace("\u200f", "")
        .replace("\ufeff", "")
    )


def collect_spec_operations() -> Counter[OperationKey]:
    documents = {normalize_text(row.document): row.section for row in parse_documents()}
    operations: Counter[OperationKey] = Counter()
    for path in sorted(SPEC_DIR.glob("*.json")):
        document = normalize_text(path.name)
        section = documents.get(document)
        if section is None:
            section = "<unknown>"
        payload = json.loads(path.read_text(encoding="utf-8"))
        paths = payload.get("paths", {})
        if not isinstance(paths, dict):
            continue
        for raw_path, path_item in paths.items():
            if not isinstance(raw_path, str) or not isinstance(path_item, dict):
                continue
            for method in path_item:
                if method.lower() not in HTTP_METHODS:
                    continue
                operations[
                    OperationKey(
                        section=section,
                        document=document,
                        method=method.upper(),
                        path=normalize_path(raw_path),
                    )
                ] += 1
    return operations


def collect_inventory_operations() -> Counter[OperationKey]:
    operations: Counter[OperationKey] = Counter()
    for row in parse_inventory():
        operations[
            OperationKey(
                section=row.section,
                document=normalize_text(row.document),
                method=row.method,
                path=normalize_path(row.path),
            )
        ] += 1
    return operations


def counter_missing(
    left: Counter[OperationKey], right: Counter[OperationKey]
) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for key, count in sorted(
        (left - right).items(),
        key=lambda item: (
            item[0].section,
            item[0].document,
            item[0].method,
            item[0].path,
        ),
    ):
        payload = asdict(key)
        payload["count"] = str(count)
        missing.append(payload)
    return missing


def write_report(
    spec_operations: Counter[OperationKey],
    inventory_operations: Counter[OperationKey],
    output: Path,
) -> tuple[int, int]:
    missing_in_inventory = counter_missing(spec_operations, inventory_operations)
    missing_in_spec = counter_missing(inventory_operations, spec_operations)
    report = {
        "spec_operation_count": spec_operations.total(),
        "inventory_operation_count": inventory_operations.total(),
        "missing_in_inventory": missing_in_inventory,
        "missing_in_spec": missing_in_spec,
        "gap_count": len(missing_in_inventory) + len(missing_in_spec),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(missing_in_inventory), len(missing_in_spec)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сверить Swagger/OpenAPI specs с inventory.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    spec_operations = collect_spec_operations()
    inventory_operations = collect_inventory_operations()
    missing_in_inventory, missing_in_spec = write_report(
        spec_operations, inventory_operations, args.output
    )
    if args.strict and (missing_in_inventory or missing_in_spec):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
