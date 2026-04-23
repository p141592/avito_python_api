from __future__ import annotations

import re
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER_PATTERN = re.compile(
    r"Раздел в разработке|placeholder|плейсхолдер|TODO|TBD|coming soon",
    re.IGNORECASE,
)


def test_production_docs_do_not_contain_placeholders() -> None:
    offenders: list[str] = []
    for path in sorted((DOCS_ROOT / "docs/site").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_PATTERN.search(text):
            offenders.append(str(path.relative_to(DOCS_ROOT)))

    assert offenders == []
