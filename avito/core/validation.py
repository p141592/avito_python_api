"""Внутренние валидаторы входных данных доменного слоя."""

from __future__ import annotations

from collections.abc import Sequence

from avito.core.exceptions import ValidationError


def validate_non_empty(name: str, items: Sequence[object]) -> None:
    """Проверяет, что последовательность содержит хотя бы один элемент."""
    if not items:
        raise ValidationError(f"`{name}` должен содержать хотя бы один элемент.")


def validate_positive_int(name: str, value: int) -> None:
    """Проверяет, что значение является положительным целым числом."""
    if value <= 0:
        raise ValidationError(f"`{name}` должен быть положительным целым числом.")


def validate_non_empty_string(name: str, value: str) -> None:
    """Проверяет, что строка не является пустой или состоящей из пробелов."""
    if not value.strip():
        raise ValidationError(f"`{name}` не может быть пустой строкой.")


def validate_string_items(name: str, values: Sequence[str]) -> None:
    """Проверяет, что список строк непустой и каждая строка непустая."""
    validate_non_empty(name, values)
    for index, value in enumerate(values):
        validate_non_empty_string(f"{name}[{index}]", value)


__all__ = (
    "validate_non_empty",
    "validate_non_empty_string",
    "validate_positive_int",
    "validate_string_items",
)
