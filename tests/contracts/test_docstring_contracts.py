from __future__ import annotations

import ast
from pathlib import Path

GENERIC_DOCSTRING_FRAGMENTS = (
    "Выполняет публичную операцию",
    "Пустой результат возвращается",
)


def test_public_domain_docstrings_do_not_use_generic_fragments() -> None:
    offenders: list[str] = []
    for path in sorted(Path("avito").glob("*/domain.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for class_node in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for function_node in (
                node for node in class_node.body if isinstance(node, ast.FunctionDef)
            ):
                docstring = ast.get_docstring(function_node) or ""
                if any(fragment in docstring for fragment in GENERIC_DOCSTRING_FRAGMENTS):
                    offenders.append(f"{path}:{class_node.name}.{function_node.name}")

    assert offenders == []
