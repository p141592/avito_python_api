from __future__ import annotations

from dataclasses import dataclass

from avito.core import (
    ApiModel,
    BinaryResponse,
    EmptyResponse,
    OperationExecutor,
    OperationSpec,
    RequestModel,
    api_field,
)
from avito.core.operations import render_path
from avito.testing import FakeTransport


def test_render_path_encodes_path_params() -> None:
    assert render_path("/items/{item_id}", {"item_id": "a/b"}) == "/items/a%2Fb"


@dataclass(slots=True, frozen=True)
class ItemQuery(RequestModel):
    page: int
    item_id: str = api_field("itemId")


@dataclass(slots=True, frozen=True)
class ItemRequest(RequestModel):
    title: str
    price: int | None = None


@dataclass(slots=True, frozen=True)
class ItemResponse(ApiModel):
    item_id: str
    title: str

    @classmethod
    def from_payload(cls, payload: object) -> ItemResponse:
        if not isinstance(payload, dict):
            raise AssertionError("expected payload mapping")
        return cls(item_id=str(payload["id"]), title=str(payload["title"]))


def test_operation_executor_serializes_path_query_request_and_response_model() -> None:
    fake_transport = FakeTransport()
    fake_transport.add_json("POST", "/items/a/b", {"id": "a/b", "title": "new"})
    transport = fake_transport.build()
    spec = OperationSpec(
        name="items.create",
        method="POST",
        path="/items/{item_id}",
        query_model=ItemQuery,
        request_model=ItemRequest,
        response_model=ItemResponse,
        retry_mode="enabled",
    )

    result = OperationExecutor(transport).execute(
        spec,
        path_params={"item_id": "a/b"},
        query=ItemQuery(page=2, item_id="a/b"),
        request=ItemRequest(title="new"),
        headers={"X-Test": "yes"},
        idempotency_key="key-1",
    )

    assert result == ItemResponse(item_id="a/b", title="new")
    request = fake_transport.last(method="POST", path="/items/a/b")
    assert request.params == {"page": "2", "itemId": "a/b"}
    assert request.json_body == {"title": "new"}
    assert request.headers["x-test"] == "yes"
    assert request.headers["idempotency-key"] == "key-1"


def test_operation_executor_empty_response_does_not_read_json() -> None:
    fake_transport = FakeTransport()
    fake_transport.add("DELETE", "/items/1", FakeTransportResponse.empty())
    transport = fake_transport.build()
    spec = OperationSpec(
        name="items.delete",
        method="DELETE",
        path="/items/{item_id}",
        response_kind="empty",
    )

    result = OperationExecutor(transport).execute(spec, path_params={"item_id": 1})

    assert result == EmptyResponse(status_code=204, headers={})


def test_operation_executor_binary_response_uses_transport_request() -> None:
    fake_transport = FakeTransport()
    fake_transport.add(
        "GET",
        "/items/1/file",
        FakeTransportResponse.binary(b"file", content_type="application/pdf"),
    )
    transport = fake_transport.build()
    spec = OperationSpec(
        name="items.file",
        method="GET",
        path="/items/{item_id}/file",
        response_kind="binary",
    )

    result = OperationExecutor(transport).execute(spec, path_params={"item_id": 1})

    assert isinstance(result, BinaryResponse)
    assert result.content == b"file"
    assert result.content_type == "application/pdf"


class FakeTransportResponse:
    @staticmethod
    def empty() -> object:
        import httpx

        return httpx.Response(204)

    @staticmethod
    def binary(content: bytes, *, content_type: str) -> object:
        import httpx

        return httpx.Response(200, content=content, headers={"content-type": content_type})
