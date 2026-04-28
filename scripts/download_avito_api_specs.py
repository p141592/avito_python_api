"""Download Avito API OpenAPI specifications from the public developer portal."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

BASE_URL = "https://developers.avito.ru"
LIST_URL = f"{BASE_URL}/web/1/openapi/list"
INFO_URL_TEMPLATE = f"{BASE_URL}/web/1/openapi/info/{{slug}}"
DEFAULT_OUTPUT_DIR = Path("docs/avito/api")


@dataclass(frozen=True, slots=True)
class ApiCatalogItem:
    slug: str
    title: str


def run_curl(url: str) -> str:
    result = subprocess.run(
        ["curl", "-fsSL", url],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or f"curl завершился с кодом {result.returncode}"
        raise RuntimeError(f"Не удалось скачать {url}: {message}")
    return result.stdout


def load_json(raw: str, source: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Источник {source} вернул некорректный JSON: {exc}") from exc


def get_string_field(data: object, field: str, source: str) -> str:
    if not isinstance(data, dict):
        raise RuntimeError(f"Источник {source} вернул объект неверного типа")
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"Источник {source} не содержит строковое поле {field!r}")
    return value


def fetch_catalog() -> list[ApiCatalogItem]:
    raw_catalog = load_json(run_curl(LIST_URL), LIST_URL)
    if not isinstance(raw_catalog, list):
        raise RuntimeError(f"Источник {LIST_URL} вернул не список API")

    catalog: list[ApiCatalogItem] = []
    for raw_item in raw_catalog:
        slug = get_string_field(raw_item, "slug", LIST_URL)
        title = get_string_field(raw_item, "title", LIST_URL)
        catalog.append(ApiCatalogItem(slug=slug, title=title))
    return catalog


def fetch_swagger(slug: str) -> object:
    source_url = INFO_URL_TEMPLATE.format(slug=slug)
    raw_info = load_json(run_curl(source_url), source_url)
    raw_swagger = get_string_field(raw_info, "swagger", source_url)
    return load_json(raw_swagger, source_url)


def normalize_filename(title: str) -> str:
    title_without_suffix = re.sub(r"\s*\([^)]*\)\s*$", "", title)
    normalized = re.sub(r"\s+", "", title_without_suffix)
    normalized = re.sub(r"[^\w\-\[\]]+", "", normalized, flags=re.UNICODE)
    if not normalized:
        raise RuntimeError(f"Не удалось нормализовать имя файла для {title!r}")
    return f"{normalized}.json"


def save_spec(spec: object, destination: Path) -> None:
    destination.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def download_specs(output_dir: Path, dry_run: bool) -> int:
    catalog = fetch_catalog()
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_count = 0
    for item in catalog:
        destination = output_dir / normalize_filename(item.title)
        if dry_run:
            print(f"{item.slug}: {destination}")
            continue

        spec = fetch_swagger(item.slug)
        save_spec(spec, destination)
        print(f"{item.slug}: {destination}")
        saved_count += 1

    return saved_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скачать Swagger/OpenAPI спецификации Авито в docs/avito/api.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Каталог для сохранения спецификаций.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать целевые имена файлов без скачивания спецификаций.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        saved_count = download_specs(args.output_dir, args.dry_run)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.dry_run:
        return 0

    print(f"Скачано спецификаций: {saved_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
