from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"
DEFAULT_OUTPUT = ROOT / "changelog-sections-report.json"
REQUIRED_SECTIONS = ("Added", "Changed", "Deprecated", "Removed", "Fixed")


@dataclass(slots=True, frozen=True)
class ChangelogGap:
    version: str
    section: str
    reason: str


def current_release_block(text: str) -> tuple[str, str]:
    heading = re.search(r"^## \[(?P<version>[^\]]+)\].*$", text, re.MULTILINE)
    if heading is None:
        raise ValueError("В CHANGELOG.md не найден заголовок версии `## [...]`.")
    next_heading = re.search(r"^## \[", text[heading.end() :], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading is not None else len(text)
    return heading.group("version"), text[heading.end() : end]


def collect_gaps(path: Path) -> list[ChangelogGap]:
    version, block = current_release_block(path.read_text(encoding="utf-8"))
    sections = set(re.findall(r"^### ([A-Za-z]+)\s*$", block, re.MULTILINE))
    return [
        ChangelogGap(version, section, "секция отсутствует в текущем релизном блоке")
        for section in REQUIRED_SECTIONS
        if section not in sections
    ]


def write_report(gaps: list[ChangelogGap], output: Path) -> None:
    report = {
        "required_sections": list(REQUIRED_SECTIONS),
        "gaps": [asdict(gap) for gap in gaps],
        "gap_count": len(gaps),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить секции текущего CHANGELOG-блока.")
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    gaps = collect_gaps(args.changelog)
    write_report(gaps, args.output)
    if args.strict and gaps:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
