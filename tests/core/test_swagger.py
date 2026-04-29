from __future__ import annotations

import builtins
import importlib
from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

import pytest

import avito.core.swagger
from avito.core import SwaggerOperationBinding, swagger_operation


@contextmanager
def _forbid_swagger_file_reads() -> Iterator[None]:
    original_open = builtins.open

    def guarded_open(file: object, *args: object, **kwargs: object) -> object:
        if "docs/avito/api" in str(file):
            raise AssertionError("Swagger files must not be read on import")
        return original_open(file, *args, **kwargs)

    builtins.open = guarded_open
    try:
        yield
    finally:
        builtins.open = original_open


def test_swagger_operation_writes_metadata_to_decorated_method() -> None:
    @swagger_operation(
        "get",
        "/messenger/v1/accounts/{user_id}/chats/",
        spec="Мессенджер.json",
        operation_id="getChats",
        factory="chat",
        factory_args={"user_id": "path.user_id"},
        method_args={"limit": "query.limit"},
        deprecated=True,
        legacy=True,
    )
    def list_chats() -> str:
        return "ok"

    binding = cast(SwaggerOperationBinding, list_chats.__swagger_binding__)

    assert binding == SwaggerOperationBinding(
        method="GET",
        path="/messenger/v1/accounts/{user_id}/chats",
        spec="Мессенджер.json",
        operation_id="getChats",
        factory="chat",
        factory_args={"user_id": "path.user_id"},
        method_args={"limit": "query.limit"},
        deprecated=True,
        legacy=True,
    )


def test_swagger_operation_does_not_change_decorated_method_behavior() -> None:
    @swagger_operation("POST", "/items/{item_id}")
    def update_item(item_id: int, *, title: str) -> tuple[int, str]:
        return item_id, title

    assert update_item(42, title="listing") == (42, "listing")


def test_swagger_operation_stores_immutable_mapping_copies() -> None:
    factory_args = {"user_id": "path.user_id"}
    method_args = {"limit": "query.limit"}

    @swagger_operation(
        "GET",
        "/items",
        factory_args=factory_args,
        method_args=method_args,
    )
    def list_items() -> str:
        return "ok"

    factory_args["user_id"] = "query.user_id"
    method_args["limit"] = "constant.limit"
    binding = cast(SwaggerOperationBinding, list_items.__swagger_binding__)

    assert binding.factory_args["user_id"] == "path.user_id"
    assert binding.method_args["limit"] == "query.limit"
    with pytest.raises(TypeError):
        cast(dict[str, str], binding.factory_args)["extra"] = "query.extra"
    with pytest.raises(TypeError):
        cast(dict[str, str], binding.method_args)["extra"] = "query.extra"


def test_swagger_operation_rejects_forbidden_kwargs_by_signature() -> None:
    with pytest.raises(TypeError):
        swagger_operation(
            "GET",
            "/items",
            response_model="Forbidden",
        )


def test_swagger_module_does_not_read_swagger_files_on_import() -> None:
    with _forbid_swagger_file_reads():
        importlib.reload(avito.core.swagger)
