from __future__ import annotations

import importlib
import inspect
from enum import Enum
from pathlib import Path

import mkdocs_gen_files

from avito.core.domain import DomainObject

EXCLUDED_PACKAGES = {"auth", "core", "testing"}
PACKAGE_ROOT = Path("avito")


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


def write_operations(packages: list[str]) -> None:
    with mkdocs_gen_files.open("reference/operations.md", "w") as file:
        file.write("# Методы API\n\n")
        file.write(
            "Страница перечисляет публичные доменные методы SDK. Подробные сигнатуры, "
            "модели и docstring-контракты находятся на страницах доменных пакетов.\n\n"
        )
        file.write("| Пакет | Доменный объект | Метод |\n")
        file.write("|---|---|---|\n")
        for package in packages:
            for domain_class in public_domain_classes(package):
                for method_name in public_domain_methods(domain_class):
                    file.write(
                        f"| `{package}` | `{domain_class.__name__}` | "
                        f"`{domain_class.__name__}.{method_name}()` |\n"
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
    packages = public_domain_packages()
    domain_pages = write_domain_pages(packages)
    write_operations(packages)
    write_enums(packages)
    write_summary(domain_pages)


main()
