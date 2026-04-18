"""Пакет общей инфраструктуры SDK."""

from avito.core.exceptions import (
    AuthenticationError,
    AvitoError,
    ClientError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ResponseMappingError,
    ServerError,
    TransportError,
    ValidationError,
)
from avito.core.pagination import Paginator
from avito.core.retries import RetryDecision, RetryPolicy
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
    "AvitoError",
    "BinaryResponse",
    "ClientError",
    "JsonPage",
    "NotFoundError",
    "Paginator",
    "PermissionDeniedError",
    "RateLimitError",
    "RequestContext",
    "ResponseMappingError",
    "RetryDecision",
    "RetryPolicy",
    "ServerError",
    "Transport",
    "TransportDebugInfo",
    "TransportError",
    "ValidationError",
)
