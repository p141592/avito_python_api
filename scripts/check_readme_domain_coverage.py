from __future__ import annotations

import inspect
from pathlib import Path
from typing import get_type_hints

from parse_inventory import parse_inventory

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
EXCLUDED_PACKAGES = {"auth", "core", "testing"}


def public_packages_from_inventory() -> set[str]:
    return {
        row.sdk_package
        for row in parse_inventory()
        if row.sdk_package and row.sdk_package not in EXCLUDED_PACKAGES
    }


def factory_methods_by_package() -> dict[str, set[str]]:
    from avito import AvitoClient

    factories: dict[str, set[str]] = {}
    for name, member in inspect.getmembers(AvitoClient, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        annotation = get_type_hints(member).get("return")
        module = getattr(annotation, "__module__", "")
        if not module.startswith("avito."):
            continue
        package = module.split(".")[1]
        factories.setdefault(package, set()).add(name)
    return factories


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    packages = public_packages_from_inventory()
    factories = factory_methods_by_package()

    missing: list[str] = []
    for package in sorted(packages):
        candidates = factories.get(package, set())
        if not candidates:
            missing.append(f"{package}: нет фабричных методов AvitoClient")
            continue
        if not any(f"avito.{factory}(" in readme for factory in candidates):
            missing.append(f"{package}: нет README-snippet с {', '.join(sorted(candidates))}")

    if missing:
        print("README не покрывает домены из inventory:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"README покрывает домены из inventory: {', '.join(sorted(packages))}")


if __name__ == "__main__":
    main()
