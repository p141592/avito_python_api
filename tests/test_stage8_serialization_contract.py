from __future__ import annotations

import importlib
import json
from dataclasses import is_dataclass
from inspect import isclass

from avito.autoteka.models import CatalogField, CatalogFieldValue, CatalogResolveResult
from avito.core.types import BinaryResponse
from avito.cpa.models import CallTrackingRecord, CpaAudioRecord
from avito.messenger.models import SendMessageRequest
from avito.orders.models import LabelPdfResult
from avito.tariffs.models import TariffContractInfo, TariffInfo

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


def iter_model_classes() -> list[tuple[str, str, type[object]]]:
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


def test_all_model_dataclasses_expose_standard_serialization_methods() -> None:
    missing = [
        f"{module_name}:{name}"
        for module_name, name, cls in iter_model_classes()
        if not hasattr(cls, "to_dict") or not hasattr(cls, "model_dump")
    ]

    assert missing == []


def test_recursive_serialization_is_json_compatible_and_hides_transport_fields() -> None:
    tariff = TariffInfo(
        current=TariffContractInfo(
            level="Максимальный",
            is_active=True,
            start_time=1713427200,
            close_time=None,
            bonus=10,
            price=1990,
            original_price=2490,
            packages_count=2,
        ),
        scheduled=None,
    )
    catalog = CatalogResolveResult(
        items=[
            CatalogField(
                field_id="brand",
                label="Марка",
                data_type="integer",
                values=[
                    CatalogFieldValue(
                        value_id="1",
                        label="Audi",
                    )
                ],
            )
        ],
    )
    request = SendMessageRequest(message="hello")

    assert tariff.to_dict() == {
        "current": {
            "level": "Максимальный",
            "is_active": True,
            "start_time": 1713427200,
            "close_time": None,
            "bonus": 10,
            "price": 1990,
            "original_price": 2490,
            "packages_count": 2,
        },
        "scheduled": None,
    }
    assert catalog.model_dump() == {
        "items": [
            {
                "field_id": "brand",
                "label": "Марка",
                "data_type": "integer",
                "values": [{"value_id": "1", "label": "Audi"}],
            }
        ]
    }
    assert request.to_dict() == {"message": "hello", "type": None}

    json.dumps(tariff.to_dict())
    json.dumps(catalog.to_dict())
    json.dumps(request.to_dict())


def test_binary_result_models_serialize_without_transport_objects() -> None:
    response = BinaryResponse(
        content=b"\x00\x01payload",
        content_type="application/octet-stream",
        filename="artifact.bin",
        status_code=200,
        headers={"x-test": "1"},
    )

    pdf = LabelPdfResult(binary=response)
    audio = CpaAudioRecord(binary=response)
    tracking = CallTrackingRecord(binary=response)

    expected = {
        "filename": "artifact.bin",
        "content_type": "application/octet-stream",
        "content_base64": "AAFwYXlsb2Fk",
    }

    assert pdf.to_dict() == expected
    assert audio.model_dump() == expected
    assert tracking.to_dict() == expected

    assert "binary" not in pdf.to_dict()
    assert "status_code" not in pdf.to_dict()
    assert "headers" not in pdf.to_dict()

    json.dumps(pdf.to_dict())
