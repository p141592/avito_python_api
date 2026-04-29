from __future__ import annotations

import importlib
import inspect
from enum import Enum
from pathlib import Path
from urllib.parse import quote

import mkdocs_gen_files

from avito.core.domain import DomainObject
from avito.core.swagger_discovery import discover_swagger_bindings
from avito.core.swagger_linter import lint_swagger_bindings
from avito.core.swagger_registry import load_swagger_registry
from avito.core.swagger_report import build_swagger_binding_report

EXCLUDED_PACKAGES = {"auth", "core", "testing"}
PACKAGE_ROOT = Path("avito")
GITHUB_API_URL = "https://github.com/p141592/avito_python_api/blob/main/docs/avito/api"


def public_domain_packages() -> list[str]:
    return sorted(
        path.parent.name
        for path in PACKAGE_ROOT.glob("*/domain.py")
        if path.parent.name not in EXCLUDED_PACKAGES
    )


def package_title(package: str) -> str:
    return package


def public_enums(package: str) -> list[type[Enum]]:
    module = importlib.import_module(f"avito.{package}")
    names = getattr(module, "__all__", ())
    enums: list[type[Enum]] = []
    for name in names:
        value = getattr(module, name, None)
        if inspect.isclass(value) and issubclass(value, Enum):
            enums.append(value)
    return enums


def public_domain_classes(package: str) -> list[type[DomainObject]]:
    module = importlib.import_module(f"avito.{package}")
    names = getattr(module, "__all__", ())
    classes: list[type[DomainObject]] = []
    for name in names:
        value = getattr(module, name, None)
        if (
            inspect.isclass(value)
            and issubclass(value, DomainObject)
            and value is not DomainObject
            and value.__module__.startswith(f"avito.{package}.")
        ):
            classes.append(value)
    return classes


def public_domain_methods(domain_class: type[DomainObject]) -> list[str]:
    methods: list[str] = []
    for name, value in inspect.getmembers(domain_class, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        if value.__qualname__.startswith(f"{domain_class.__name__}."):
            methods.append(name)
    return methods


def write_domain_pages(packages: list[str]) -> list[str]:
    pages: list[str] = []
    for package in packages:
        page = f"reference/domains/{package}.md"
        pages.append(page)
        enums = public_enums(package)
        with mkdocs_gen_files.open(page, "w") as file:
            file.write(f"# {package}\n\n")
            file.write(f"Публичный доменный пакет SDK: `{package_title(package)}`.\n\n")
            if enums:
                file.write("## Enum\n\n")
                for enum_class in enums:
                    file.write(f"- [`{enum_class.__name__}`](../enums.md#{enum_class.__name__})\n")
                file.write("\n")
            file.write(f"::: avito.{package}\n")
        mkdocs_gen_files.set_edit_path(page, Path(f"avito/{package}/__init__.py"))
    return pages


def write_operations(report: dict[str, object]) -> None:
    operations = report["operations"]
    if not isinstance(operations, list):
        raise TypeError("Swagger binding report operations must be a list.")

    with mkdocs_gen_files.open("reference/operations.md", "w") as file:
        file.write("# Методы API\n\n")
        file.write(
            "Страница строится из Swagger operation bindings и связывает каждую "
            "upstream-операцию с публичным SDK-методом. Подробные сигнатуры, модели "
            "и docstring-контракты находятся на страницах доменных пакетов.\n\n"
        )
        file.write("| Spec | HTTP | Path | SDK method | Deprecated |\n")
        file.write("|---|---|---|---|---|\n")
        for operation in operations:
            if not isinstance(operation, dict):
                raise TypeError("Swagger binding report operation entry must be an object.")
            binding = operation["binding"]
            sdk_method = ""
            if isinstance(binding, dict):
                sdk_method = str(binding["sdk_method"])
            file.write(
                f"| `{operation['spec']}` | `{operation['method']}` | "
                f"`{operation['path']}` | `{sdk_method}` | "
                f"{'yes' if operation['deprecated'] else 'no'} |\n"
            )


def write_coverage(report: dict[str, object]) -> None:
    summary = report["summary"]
    operations = report["operations"]
    if not isinstance(summary, dict):
        raise TypeError("Swagger binding report summary must be an object.")
    if not isinstance(operations, list):
        raise TypeError("Swagger binding report operations must be a list.")

    specs: dict[str, dict[str, int]] = {}
    for operation in operations:
        if not isinstance(operation, dict):
            raise TypeError("Swagger binding report operation entry must be an object.")
        spec = str(operation["spec"])
        spec_summary = specs.setdefault(spec, {"total": 0, "bound": 0, "deprecated": 0})
        spec_summary["total"] += 1
        if operation["status"] == "bound":
            spec_summary["bound"] += 1
        if operation["deprecated"]:
            spec_summary["deprecated"] += 1

    with mkdocs_gen_files.open("reference/coverage.md", "w") as file:
        file.write("# Покрытие API\n\n")
        file.write(
            "Swagger/OpenAPI-спецификации в `docs/avito/api/` остаются источником "
            "истины, а карта покрытия SDK строится из Swagger operation bindings "
            "на публичных SDK-методах.\n\n"
        )
        file.write(
            f"SDK покрывает {summary['bound']} из {summary['operations_total']} "
            f"операций Avito API. Deprecated operations: "
            f"{summary['deprecated_operations']}.\n\n"
        )
        file.write("!!! info \"Источник данных\"\n")
        file.write(
            "    Страница генерируется из JSON-compatible Swagger binding report, "
            "который строится из локальных specs и binding discovery.\n\n"
        )
        file.write("| Документ API | Операции | Bound | Deprecated | Swagger/OpenAPI |\n")
        file.write("|---|---:|---:|---:|---|\n")
        for spec, spec_summary in sorted(specs.items()):
            quoted_spec = quote(spec)
            file.write(
                f"| `{spec}` | {spec_summary['total']} | {spec_summary['bound']} | "
                f"{spec_summary['deprecated']} | "
                f"[{spec}]({GITHUB_API_URL}/{quoted_spec}) |\n"
            )
        file.write("\nПубличная карта операций: [Методы API](operations.md).\n")


def write_enums(packages: list[str]) -> None:
    with mkdocs_gen_files.open("reference/enums.md", "w") as file:
        file.write("# Enum\n\n")
        file.write("Публичные перечисления из доменных пакетов SDK.\n\n")
        for package in packages:
            enums = public_enums(package)
            if not enums:
                continue
            file.write(f"## {package}\n\n")
            for enum_class in enums:
                file.write(f"### {enum_class.__name__} {{ #{enum_class.__name__} }}\n\n")
                file.write(f"::: avito.{package}.{enum_class.__name__}\n\n")


def write_summary(domain_pages: list[str]) -> None:
    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as file:
        file.write("* [Reference](index.md)\n")
        file.write("* [Покрытие API](coverage.md)\n")
        file.write("* [AvitoClient](client.md)\n")
        file.write("* [Конфигурация](config.md)\n")
        file.write("* [Операции API](operations.md)\n")
        file.write("* Домены\n")
        for page in domain_pages:
            name = Path(page).stem
            file.write(f"    * [{name}]({page.removeprefix('reference/')})\n")
        file.write("* [Enum](enums.md)\n")
        file.write("* [Модели](models.md)\n")
        file.write("* [Исключения](exceptions.md)\n")
        file.write("* [Пагинация](pagination.md)\n")
        file.write("* [Тестирование](testing.md)\n")


def ensure_debug_info_exists() -> None:
    from avito import AvitoClient

    debug_info = getattr(AvitoClient, "debug_info", None)
    if debug_info is None or not callable(debug_info):
        raise RuntimeError("AvitoClient.debug_info отсутствует в публичном reference-контракте.")


def main() -> None:
    ensure_debug_info_exists()
    registry = load_swagger_registry()
    discovery = discover_swagger_bindings(registry=registry)
    lint_errors = lint_swagger_bindings(registry, discovery, strict=True)
    if registry.errors or lint_errors:
        raise RuntimeError("Swagger binding report contains validation errors.")
    report = build_swagger_binding_report(registry, discovery).to_dict()

    packages = public_domain_packages()
    domain_pages = write_domain_pages(packages)
    write_coverage(report)
    write_operations(report)
    write_enums(packages)
    write_summary(domain_pages)


main()
