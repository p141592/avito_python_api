"""Публичная сериализация SDK-моделей без transport-деталей."""

from __future__ import annotations

from base64 import b64encode
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from inspect import isclass
from typing import Any, cast


def _is_public_field(name: str) -> bool:
    return not name.startswith("_") and name != "raw_payload"


def _serialize_value(value: object) -> object:
    if isinstance(value, SerializableModel):
        return value.to_dict()
    if isinstance(value, bytes | bytearray):
        return b64encode(bytes(value)).decode("ascii")
    if is_dataclass(value):
        return {
            field.name: _serialize_value(getattr(value, field.name))
            for field in fields(value)
            if _is_public_field(field.name)
        }
    if isinstance(value, Mapping):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_serialize_value(item) for item in value]
    return value


class SerializableModel:
    """Mixin для стабильной JSON-compatible сериализации публичных моделей."""

    def to_dict(self) -> dict[str, Any]:
        if not is_dataclass(self):
            raise TypeError("SerializableModel supports dataclass instances only.")
        return {
            field.name: _serialize_value(getattr(self, field.name))
            for field in fields(self)
            if _is_public_field(field.name)
        }

    def model_dump(self) -> dict[str, Any]:
        """Совместимый alias для pydantic-подобного публичного контракта."""

        return self.to_dict()


def enable_module_serialization(namespace: Mapping[str, object]) -> None:
    """Добавляет `to_dict()` / `model_dump()` всем dataclass-моделям модуля."""

    module_name = namespace.get("__name__")
    for value in namespace.values():
        if not isclass(value) or getattr(value, "__module__", None) != module_name:
            continue
        if not is_dataclass(value) or hasattr(value, "to_dict"):
            continue
        dynamic_value = cast(Any, value)
        dynamic_value.to_dict = SerializableModel.to_dict
        dynamic_value.model_dump = SerializableModel.model_dump


__all__ = ("SerializableModel", "enable_module_serialization")
