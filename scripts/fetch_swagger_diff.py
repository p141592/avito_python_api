from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "docs" / "avito" / "api"
HTTP_METHODS = {"get", "post", "put", "delete", "patch"}
LIST_URL = "https://developers.avito.ru/web/1/openapi/list"
INFO_URL = "https://developers.avito.ru/web/1/openapi/info/{slug}"


def normalize_title(value: str) -> str:
    return re.sub(r"[^A-Za-zА-Яа-яЁё0-9]", "", value).casefold()


@dataclass(slots=True, frozen=True)
class Operation:
    method: str
    path: str

    def __str__(self) -> str:
        return f"{self.method:<6} {self.path}"


@dataclass(slots=True)
class ApiEntry:
    slug: str
    title: str
    spec: dict[str, object]

    @property
    def norm_key(self) -> str:
        info_title = str(self.spec.get("info", {}).get("title", self.title))  # type: ignore[union-attr]
        return normalize_title(info_title)

    def operations(self) -> set[Operation]:
        result: set[Operation] = set()
        paths = self.spec.get("paths", {})
        if not isinstance(paths, dict):
            return result
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method in path_item:
                if method.lower() in HTTP_METHODS:
                    result.add(Operation(method.upper(), path))
        return result


@dataclass(slots=True)
class LocalFile:
    path: Path

    @property
    def norm_key(self) -> str:
        return normalize_title(self.path.stem)

    def spec(self) -> dict[str, object]:
        return json.loads(self.path.read_text(encoding="utf-8"))  # type: ignore[return-value]

    def operations(self) -> set[Operation]:
        result: set[Operation] = set()
        paths = self.spec().get("paths", {})
        if not isinstance(paths, dict):
            return result
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method in path_item:
                if method.lower() in HTTP_METHODS:
                    result.add(Operation(method.upper(), path))
        return result


@dataclass(slots=True)
class SectionDiff:
    slug: str
    title: str
    filename: str
    added: list[Operation] = field(default_factory=list)
    removed: list[Operation] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)


@dataclass(slots=True)
class DiffResult:
    new_apis: list[ApiEntry] = field(default_factory=list)
    removed_apis: list[LocalFile] = field(default_factory=list)
    changed: list[SectionDiff] = field(default_factory=list)

    @property
    def total_added(self) -> int:
        return sum(len(s.added) for s in self.changed)

    @property
    def total_removed(self) -> int:
        return sum(len(s.removed) for s in self.changed)

    @property
    def has_any_changes(self) -> bool:
        return bool(self.new_apis or self.removed_apis or any(s.has_changes for s in self.changed))


def fetch_catalog(client: httpx.Client) -> list[dict[str, str]]:
    resp = client.get(LIST_URL)
    resp.raise_for_status()
    return resp.json()  # type: ignore[no-any-return]


def fetch_spec(client: httpx.Client, slug: str) -> dict[str, object]:
    url = INFO_URL.format(slug=slug)
    resp = client.get(url)
    resp.raise_for_status()
    payload = resp.json()
    return json.loads(payload["swagger"])  # type: ignore[no-any-return]


def load_local_files() -> dict[str, LocalFile]:
    result: dict[str, LocalFile] = {}
    for path in sorted(SPEC_DIR.glob("*.json")):
        local = LocalFile(path)
        result[local.norm_key] = local
    return result


def _find_local_key(entry_key: str, local_files: dict[str, LocalFile]) -> str | None:
    if entry_key in local_files:
        return entry_key
    # Fuzzy prefix match handles titles that gained/lost suffixes like "(beta-version)".
    for local_key in local_files:
        if entry_key.startswith(local_key) or local_key.startswith(entry_key):
            return local_key
    return None


def compute_diff(remote_entries: list[ApiEntry], local_files: dict[str, LocalFile]) -> DiffResult:
    diff = DiffResult()
    matched_local_keys: set[str] = set()

    for entry in remote_entries:
        key = entry.norm_key
        matched_key = _find_local_key(key, local_files)
        if matched_key is None:
            diff.new_apis.append(entry)
            continue

        local = local_files[matched_key]
        matched_local_keys.add(matched_key)

        remote_ops = entry.operations()
        local_ops = local.operations()
        added = sorted(remote_ops - local_ops, key=lambda op: (op.path, op.method))
        removed = sorted(local_ops - remote_ops, key=lambda op: (op.path, op.method))

        section = SectionDiff(
            slug=entry.slug,
            title=entry.title,
            filename=local.path.name,
            added=added,
            removed=removed,
        )
        diff.changed.append(section)

    for key, local in local_files.items():
        if key not in matched_local_keys:
            diff.removed_apis.append(local)

    diff.changed.sort(key=lambda s: s.title)
    return diff


def print_diff(diff: DiffResult) -> None:
    if not diff.has_any_changes:
        print("Изменений не найдено.")
        return

    if diff.new_apis:
        print("=== Новые API-разделы ===")
        for entry in sorted(diff.new_apis, key=lambda e: e.title):
            print(f"  + {entry.slug:<30}  {entry.title}")
        print()

    if diff.removed_apis:
        print("=== Удалённые API-разделы ===")
        for local in sorted(diff.removed_apis, key=lambda f: f.path.name):
            print(f"  - {local.path.name}")
        print()

    changed_sections = [s for s in diff.changed if s.has_changes]
    if changed_sections:
        print("=== Изменения в существующих разделах ===")
        for section in changed_sections:
            print(f"\n  [{section.title}]  ({section.filename})")
            for op in section.added:
                print(f"    + {op}")
            for op in section.removed:
                print(f"    - {op}")
        print()

    sections_changed = len(changed_sections)
    print(
        f"Итог: {sections_changed} раздел(ов) изменено, "
        f"{diff.total_added} операций добавлено, "
        f"{diff.total_removed} удалено."
    )
    if diff.new_apis:
        print(f"  Новых API-разделов: {len(diff.new_apis)}")
    if diff.removed_apis:
        print(f"  Удалённых API-разделов: {len(diff.removed_apis)}")


def build_json_report(diff: DiffResult) -> dict[str, object]:
    return {
        "new_apis": [{"slug": e.slug, "title": e.title} for e in diff.new_apis],
        "removed_apis": [f.path.name for f in diff.removed_apis],
        "changed": [
            {
                "slug": s.slug,
                "title": s.title,
                "filename": s.filename,
                "added": [{"method": op.method, "path": op.path} for op in s.added],
                "removed": [{"method": op.method, "path": op.path} for op in s.removed],
            }
            for s in diff.changed
            if s.has_changes
        ],
        "summary": {
            "new_api_count": len(diff.new_apis),
            "removed_api_count": len(diff.removed_apis),
            "changed_section_count": sum(1 for s in diff.changed if s.has_changes),
            "total_added_ops": diff.total_added,
            "total_removed_ops": diff.total_removed,
        },
    }


def update_files(remote_entries: list[ApiEntry], local_files: dict[str, LocalFile]) -> None:
    updated = 0
    created = 0
    for entry in remote_entries:
        key = entry.norm_key
        if key in local_files:
            target = local_files[key].path
            target.write_text(
                json.dumps(entry.spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            updated += 1
        else:
            info_title = str(entry.spec.get("info", {}).get("title", entry.title))  # type: ignore[union-attr]
            filename = re.sub(r"[^A-Za-zА-Яа-яЁё0-9\[\]\-]", "", info_title) + ".json"
            target = SPEC_DIR / filename
            target.write_text(
                json.dumps(entry.spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            created += 1
            print(f"  Создан: {filename}", file=sys.stderr)
    print(f"Обновлено: {updated}, создано: {created} файлов.", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Скачать swagger-спецификации с developers.avito.ru и показать diff с docs/avito/api/."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Перезаписать файлы в docs/avito/api/ актуальными версиями.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="Сохранить машиночитаемый diff в JSON-файл.",
    )
    args = parser.parse_args()

    print("Загружаю список API...", file=sys.stderr)
    with httpx.Client(timeout=30) as client:
        catalog = fetch_catalog(client)
        remote_entries: list[ApiEntry] = []
        for item in catalog:
            slug = item["slug"]
            title = item.get("title", slug)
            print(f"  Скачиваю {slug} ({title})...", file=sys.stderr)
            spec = fetch_spec(client, slug)
            remote_entries.append(ApiEntry(slug=slug, title=title, spec=spec))

    print(f"Скачано {len(remote_entries)} спецификаций.", file=sys.stderr)

    local_files = load_local_files()
    diff = compute_diff(remote_entries, local_files)

    print_diff(diff)

    if args.output:
        report = build_json_report(diff)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nJSON-отчёт сохранён: {args.output}", file=sys.stderr)

    if args.update:
        print("\nОбновляю файлы...", file=sys.stderr)
        update_files(remote_entries, local_files)


if __name__ == "__main__":
    main()
