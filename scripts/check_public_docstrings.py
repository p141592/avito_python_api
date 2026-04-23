from __future__ import annotations

import argparse
import importlib
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from parse_inventory import InventoryRow, parse_inventory

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docstring-contract-report.json"
EXCEPTION_METADATA_FIELDS = ("operation", "status", "request_id", "attempt", "method", "endpoint")


@dataclass(slots=True, frozen=True)
class DocstringGap:
    symbol: str
    aspect: str
    reason: str


def domain_method(row: InventoryRow) -> object | None:
    if row.domain_object == "AvitoClient.auth()":
        from avito import AvitoClient

        return getattr(AvitoClient, "auth", None)

    try:
        module = importlib.import_module(f"avito.{row.sdk_package}")
    except ModuleNotFoundError:
        return None
    domain_class = getattr(module, row.domain_object, None)
    if domain_class is None:
        return None
    return getattr(domain_class, row.sdk_public_method, None)


def symbol_name(row: InventoryRow) -> str:
    return f"avito.{row.sdk_package}.{row.domain_object}.{row.sdk_public_method}"


def collect_gaps(rows: list[InventoryRow]) -> list[DocstringGap]:
    gaps: list[DocstringGap] = []
    seen: set[str] = set()
    for row in rows:
        symbol = symbol_name(row)
        if symbol in seen:
            continue
        seen.add(symbol)

        method = domain_method(row)
        if method is None:
            gaps.append(DocstringGap(symbol, "exists", "публичный метод не найден"))
            continue

        doc = inspect.getdoc(method) or ""
        lowered = doc.lower()
        if not doc:
            gaps.append(DocstringGap(symbol, "docstring", "docstring отсутствует"))
            continue

        expected = {
            "return_model": ("возвращ", "return", row.response_type.lower()),
            "nullable_empty": ("none", "null", "пуст", "empty"),
            "overrides": ("timeout", "retries", "dry_run", "idempotency_key", "page_size"),
            "idempotency": ("идемпот", "idempot"),
            "raises": ("raises", "исключ", "ошиб", *EXCEPTION_METADATA_FIELDS),
        }
        if row.request_type != "NoRequest":
            expected["dry_run"] = ("dry_run", "транспорт", "transport")

        for aspect, markers in expected.items():
            if not any(marker.lower() in lowered for marker in markers):
                gaps.append(
                    DocstringGap(
                        symbol,
                        aspect,
                        "docstring не описывает обязательный contract-аспект",
                    )
                )
    return gaps


def write_report(rows: list[InventoryRow], gaps: list[DocstringGap], output: Path) -> None:
    report = {
        "checked_symbols": len({symbol_name(row) for row in rows}),
        "required_exception_metadata_fields": list(EXCEPTION_METADATA_FIELDS),
        "gaps": [asdict(gap) for gap in gaps],
        "gap_count": len(gaps),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить docstring-контракт публичных методов.")
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
