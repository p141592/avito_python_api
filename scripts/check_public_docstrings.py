from __future__ import annotations

import argparse
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from parse_inventory import InventoryRow, parse_inventory
from public_sdk_surface import resolve_public_method

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docstring-contract-report.json"
EXCEPTION_METADATA_FIELDS = ("operation", "status", "request_id", "attempt", "method", "endpoint")
OVERRIDE_PARAMS = ("timeout", "retries", "dry_run", "idempotency_key", "page_size")


@dataclass(slots=True, frozen=True)
class DocstringGap:
    symbol: str
    aspect: str
    reason: str


def inventory_symbol_name(row: InventoryRow) -> str:
    return f"avito.{row.sdk_package}.{row.domain_object}.{row.sdk_public_method}"


def public_parameters(method: object) -> set[str]:
    try:
        return set(inspect.signature(method).parameters)
    except (TypeError, ValueError):
        return set()


def has_return_annotation(method: object) -> bool:
    try:
        return inspect.signature(method).return_annotation is not inspect.Signature.empty
    except (TypeError, ValueError):
        return False


def needs_empty_behavior_note(method_name: str, doc: str, method: object) -> bool:
    if any(marker in doc for marker in ("none", "null", "пуст", "empty")):
        return False
    if method_name.startswith("list") or method_name in {"get_items", "get_by_ids"}:
        return True
    try:
        annotation = inspect.signature(method).return_annotation
    except (TypeError, ValueError):
        return False
    return "PaginatedList" in str(annotation) or "list[" in str(annotation)


def doc_mentions_all(doc: str, markers: set[str]) -> bool:
    return all(marker.lower() in doc for marker in markers)


def collect_gaps(rows: list[InventoryRow]) -> list[DocstringGap]:
    gaps: list[DocstringGap] = []
    seen: set[str] = set()
    for row in rows:
        resolved = resolve_public_method(row)
        symbol = resolved.symbol if resolved is not None else inventory_symbol_name(row)
        if symbol in seen:
            continue
        seen.add(symbol)

        if resolved is None:
            gaps.append(DocstringGap(symbol, "exists", "публичный метод не найден"))
            continue

        doc = inspect.getdoc(resolved.method) or ""
        lowered = doc.lower()
        if not doc:
            gaps.append(DocstringGap(symbol, "docstring", "docstring отсутствует"))
            continue

        params = public_parameters(resolved.method)
        override_params = params.intersection(OVERRIDE_PARAMS)

        if not has_return_annotation(resolved.method) and not any(
            marker in lowered for marker in ("возвращ", "return", row.response_type.lower())
        ):
            gaps.append(gap(symbol, "return_model"))

        if needs_empty_behavior_note(resolved.method_name, lowered, resolved.method):
            gaps.append(gap(symbol, "nullable_empty"))

        if override_params and not doc_mentions_all(lowered, override_params):
            gaps.append(gap(symbol, "overrides"))

        if "idempotency_key" in params and not any(
            marker in lowered for marker in ("идемпот", "idempot", "idempotency_key")
        ):
            gaps.append(gap(symbol, "idempotency"))

        if not any(
            marker in lowered
            for marker in ("raises", "исключ", "ошиб", *EXCEPTION_METADATA_FIELDS)
        ):
            gaps.append(gap(symbol, "raises"))

        if "dry_run" in params and not any(
            marker in lowered for marker in ("dry_run", "транспорт", "transport")
        ):
            gaps.append(gap(symbol, "dry_run"))
    return gaps


def gap(symbol: str, aspect: str) -> DocstringGap:
    return DocstringGap(symbol, aspect, "docstring не описывает обязательный contract-аспект")


def write_report(rows: list[InventoryRow], gaps: list[DocstringGap], output: Path) -> None:
    by_aspect: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    for item in gaps:
        by_aspect[item.aspect] = by_aspect.get(item.aspect, 0) + 1
        parts = item.symbol.split(".")
        domain = parts[1] if len(parts) > 1 else "unknown"
        by_domain[domain] = by_domain.get(domain, 0) + 1

    report = {
        "checked_symbols": len(
            {
                resolved.symbol if (resolved := resolve_public_method(row)) is not None
                else inventory_symbol_name(row)
                for row in rows
            }
        ),
        "required_exception_metadata_fields": list(EXCEPTION_METADATA_FIELDS),
        "by_aspect": dict(sorted(by_aspect.items())),
        "by_domain": dict(sorted(by_domain.items())),
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
