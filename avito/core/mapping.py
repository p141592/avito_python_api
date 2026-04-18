"""Внутренние helper-ы для преобразования transport payload в публичные SDK-модели."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeVar

from avito.core.transport import Transport
from avito.core.types import HttpMethod, RequestContext

ModelT = TypeVar("ModelT")


def request_public_model[ModelT](
    transport: Transport,
    method: HttpMethod,
    path: str,
    *,
    context: RequestContext,
    mapper: Callable[[object], ModelT],
    params: Mapping[str, object] | None = None,
    json_body: Mapping[str, object] | None = None,
) -> ModelT:
    """Выполняет HTTP-запрос и маппит JSON в публичную модель SDK."""

    payload = transport.request_json(
        method,
        path,
        context=context,
        params=params,
        json_body=json_body,
    )
    return mapper(payload)


__all__ = ("request_public_model",)
