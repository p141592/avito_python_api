"""Validate local Swagger/OpenAPI corpus and report SDK binding coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from avito.core.swagger_discovery import discover_swagger_bindings
from avito.core.swagger_factory_map import build_factory_domain_mapping_report
from avito.core.swagger_linter import lint_swagger_bindings
from avito.core.swagger_registry import (
    DEFAULT_SWAGGER_API_DIR,
    SwaggerRegistryError,
    load_swagger_registry,
)
from avito.core.swagger_report import build_swagger_binding_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверить локальные Swagger/OpenAPI specs для SDK bindings.",
    )
    parser.add_argument(
        "--api-dir",
        type=Path,
        default=DEFAULT_SWAGGER_API_DIR,
        help="Каталог с Swagger/OpenAPI JSON specs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_report",
        help="Вывести baseline coverage report в JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Требовать ровно один SDK binding для каждой Swagger operation.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Записать JSON report в файл вместо stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        registry = load_swagger_registry(args.api_dir)
    except SwaggerRegistryError as exc:
        print(exc, file=sys.stderr)
        return 2

    discovery = discover_swagger_bindings(registry=registry)
    lint_errors = lint_swagger_bindings(registry, discovery, strict=args.strict)
    factory_mapping = build_factory_domain_mapping_report()
    report = build_swagger_binding_report(
        registry,
        discovery,
        errors=lint_errors,
        factory_mapping=factory_mapping,
    )
    report_data = report.to_dict()

    if args.json_report:
        # `json.dumps()` принимает JSON-compatible структуру на границе CLI.
        output = json.dumps(report_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            print(output, end="")
        else:
            args.output.write_text(output, encoding="utf-8")
        return 1 if registry.errors or lint_errors else 0

    summary = report_data["summary"]
    if not isinstance(summary, dict):
        raise TypeError("Swagger report summary must be a JSON object.")
    print(
        "Swagger specs: "
        f"{len(registry.specs)}, operations: {len(registry.operations)}, "
        f"deprecated operations: {len(registry.deprecated_operations)}, "
        f"bound: {summary['bound']}, unbound: {summary['unbound']}, "
        f"duplicate: {summary['duplicate']}, ambiguous: {summary['ambiguous']}, "
        f"validation errors: {len(registry.errors)}"
    )
    for error in registry.errors:
        print(f"[{error.code}] {error.message}", file=sys.stderr)
    for error in lint_errors:
        print(f"[{error.code}] {error.message}", file=sys.stderr)
    return 1 if registry.errors or lint_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
