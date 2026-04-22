"""Внутренние helper-ы для преобразования transport payload в публичные SDK-модели."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from avito.core.transport import Transport
from avito.core.types import HttpMethod, RequestContext


def request_public_model[ModelT](
    transport: Transport,
    method: HttpMethod,
    path: str,
    *,
    context: RequestContext,
    mapper: Callable[[object], ModelT],
    params: Mapping[str, object] | None = None,
    json_body: Mapping[str, object] | None = None,
    idempotency_key: str | None = None,
) -> ModelT:
    """Выполняет HTTP-запрос и маппит JSON в публичную модель SDK."""

    return transport.request_public_model(
        method,
        path,
        context=context,
        mapper=mapper,
        params=params,
        json_body=json_body,
        idempotency_key=idempotency_key,
    )


__all__ = ("request_public_model",)
