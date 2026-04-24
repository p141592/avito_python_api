from __future__ import annotations

from pathlib import Path

import mktestdocs

DOCS_ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_MARKDOWN = [
    DOCS_ROOT / "README.md",
    *sorted((DOCS_ROOT / "docs/site/tutorials").glob("*.md")),
    *sorted((DOCS_ROOT / "docs/site/how-to").glob("*.md")),
]


def execute_pycon(source: str) -> None:
    lines: list[str] = []
    for line in source.splitlines():
        if line.startswith(">>> "):
            lines.append(line[4:])
        elif line.startswith("... "):
            lines.append(line[4:])
    exec("\n".join(lines), {"__name__": "__main__"})


mktestdocs.register_executor("pycon", execute_pycon)


def test_readme_tutorial_and_howto_python_examples_execute_without_network() -> None:
    assert EXECUTABLE_MARKDOWN, "README/tutorials/how-to должны проверяться mktestdocs."

    for path in EXECUTABLE_MARKDOWN:
        try:
            mktestdocs.check_md_file(path, lang="python")
            mktestdocs.check_md_file(path, lang="pycon")
        except Exception as exc:  # noqa: BLE001
            relative_path = path.relative_to(DOCS_ROOT)
            raise AssertionError(f"Python/pycon-пример из {relative_path} не выполнился.") from exc
