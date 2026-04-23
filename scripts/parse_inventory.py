from __future__ import annotations

import argparse
import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY_PATH = ROOT / "docs" / "avito" / "inventory.md"


@dataclass(slots=True, frozen=True)
class DocumentRow:
    document: str
    section: str
    sdk_package: str
    default_domain_object: str
    operations_count: int


@dataclass(slots=True, frozen=True)
class InventoryRow:
    section: str
    document: str
    method: str
    path: str
    description: str
    deprecated: bool
    deprecated_since: str | None
    replacement: str | None
    removal_version: str | None
    sdk_package: str
    domain_object: str
    sdk_public_method: str
    request_type: str
    response_type: str
    test_type: str
    notes: str | None


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()


def parse_optional(value: str) -> str | None:
    normalized = normalize_text(value).strip("`")
    return normalized or None


def parse_bool(value: str) -> bool:
    normalized = normalize_text(value).lower()
    if normalized == "да":
        return True
    if normalized == "нет":
        return False
    raise ValueError(f"Недопустимое значение deprecated: {value!r}")


def parse_markdown_table(line: str) -> list[str]:
    return [normalize_text(cell).strip("`") for cell in line.strip().strip("|").split("|")]


def read_table(
    lines: list[str], marker: str | None = None, heading: str | None = None
) -> list[str]:
    start = None
    if marker is not None:
        for index, line in enumerate(lines):
            if marker in line:
                start = index + 1
                break
    elif heading is not None:
        for index, line in enumerate(lines):
            if line.strip() == heading:
                start = index + 1
                break
    if start is None:
        return []

    table: list[str] = []
    for line in lines[start:]:
        if line.startswith("|"):
            table.append(line)
            continue
        if table:
            break
    return table


def parse_documents(path: Path = DEFAULT_INVENTORY_PATH) -> list[DocumentRow]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table = read_table(lines, heading="## Соответствие Документов И SDK")
    rows: list[DocumentRow] = []
    for line in table[2:]:
        cells = parse_markdown_table(line)
        if len(cells) != 5:
            raise ValueError(f"Некорректная строка таблицы документов: {line}")
        document, section, sdk_package, default_domain_object, operations_count = cells
        rows.append(
            DocumentRow(
                document=document,
                section=section,
                sdk_package=sdk_package,
                default_domain_object=default_domain_object,
                operations_count=int(operations_count.rstrip(":")),
            )
        )
    return rows


def parse_inventory(path: Path = DEFAULT_INVENTORY_PATH) -> list[InventoryRow]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table = read_table(lines, marker="<!-- operations-table:start -->")
    if len(table) < 2:
        raise ValueError("Таблица операций не найдена.")

    headers = parse_markdown_table(table[0])
    expected_headers = [
        "раздел",
        "документ",
        "метод",
        "путь",
        "описание",
        "deprecated",
        "deprecated_since",
        "replacement",
        "removal_version",
        "пакет_sdk",
        "доменный_объект",
        "публичный_метод_sdk",
        "тип_запроса",
        "тип_ответа",
        "тип_теста",
        "примечания",
    ]
    if headers != expected_headers:
        raise ValueError(f"Неожиданные колонки inventory: {headers!r}")

    rows: list[InventoryRow] = []
    for line in table[2:]:
        if line.startswith("<!-- operations-table:end -->"):
            break
        cells = parse_markdown_table(line)
        if len(cells) != len(expected_headers):
            raise ValueError(f"Некорректная строка operations table: {line}")
        deprecated = parse_bool(cells[5])
        rows.append(
            InventoryRow(
                section=cells[0],
                document=cells[1],
                method=cells[2].upper(),
                path=cells[3],
                description=cells[4],
                deprecated=deprecated,
                deprecated_since=parse_optional(cells[6]),
                replacement=parse_optional(cells[7]),
                removal_version=parse_optional(cells[8]),
                sdk_package=cells[9],
                domain_object=cells[10],
                sdk_public_method=cells[11],
                request_type=cells[12],
                response_type=cells[13],
                test_type=cells[14],
                notes=parse_optional(cells[15]),
            )
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Разобрать docs/avito/inventory.md.")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--documents", action="store_true")
    args = parser.parse_args()

    rows = parse_documents(args.inventory) if args.documents else parse_inventory(args.inventory)
    print(json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
