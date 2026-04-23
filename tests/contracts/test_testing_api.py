from __future__ import annotations

from avito import AvitoClient
from avito.testing import FakeTransport


def test_fake_transport_builds_public_client_without_real_http() -> None:
    fake = FakeTransport()
    fake.add_json(
        "GET",
        "/core/v1/accounts/self",
        {"id": 7, "name": "Иван", "email": "user@example.com", "phone": "+7999"},
    )

    with fake.as_client(user_id=7) as avito:
        profile = avito.account().get_self()
        info = avito.debug_info()

    assert isinstance(avito, AvitoClient)
    assert profile.user_id == 7
    assert profile.name == "Иван"
    assert info.user_id == 7
    assert info.requires_auth is False
    assert fake.count(method="GET", path="/core/v1/accounts/self") == 1
