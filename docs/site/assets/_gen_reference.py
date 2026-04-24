from __future__ import annotations

import importlib
import inspect
from enum import Enum
from pathlib import Path

import mkdocs_gen_files

from scripts.parse_inventory import InventoryRow, parse_inventory
from scripts.public_sdk_surface import public_method_name

EXCLUDED_PACKAGES = {"auth", "core", "testing"}


def public_domain_packages(rows: list[InventoryRow]) -> list[str]:
    return sorted(
        {
            row.sdk_package
            for row in rows
            if row.sdk_package and row.sdk_package not in EXCLUDED_PACKAGES
        }
    )


def package_title(package: str, rows: list[InventoryRow]) -> str:
    documents = sorted({row.document for row in rows if row.sdk_package == package})
    return ", ".join(documents) if documents else package


def public_enums(package: str) -> list[type[Enum]]:
    module = importlib.import_module(f"avito.{package}")
    names = getattr(module, "__all__", ())
    enums: list[type[Enum]] = []
    for name in names:
        value = getattr(module, name, None)
        if inspect.isclass(value) and issubclass(value, Enum):
            enums.append(value)
    return enums


def write_domain_pages(rows: list[InventoryRow]) -> list[str]:
    pages: list[str] = []
    for package in public_domain_packages(rows):
        page = f"reference/domains/{package}.md"
        pages.append(page)
        enums = public_enums(package)
        with mkdocs_gen_files.open(page, "w") as file:
            file.write(f"# {package}\n\n")
            file.write(f"Источник API: {package_title(package, rows)}.\n\n")
            if enums:
                file.write("## Enum\n\n")
                for enum_class in enums:
                    file.write(f"- [`{enum_class.__name__}`](../enums.md#{enum_class.__name__})\n")
                file.write("\n")
            file.write(f"::: avito.{package}\n")
        mkdocs_gen_files.set_edit_path(page, Path(f"avito/{package}/__init__.py"))
    return pages


def write_operations(rows: list[InventoryRow]) -> None:
    with mkdocs_gen_files.open("reference/operations.md", "w") as file:
        file.write("# Операции API\n\n")
        file.write(
            "Таблица строится из `docs/avito/inventory.md` и связывает HTTP-операции "
            "с публичными методами SDK.\n\n"
        )
        file.write(
            "| Описание | HTTP | SDK | Тип ответа | Deprecated |\n"
            "|---|---|---|---|---|\n"
        )
        for row in rows:
            method_name = public_method_name(row)
            sdk = f"`avito.{row.sdk_package}.{row.domain_object}.{method_name}()`"
            http = f"`{row.method} {row.path}`"
            deprecated = "нет"
            if row.deprecated:
                deprecated = "да"
                if row.replacement:
                    deprecated += f"; замена `{row.replacement}`"
            file.write(
                f"| {row.description} | {http}<br>`{row.document}` | "
                f"{sdk} | `{row.response_type}` | {deprecated} |\n"
            )


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
    rows = parse_inventory()
    packages = public_domain_packages(rows)
    domain_pages = write_domain_pages(rows)
    write_operations(rows)
    write_enums(packages)
    write_summary(domain_pages)


main()
