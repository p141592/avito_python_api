"""Пакет общей инфраструктуры SDK."""

from avito.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    AvitoError,
    ClientError,
    ConfigurationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
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
    "JsonPage",
    "NotFoundError",
    "PaginatedList",
    "Paginator",
    "PermissionDeniedError",
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
