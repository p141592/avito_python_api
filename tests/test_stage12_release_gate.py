from __future__ import annotations

import httpx

from avito import AvitoClient
from avito.auth import AuthProvider, LegacyTokenClient, TokenClient
from avito.auth.settings import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport


def test_debug_info_does_not_expose_secrets() -> None:
    settings = AvitoSettings(
        auth=AuthSettings(client_id="client-id", client_secret="super-secret"),
    )

    client = AvitoClient(settings)
    info = client.debug_info()

    assert info.base_url == "https://api.avito.ru"
    assert info.user_id is None
    assert info.requires_auth is True
    assert info.retry_max_attempts == settings.retry_policy.max_attempts
    assert "secret" not in repr(info).lower()
    client.close()


def test_client_context_manager_closes_transport_and_auth_clients() -> None:
    transport_http_client = httpx.Client()
    token_http_client = httpx.Client()
    legacy_http_client = httpx.Client()
    autoteka_http_client = httpx.Client()

    settings = AvitoSettings(
        auth=AuthSettings(client_id="client-id", client_secret="client-secret"),
    )
    auth_provider = AuthProvider(
        settings.auth,
        token_client=TokenClient(settings.auth, client=token_http_client),
        legacy_token_client=LegacyTokenClient(settings.auth, client=legacy_http_client),
        autoteka_token_client=TokenClient(settings.auth, client=autoteka_http_client),
    )
    client = AvitoClient(settings)
    client.transport = Transport(
        settings, auth_provider=auth_provider, client=transport_http_client
    )
    client.auth_provider = auth_provider

    with client as managed_client:
        assert managed_client.debug_info().requires_auth is True

    assert transport_http_client.is_closed is True
    assert token_http_client.is_closed is True
    assert legacy_http_client.is_closed is True
    assert autoteka_http_client.is_closed is True
