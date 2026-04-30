"""Download Avito API OpenAPI specifications from the public developer portal."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

BASE_URL = "https://developers.avito.ru"
API_CATALOG_URL = f"{BASE_URL}/api-catalog"
DOCUMENTATION_URL_TEMPLATE = f"{API_CATALOG_URL}/{{slug}}/documentation"
DEFAULT_OUTPUT_DIR = Path("docs/avito/api")
DEFAULT_CONNECT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_TIME_SECONDS = 180


@dataclass(frozen=True, slots=True)
class ApiCatalogItem:
    slug: str
    title: str
    documentation_url: str


@dataclass(frozen=True, slots=True)
class ApiCatalogSource:
    data_base_url: str

    @property
    def list_url(self) -> str:
        return f"{self.data_base_url}/list"

    def info_url(self, slug: str) -> str:
        return f"{self.data_base_url}/info/{slug}"


def run_curl(url: str, source_url: str) -> str:
    result = subprocess.run(
        [
            "curl",
            "-fsSL",
            "--connect-timeout",
            str(DEFAULT_CONNECT_TIMEOUT_SECONDS),
            "--max-time",
            str(DEFAULT_MAX_TIME_SECONDS),
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or f"curl завершился с кодом {result.returncode}"
        raise RuntimeError(f"Не удалось скачать {source_url}: {message}")
    return result.stdout


def discover_catalog_source(page_html: str) -> ApiCatalogSource:
    script_match = re.search(
        r'<script[^>]+src="([^"]*open-api-dev-portal[^"]+\.js)"',
        page_html,
    )
    if script_match is None:
        raise RuntimeError(f"Источник {API_CATALOG_URL} не содержит JS каталога API")

    script_url = urljoin(BASE_URL, script_match.group(1))
    script = run_curl(script_url, API_CATALOG_URL)
    data_base_match = re.search(r'"(/web/\d+/openapi)"', script)
    if data_base_match is None:
        raise RuntimeError(f"Источник {API_CATALOG_URL} не содержит data endpoint каталога API")

    return ApiCatalogSource(data_base_url=urljoin(BASE_URL, data_base_match.group(1)))


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
    catalog, _source = fetch_catalog_with_source()
    return catalog


def fetch_catalog_with_source() -> tuple[list[ApiCatalogItem], ApiCatalogSource]:
    page_html = run_curl(API_CATALOG_URL, API_CATALOG_URL)
    source = discover_catalog_source(page_html)
    raw_catalog = load_json(run_curl(source.list_url, API_CATALOG_URL), API_CATALOG_URL)
    if not isinstance(raw_catalog, list):
        raise RuntimeError(f"Источник {API_CATALOG_URL} вернул не список API")

    catalog: list[ApiCatalogItem] = []
    for raw_item in raw_catalog:
        slug = get_string_field(raw_item, "slug", API_CATALOG_URL)
        title = get_string_field(raw_item, "title", API_CATALOG_URL)
        documentation_url = DOCUMENTATION_URL_TEMPLATE.format(slug=slug)
        catalog.append(ApiCatalogItem(slug=slug, title=title, documentation_url=documentation_url))
    return catalog, source


def fetch_swagger(item: ApiCatalogItem, source: ApiCatalogSource) -> object:
    data_url = source.info_url(item.slug)
    raw_info = load_json(run_curl(data_url, item.documentation_url), item.documentation_url)
    raw_swagger = get_string_field(raw_info, "swagger", item.documentation_url)
    return load_json(raw_swagger, item.documentation_url)


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


def remove_stale_specs(output_dir: Path, expected_files: set[Path]) -> int:
    removed_count = 0
    for path in output_dir.glob("*.json"):
        if path not in expected_files:
            path.unlink()
            print(f"Удалена устаревшая спецификация: {path}")
            removed_count += 1
    return removed_count


def download_specs(output_dir: Path, dry_run: bool, clean: bool) -> int:
    catalog, source = fetch_catalog_with_source()
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_files = {output_dir / normalize_filename(item.title) for item in catalog}

    if clean and not dry_run:
        remove_stale_specs(output_dir, expected_files)

    saved_count = 0
    for item in catalog:
        destination = output_dir / normalize_filename(item.title)
        if dry_run:
            print(f"{item.slug}: {destination}")
            continue

        spec = fetch_swagger(item, source)
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
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Удалить локальные JSON-файлы, которых больше нет в upstream catalog.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        saved_count = download_specs(args.output_dir, args.dry_run, args.clean)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.dry_run:
        return 0

    print(f"Скачано спецификаций: {saved_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
