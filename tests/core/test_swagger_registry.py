from __future__ import annotations

import json
from pathlib import Path

import pytest

from avito.core.swagger_registry import (
    SwaggerRegistryError,
    load_swagger_registry,
    normalize_swagger_path,
)


def test_load_swagger_registry_extracts_current_corpus_counts() -> None:
    registry = load_swagger_registry()

    assert len(registry.specs) == 23
    assert len(registry.operations) == 204
    assert len(registry.deprecated_operations) == 7
    assert registry.errors == ()


def test_load_swagger_registry_extracts_operation_level_deprecated_policy_set() -> None:
    registry = load_swagger_registry()

    assert [operation.key for operation in registry.deprecated_operations] == [
        "CPAАвито.json GET /cpa/v1/call/{call_id}",
        "CPAАвито.json POST /cpa/v2/balanceInfo",
        "CPAАвито.json POST /cpa/v2/callById",
        "Автозагрузка.json GET /autoload/v1/profile",
        "Автозагрузка.json POST /autoload/v1/profile",
        "Автозагрузка.json GET /autoload/v2/reports/last_completed_report",
        "Автозагрузка.json GET /autoload/v2/reports/{report_id}",
    ]


def test_load_swagger_registry_extracts_operation_contract_metadata() -> None:
    registry = load_swagger_registry()

    operation = next(
        operation
        for operation in registry.operations
        if operation.key
        == "Мессенджер.json POST /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
    )

    assert operation.operation_id == "postSendMessage"
    assert operation.deprecated is False
    assert [parameter.name for parameter in operation.path_parameters] == ["user_id", "chat_id"]
    assert [parameter.name for parameter in operation.header_parameters] == ["Authorization"]
    assert operation.request_body is not None
    assert operation.request_body.content_types == ("application/json",)
    assert [(response.status_code, response.content_types) for response in operation.responses] == [
        ("200", ("application/json",)),
    ]


def test_normalize_swagger_path_removes_trailing_slash() -> None:
    assert normalize_swagger_path("/core/v1/accounts/{user_id}/balance/") == (
        "/core/v1/accounts/{user_id}/balance"
    )


def test_load_swagger_registry_rejects_path_parameter_mismatch(tmp_path: Path) -> None:
    spec_path = tmp_path / "Broken.json"
    spec_path.write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {
                    "/items/{item_id}": {
                        "get": {
                            "operationId": "getItem",
                            "parameters": [
                                {
                                    "name": "wrong_id",
                                    "in": "path",
                                    "required": True,
                                }
                            ],
                            "responses": {"200": {"description": "ok"}},
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SwaggerRegistryError, match="path parameters"):
        load_swagger_registry(tmp_path, strict=True)


def test_load_swagger_registry_records_path_parameter_mismatch_in_non_strict_mode(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "Broken.json"
    spec_path.write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {
                    "/items/{item_id}": {
                        "get": {
                            "operationId": "getItem",
                            "parameters": [
                                {
                                    "name": "wrong_id",
                                    "in": "path",
                                    "required": True,
                                }
                            ],
                            "responses": {"200": {"description": "ok"}},
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    registry = load_swagger_registry(tmp_path)

    assert len(registry.operations) == 1
    assert len(registry.errors) == 1
    assert registry.errors[0].code == "SWAGGER_PATH_PARAMETER_MISMATCH"
