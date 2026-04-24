"""Проверяет, что python/pycon блоки в reference/ и explanations/ не являются «orphaned».

Orphaned блок — fenced code block с меткой `python` или `pycon`, который находится в
`docs/site/reference/` или `docs/site/explanations/` и НЕ включён в mktestdocs-сборщик
(README.md, tutorials/*.md, how-to/*.md).

По умолчанию такие блоки запрещены: если блок показывает SDK-вызов, он должен либо
исполняться через тот же harness, либо быть помечен нейтральным fence (text, console и т.д.).

Использование:
    python scripts/check_docs_examples.py [--output report.json] [--strict]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DOCS_ROOT = Path("docs/site")
CHECKED_DIRS = ["reference", "explanations"]
EXECUTABLE_DIRS = ["tutorials", "how-to"]
EXECUTABLE_FILES = ["README.md"]

EXECUTABLE_FENCE = re.compile(r"^```(python|pycon)\s*$", re.MULTILINE)
ANY_FENCE_OPEN = re.compile(r"^```(\S*)\s*$", re.MULTILINE)


def collect_executable_fences(paths: list[Path]) -> set[str]:
    """Собирает содержимое python/pycon блоков из executable-файлов."""

    blocks: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for block in extract_fenced_blocks(text, {"python", "pycon"}):
            blocks.add(block.strip())
    return blocks


def extract_fenced_blocks(text: str, fence_types: set[str]) -> list[str]:
    """Извлекает содержимое fenced-блоков заданных типов."""

    blocks: list[str] = []
    lines = text.splitlines()
    in_block = False
    current_lines: list[str] = []

    for line in lines:
        if not in_block:
            m = re.match(r"^```(\S*)\s*$", line)
            if m:
                fence_type = m.group(1).lower()
                if fence_type in fence_types:
                    in_block = True
                    current_lines = []
        else:
            if line.strip() == "```":
                blocks.append("\n".join(current_lines))
                in_block = False
                current_lines = []
            else:
                current_lines.append(line)

    return blocks


def find_orphaned_blocks(
    checked_dirs: list[Path],
    executable_blocks: set[str],
) -> list[dict[str, object]]:
    """Находит python/pycon блоки в reference/explanations, не покрытые harness."""

    gaps: list[dict[str, object]] = []
    for directory in checked_dirs:
        if not directory.exists():
            continue
        for md_file in sorted(directory.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            blocks = extract_fenced_blocks(text, {"python", "pycon"})
            for block in blocks:
                if block.strip() not in executable_blocks:
                    gaps.append(
                        {
                            "file": str(md_file),
                            "block_preview": block.strip()[:120],
                        }
                    )
    return gaps


def main() -> int:
    """Запускает проверку и возвращает код выхода."""

    parser = argparse.ArgumentParser(
        description="Проверяет orphaned python-блоки в reference/explanations"
    )
    parser.add_argument("--output", default=None, help="Путь для JSON-отчёта")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Завершиться с кодом 1 при наличии gaps",
    )
    args = parser.parse_args()

    executable_paths: list[Path] = []
    for name in EXECUTABLE_FILES:
        executable_paths.append(Path(name))
    for d in EXECUTABLE_DIRS:
        executable_paths.extend(sorted((DOCS_ROOT / d).rglob("*.md")))

    executable_blocks = collect_executable_fences(executable_paths)

    checked_dirs = [DOCS_ROOT / d for d in CHECKED_DIRS]
    gaps = find_orphaned_blocks(checked_dirs, executable_blocks)

    report = {
        "checked_dirs": CHECKED_DIRS,
        "executable_sources": [str(p) for p in executable_paths if p.exists()],
        "gap_count": len(gaps),
        "gaps": gaps,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"Отчёт сохранён в {args.output}")

    if gaps:
        print(
            f"Найдено {len(gaps)} orphaned python/pycon блок(а/ов) "
            "в reference/ или explanations/:"
        )
        for g in gaps:
            print(f"  {g['file']}")
            print(f"    {g['block_preview']!r}")
        if args.strict:
            return 1
    else:
        print(
            f"reference_explanation_examples_gaps=0 "
            f"(проверено {len(checked_dirs)} директорий)"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
