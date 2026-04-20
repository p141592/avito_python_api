from __future__ import annotations

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts


def make_transport(handler: httpx.MockTransport, *, user_id: int | None = None) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
        user_id=user_id,
        auth=AuthSettings(),
        retry_policy=RetryPolicy(),
        timeouts=ApiTimeouts(),
    )
    return Transport(
        settings,
        auth_provider=None,
        client=httpx.Client(transport=handler, base_url="https://api.avito.ru"),
        sleep=lambda _: None,
    )
