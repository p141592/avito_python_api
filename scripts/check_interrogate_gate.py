"""Interrogate diff-gate: проверяет, что изменённые модули не ухудшили покрытие docstrings.

Использование:
    python scripts/check_interrogate_gate.py [--baseline .interrogate-baseline] [--base-ref origin/main]

Сравнивает текущее покрытие docstrings в каждом изменённом avito/*.py модуле с
зафиксированным baseline. Завершается с ненулевым кодом, если покрытие упало.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def get_changed_modules(base_ref: str) -> list[str]:
    """Возвращает список изменённых .py файлов в avito/ по сравнению с base_ref."""

    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Предупреждение: git diff завершился с кодом {result.returncode}", file=sys.stderr)
        return []
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip().startswith("avito/") and line.strip().endswith(".py")
    ]


def get_module_coverage(module_path: str) -> float | None:
    """Запускает interrogate для одного файла и возвращает процент покрытия."""

    result = subprocess.run(
        ["poetry", "run", "interrogate", module_path, "--fail-under=0", "-vv"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    basename = Path(module_path).name
    # Ищем строку с именем файла в Summary-таблице (целое %; совпадает с baseline).
    match = re.search(
        r"\|\s+" + re.escape(basename) + r"\s+\|\s+\d+\s+\|\s+\d+\s+\|\s+\d+\s+\|\s+(\d+)%",
        output,
    )
    if match:
        return float(match.group(1))
    return None


def load_baseline(baseline_path: Path) -> dict[str, float]:
    """Загружает baseline из JSON-файла."""

    if not baseline_path.exists():
        return {}
    with baseline_path.open() as f:
        data = json.load(f)
    return {k: float(v) for k, v in data.get("modules", {}).items()}


def main() -> int:
    """Запускает interrogate diff-gate и возвращает код выхода."""

    parser = argparse.ArgumentParser(description="Interrogate diff-gate против baseline")
    parser.add_argument("--baseline", default=".interrogate-baseline", help="Путь к baseline-файлу")
    parser.add_argument("--base-ref", default="origin/main", help="Git ref для сравнения")
    args = parser.parse_args()

    baseline = load_baseline(Path(args.baseline))
    changed = get_changed_modules(args.base_ref)

    if not changed:
        print("Нет изменённых avito/ модулей — gate пройден.")
        return 0

    failures: list[str] = []
    for module in changed:
        current = get_module_coverage(module)
        if current is None:
            print(f"  ПРОПУСК {module}: не удалось получить покрытие")
            continue

        baseline_value = baseline.get(module)
        if baseline_value is None:
            print(f"  НОВЫЙ   {module}: {current:.0f}% (не в baseline)")
            continue

        delta = current - baseline_value
        status = "OK" if delta >= 0 else "УПАЛО"
        print(f"  {status:6s} {module}: {current:.0f}% (baseline {baseline_value:.0f}%, delta {delta:+.0f}%)")
        if delta < 0:
            failures.append(f"{module}: {current:.0f}% < baseline {baseline_value:.0f}%")

    if failures:
        print(f"\nGate провален — покрытие упало в {len(failures)} модуле(ях):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\nGate пройден — {len(changed)} изменённых модулей, регрессий нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
