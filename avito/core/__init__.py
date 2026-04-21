"""Пакет общей инфраструктуры SDK."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from avito.core.domain import DomainObject
    from avito.core.exceptions import (
        AuthenticationError,
        AuthorizationError,
        AvitoError,
        ClientError,
        ConfigurationError,
        ConflictError,
        NotFoundError,
        RateLimitError,
        ResponseMappingError,
        ServerError,
        TransportError,
        UnsupportedOperationError,
        UpstreamApiError,
        ValidationError,
    )
    from avito.core.pagination import PaginatedList, Paginator
    from avito.core.retries import RetryDecision, RetryPolicy
    from avito.core.serialization import SerializableModel
    from avito.core.transport import Transport
    from avito.core.types import (
        ApiTimeouts,
        BinaryResponse,
        JsonPage,
        RequestContext,
        TransportDebugInfo,
    )

__all__ = (
    "ApiTimeouts",
    "AuthenticationError",
    "AuthorizationError",
    "AvitoError",
    "BinaryResponse",
    "ClientError",
    "ConfigurationError",
    "ConflictError",
    "DomainObject",
    "JsonPage",
    "NotFoundError",
    "PaginatedList",
    "Paginator",
    "RateLimitError",
    "RequestContext",
    "ResponseMappingError",
    "RetryDecision",
    "RetryPolicy",
    "SerializableModel",
    "ServerError",
    "Transport",
    "TransportDebugInfo",
    "TransportError",
    "UnsupportedOperationError",
    "UpstreamApiError",
    "ValidationError",
)

_EXPORT_MODULES = {
    "ApiTimeouts": "avito.core.types",
    "AuthenticationError": "avito.core.exceptions",
    "AuthorizationError": "avito.core.exceptions",
    "AvitoError": "avito.core.exceptions",
    "BinaryResponse": "avito.core.types",
    "ClientError": "avito.core.exceptions",
    "ConfigurationError": "avito.core.exceptions",
    "ConflictError": "avito.core.exceptions",
    "DomainObject": "avito.core.domain",
    "JsonPage": "avito.core.types",
    "NotFoundError": "avito.core.exceptions",
    "PaginatedList": "avito.core.pagination",
    "Paginator": "avito.core.pagination",
    "RateLimitError": "avito.core.exceptions",
    "RequestContext": "avito.core.types",
    "ResponseMappingError": "avito.core.exceptions",
    "RetryDecision": "avito.core.retries",
    "RetryPolicy": "avito.core.retries",
    "SerializableModel": "avito.core.serialization",
    "ServerError": "avito.core.exceptions",
    "Transport": "avito.core.transport",
    "TransportDebugInfo": "avito.core.types",
    "TransportError": "avito.core.exceptions",
    "UnsupportedOperationError": "avito.core.exceptions",
    "UpstreamApiError": "avito.core.exceptions",
    "ValidationError": "avito.core.exceptions",
}


def __getattr__(name: str) -> object:
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_name)
    return getattr(module, name)
