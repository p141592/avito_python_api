from __future__ import annotations

import importlib
from dataclasses import fields, is_dataclass
from inspect import isclass

MODEL_MODULES = (
    "avito.accounts.models",
    "avito.ads.models",
    "avito.autoteka.models",
    "avito.cpa.models",
    "avito.jobs.models",
    "avito.messenger.models",
    "avito.orders.models",
    "avito.promotion.models",
    "avito.ratings.models",
    "avito.realty.models",
    "avito.tariffs.models",
)


def iter_public_dataclasses() -> list[tuple[str, str, type[object]]]:
    classes: list[tuple[str, str, type[object]]] = []
    for module_name in MODEL_MODULES:
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not isclass(value) or getattr(value, "__module__", None) != module_name:
                continue
            if not is_dataclass(value):
                continue
            classes.append((module_name, name, value))
    return classes


def test_no_public_model_declares_raw_payload_field() -> None:
    offenders = []
    for module_name, name, cls in iter_public_dataclasses():
        if any(field.name in {"raw_payload", "_payload"} for field in fields(cls)):
            offenders.append(f"{module_name}:{name}")

    assert offenders == []
