from __future__ import annotations

import re
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_MARKDOWN = [
    *sorted((DOCS_ROOT / "docs/site/tutorials").glob("*.md")),
    *sorted((DOCS_ROOT / "docs/site/how-to").glob("*.md")),
]
PYTHON_BLOCK = re.compile(r"```(?:python|pycon)\n(.*?)\n```", re.DOTALL)


def executable_blocks(path: Path) -> list[str]:
    return [match.group(1) for match in PYTHON_BLOCK.finditer(path.read_text(encoding="utf-8"))]


def test_tutorial_and_howto_python_examples_execute_without_network() -> None:
    namespace: dict[str, object] = {}
    blocks = [(path, block) for path in EXECUTABLE_MARKDOWN for block in executable_blocks(path)]

    assert blocks, "В tutorials/how-to должен быть хотя бы один исполняемый Python-пример."

    for path, block in blocks:
        try:
            exec(compile(block, str(path), "exec"), namespace)
        except Exception as exc:  # noqa: BLE001
            raise AssertionError(f"Python-пример из {path} не выполнился.") from exc
