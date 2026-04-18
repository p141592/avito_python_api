from __future__ import annotations

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
INVENTORY = DOCS_DIR / "inventory.md"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
INVENTORY_HEADER_MAP = {
    "раздел": "section",
    "документ": "document",
    "метод": "method",
    "путь": "path",
    "описание": "summary",
    "deprecated": "deprecated",
    "пакет_sdk": "package_sdk",
    "доменный_объект": "domain_object",
    "публичный_метод_sdk": "public_method_sdk",
    "тип_запроса": "type_request",
    "тип_ответа": "type_response",
    "тип_теста": "type_test",
    "примечания": "notes",
}
DOC_TO_PACKAGE = {
    "Авторизация.json": "auth",
    "Информацияопользователе.json": "accounts",
    "ИерархияАккаунтов.json": "accounts",
    "Объявления.json": "ads",
    "Автозагрузка.json": "ads",
    "Мессенджер.json": "messenger",
    "Рассылкаскидокиспецпредложенийвмессенджере.json": "messenger",
    "Продвижение.json": "promotion",
    "TrxPromo.json": "promotion",
    "CPA-аукцион.json": "promotion",
    "Настройкаценыцелевогодействия.json": "promotion",
    "Автостратегия.json": "promotion",
    "Управлениезаказами.json": "orders",
    "Доставка.json": "orders",
    "Управлениеостатками.json": "orders",
    "АвитоРабота.json": "jobs",
    "CPAАвито.json": "cpa",
    "CallTracking[КТ].json": "cpa",
    "Автотека.json": "autoteka",
    "Краткосрочнаяаренда.json": "realty",
    "Аналитикапонедвижимости.json": "realty",
    "Рейтингииотзывы.json": "ratings",
    "Тарифы.json": "tariffs",
}


def _normalize(value: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKC", value) if unicodedata.category(ch) != "Cf"
    )


def _resolve_doc_path(document: str) -> Path:
    direct_path = DOCS_DIR / document
    if direct_path.exists():
        return direct_path

    normalized_target = _normalize(document)
    for candidate in DOCS_DIR.iterdir():
        if _normalize(candidate.name) == normalized_target:
            return candidate

    raise FileNotFoundError(f"Swagger document not found: {document}")


def _read_inventory_rows() -> list[dict[str, str]]:
    in_table = False
    rows: list[dict[str, str]] = []
    header: list[str] = []
    for line in INVENTORY.read_text(encoding="utf-8").splitlines():
        if line.strip() == "<!-- operations-table:start -->":
            in_table = True
            continue
        if line.strip() == "<!-- operations-table:end -->":
            break
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(cell and set(cell) == {"-"} for cell in cells):
            continue
        if cells[0] == "раздел":
            header = [INVENTORY_HEADER_MAP[cell] for cell in cells]
            continue
        rows.append(dict(zip(header, cells, strict=True)))
    return rows


def _swagger_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for document in sorted(DOC_TO_PACKAGE):
        data = json.loads(_resolve_doc_path(document).read_text(encoding="utf-8"))
        for path, path_item in data.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in HTTP_METHODS:
                    continue
                rows.append(
                    {
                        "document": document,
                        "method": method.upper(),
                        "path": _normalize(path),
                        "deprecated": "да" if operation.get("deprecated", False) else "нет",
                    }
                )
    return rows


def test_inventory_covers_all_swagger_operations() -> None:
    inventory_rows = _read_inventory_rows()
    inventory_index = {
        (row["document"], row["method"], _normalize(row["path"]), row["deprecated"]): row
        for row in inventory_rows
    }

    swagger_rows = _swagger_rows()

    assert len(inventory_rows) == len(swagger_rows)

    for swagger_row in swagger_rows:
        key = (
            swagger_row["document"],
            swagger_row["method"],
            swagger_row["path"],
            swagger_row["deprecated"],
        )
        assert key in inventory_index, key


def test_inventory_rows_are_complete_and_package_mapping_is_stable() -> None:
    for row in _read_inventory_rows():
        assert row["package_sdk"] == DOC_TO_PACKAGE[row["document"]]
        assert row["domain_object"]
        assert row["public_method_sdk"]
        assert row["type_request"]
        assert row["type_response"]
        assert row["type_test"]
