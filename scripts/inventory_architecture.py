"""Report current API-domain architecture inventory for v2 migration."""

from __future__ import annotations

import argparse
import ast
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from avito.core.swagger_discovery import DiscoveredSwaggerBinding, discover_swagger_bindings
from avito.core.swagger_registry import SwaggerOperation, load_swagger_registry

API_DOMAINS = (
    "accounts",
    "ads",
    "autoteka",
    "cpa",
    "jobs",
    "messenger",
    "orders",
    "promotion",
    "ratings",
    "realty",
    "tariffs",
)
LEGACY_FILENAMES = (
    "client.py",
    "mappers.py",
    "enums.py",
    "_client.py",
    "_mappers.py",
    "_mapping.py",
    "_enums.py",
)
LEGACY_USAGE_PATTERNS = ("request_public_model", "mapper=")
PAGINATION_QUERY_NAMES = frozenset(
    {
        "cursor",
        "limit",
        "offset",
        "page",
        "page_size",
        "per_page",
        "perPage",
    }
)


@dataclass(frozen=True, slots=True)
class SourceHit:
    """Source code location for inventory findings."""

    path: str
    line: int
    value: str

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible source hit data."""

        return {"path": self.path, "line": self.line, "value": self.value}


@dataclass(frozen=True, slots=True)
class LegacyFile:
    """Legacy file found inside an API domain package."""

    domain: str
    kind: str
    path: str

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible legacy file data."""

        return {"domain": self.domain, "kind": self.kind, "path": self.path}


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Снять baseline inventory для перехода API-доменов на v2 architecture.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_report",
        help="Вывести полный inventory report в JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Записать report в файл вместо stdout.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Корень репозитория.",
    )
    return parser.parse_args()


def main() -> int:
    """Run inventory report CLI."""

    args = parse_args()
    root = args.root
    report = build_inventory_report(root)
    if args.json_report:
        output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    else:
        output = render_text_report(report)
    if args.output is None:
        print(output, end="")
    else:
        args.output.write_text(output, encoding="utf-8")
    return 0


def build_inventory_report(root: Path = Path(".")) -> dict[str, object]:
    """Build JSON-compatible API-domain architecture inventory report."""

    registry = load_swagger_registry(root / "docs/avito/api")
    discovery = discover_swagger_bindings(registry=registry)
    operation_domains = _operation_domains(discovery.bindings)
    operations_by_domain = _operations_by_domain(registry.operations, operation_domains)
    public_methods = _public_domain_methods(root)
    bindings_by_domain = _bindings_by_domain(discovery.bindings)
    edge_cases = {
        domain: _edge_cases_for_operations(operations)
        for domain, operations in operations_by_domain.items()
    }
    legacy_files = _legacy_files(root)
    legacy_imports = _legacy_imports(root)
    legacy_usage = _legacy_usage(root)

    domain_entries: dict[str, object] = {}
    for domain in API_DOMAINS:
        domain_entries[domain] = {
            "legacy_files": [
                entry.to_dict() for entry in legacy_files if entry.domain == domain
            ],
            "public_methods": public_methods.get(domain, []),
            "public_method_count": len(public_methods.get(domain, [])),
            "swagger_binding_count": len(bindings_by_domain.get(domain, ())),
            "swagger_operation_count": len(operations_by_domain.get(domain, ())),
            "edge_cases": edge_cases.get(domain, []),
        }

    return {
        "api_domains": list(API_DOMAINS),
        "summary": {
            "api_domain_count": len(API_DOMAINS),
            "legacy_file_count": len(legacy_files),
            "legacy_import_count": len(legacy_imports),
            "legacy_usage_count": len(legacy_usage),
            "public_method_count": sum(len(methods) for methods in public_methods.values()),
            "swagger_total_operation_count": len(registry.operations),
            "swagger_binding_count": sum(
                len(bindings) for bindings in bindings_by_domain.values()
            ),
            "swagger_operation_count": sum(
                len(operations) for operations in operations_by_domain.values()
            ),
        },
        "domains": domain_entries,
        "legacy_files": [entry.to_dict() for entry in legacy_files],
        "legacy_imports": [entry.to_dict() for entry in legacy_imports],
        "legacy_usage": [entry.to_dict() for entry in legacy_usage],
    }


def render_text_report(report: Mapping[str, object]) -> str:
    """Render compact human-readable report."""

    lines: list[str] = []
    summary = _expect_mapping(report["summary"])
    lines.append("Architecture inventory baseline")
    lines.append(
        "Summary: "
        f"domains={summary['api_domain_count']}, "
        f"legacy_files={summary['legacy_file_count']}, "
        f"legacy_imports={summary['legacy_import_count']}, "
        f"legacy_usage={summary['legacy_usage_count']}, "
        f"public_methods={summary['public_method_count']}, "
        f"swagger_bindings={summary['swagger_binding_count']}, "
        f"api_domain_swagger_operations={summary['swagger_operation_count']}, "
        f"swagger_operations_total={summary['swagger_total_operation_count']}"
    )
    lines.append("")
    lines.append(
        "| Domain | Legacy files | Public methods | Swagger bindings | "
        "Swagger operations | Edge cases |"
    )
    lines.append("|---|---:|---:|---:|---:|---|")
    domains = _expect_mapping(report["domains"])
    for domain in API_DOMAINS:
        entry = _expect_mapping(domains[domain])
        edge_cases = _expect_sequence(entry["edge_cases"])
        lines.append(
            f"| {domain} | {len(_expect_sequence(entry['legacy_files']))} | "
            f"{entry['public_method_count']} | {entry['swagger_binding_count']} | "
            f"{entry['swagger_operation_count']} | {', '.join(map(str, edge_cases)) or '-'} |"
        )
    return "\n".join(lines) + "\n"


def _legacy_files(root: Path) -> tuple[LegacyFile, ...]:
    entries: list[LegacyFile] = []
    for domain in API_DOMAINS:
        for filename in LEGACY_FILENAMES:
            path = root / "avito" / domain / filename
            if path.exists():
                entries.append(
                    LegacyFile(
                        domain=domain,
                        kind=filename.removesuffix(".py"),
                        path=_relative_path(path, root),
                    )
                )
    return tuple(entries)


def _legacy_imports(root: Path) -> tuple[SourceHit, ...]:
    hits: list[SourceHit] = []
    for path in _iter_python_files(root, ("avito", "tests", "docs")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                if _is_legacy_module(node.module):
                    hits.append(
                        SourceHit(
                            path=_relative_path(path, root),
                            line=node.lineno,
                            value=f"from {node.module} import ...",
                        )
                    )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if _is_legacy_module(alias.name):
                        hits.append(
                            SourceHit(
                                path=_relative_path(path, root),
                                line=node.lineno,
                                value=f"import {alias.name}",
                            )
                        )
    return tuple(sorted(hits, key=lambda hit: (hit.path, hit.line, hit.value)))


def _legacy_usage(root: Path) -> tuple[SourceHit, ...]:
    hits: list[SourceHit] = []
    for path in _iter_text_files(root, ("avito", "tests", "docs")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern in LEGACY_USAGE_PATTERNS:
                if pattern in line:
                    hits.append(
                        SourceHit(
                            path=_relative_path(path, root),
                            line=line_number,
                            value=pattern,
                        )
                    )
    return tuple(sorted(hits, key=lambda hit: (hit.path, hit.line, hit.value)))


def _public_domain_methods(root: Path) -> dict[str, list[str]]:
    methods_by_domain: dict[str, list[str]] = {}
    for domain in API_DOMAINS:
        path = root / "avito" / domain / "domain.py"
        if not path.exists():
            methods_by_domain[domain] = []
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        methods: list[str] = []
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or node.name.startswith("_"):
                continue
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    methods.append(f"{node.name}.{item.name}")
        methods_by_domain[domain] = sorted(methods)
    return methods_by_domain


def _operation_domains(
    bindings: Sequence[DiscoveredSwaggerBinding],
) -> dict[str, str]:
    domains: dict[str, str] = {}
    for binding in bindings:
        if binding.operation_key is None or binding.domain not in API_DOMAINS:
            continue
        domains[binding.operation_key] = binding.domain
    return domains


def _operations_by_domain(
    operations: Sequence[SwaggerOperation],
    operation_domains: Mapping[str, str],
) -> dict[str, tuple[SwaggerOperation, ...]]:
    grouped: dict[str, list[SwaggerOperation]] = {domain: [] for domain in API_DOMAINS}
    for operation in operations:
        domain = operation_domains.get(operation.key)
        if domain is not None:
            grouped[domain].append(operation)
    return {domain: tuple(items) for domain, items in grouped.items()}


def _bindings_by_domain(
    bindings: Sequence[DiscoveredSwaggerBinding],
) -> dict[str, tuple[DiscoveredSwaggerBinding, ...]]:
    grouped: dict[str, list[DiscoveredSwaggerBinding]] = {domain: [] for domain in API_DOMAINS}
    for binding in bindings:
        if binding.domain in API_DOMAINS:
            grouped[binding.domain].append(binding)
    return {domain: tuple(items) for domain, items in grouped.items()}


def _edge_cases_for_operations(operations: Sequence[SwaggerOperation]) -> list[str]:
    edge_cases: set[str] = set()
    for operation in operations:
        if operation.request_body is not None:
            content_types = operation.request_body.content_types
            if any("multipart/" in content_type for content_type in content_types):
                edge_cases.add("multipart")
        if _has_binary_success_response(operation):
            edge_cases.add("binary")
        if _has_empty_success_response(operation):
            edge_cases.add("empty_response")
        if any(parameter.name in PAGINATION_QUERY_NAMES for parameter in operation.query_parameters):
            edge_cases.add("pagination")
        if any("idempot" in parameter.name.lower() for parameter in operation.header_parameters):
            edge_cases.add("idempotency")
    return sorted(edge_cases)


def _has_binary_success_response(operation: SwaggerOperation) -> bool:
    for response in operation.success_responses:
        for content_type in response.content_types:
            if "json" not in content_type:
                return True
    return False


def _has_empty_success_response(operation: SwaggerOperation) -> bool:
    return any(
        response.status_code == "204" or not response.content_types
        for response in operation.success_responses
    )


def _is_legacy_module(module: str) -> bool:
    parts = module.split(".")
    if len(parts) != 3:
        return False
    package, domain, name = parts
    return package == "avito" and domain in API_DOMAINS and f"{name}.py" in LEGACY_FILENAMES


def _iter_python_files(root: Path, directories: Iterable[str]) -> Iterable[Path]:
    for path in _iter_text_files(root, directories):
        if path.suffix == ".py":
            yield path


def _iter_text_files(root: Path, directories: Iterable[str]) -> Iterable[Path]:
    for directory in directories:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in {".py", ".md", ".txt"}:
                yield path


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _expect_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("Expected mapping in inventory report.")
    return value


def _expect_sequence(value: object) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise TypeError("Expected sequence in inventory report.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
