"""Внутренние утилиты детерминированного чтения env и `.env`."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path


def read_dotenv(env_file: str | Path | None) -> dict[str, str]:
    """Читает простой `.env` файл без побочных эффектов."""

    if env_file is None:
        return {}

    path = Path(env_file)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        cleaned_value = value.strip()
        if len(cleaned_value) >= 2 and cleaned_value[0] == cleaned_value[-1]:
            if cleaned_value[0] in {"'", '"'}:
                cleaned_value = cleaned_value[1:-1]
        values[key.strip()] = cleaned_value
    return values


def resolve_env_aliases(
    aliases_by_field: Mapping[str, tuple[str, ...]],
    *,
    env_file: str | Path | None,
) -> dict[str, str]:
    """Разрешает env alias-имена с приоритетом process environment над `.env`."""

    file_values = read_dotenv(env_file)
    resolved: dict[str, str] = {}

    for field_name, aliases in aliases_by_field.items():
        for source in (os.environ, file_values):
            value = _first_present(source, aliases)
            if value is not None:
                resolved[field_name] = value
                break

    return resolved


def _first_present(source: Mapping[str, str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        value = source.get(alias)
        if value is not None and value != "":
            return value
    return None
