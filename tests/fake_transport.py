from __future__ import annotations

from warnings import warn

from avito.testing.fake_transport import (
    FakeResponse,
    FakeTransport,
    JsonValue,
    RecordedRequest,
    json_response,
    route_sequence,
)

warn(
    "Импорт из tests.fake_transport устарел; используйте avito.testing.fake_transport "
    "или avito.testing.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = (
    "FakeResponse",
    "FakeTransport",
    "JsonValue",
    "RecordedRequest",
    "json_response",
    "route_sequence",
)
