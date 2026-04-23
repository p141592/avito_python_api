from __future__ import annotations

from collections.abc import Iterator

import pytest

from avito import AvitoClient
from avito.testing import FakeTransport


def build_docs_client() -> AvitoClient:
    fake = FakeTransport()
    fake.add_json(
        "GET",
        "/core/v1/accounts/self",
        {"id": 7, "name": "Иван", "email": "user@example.com", "phone": "+7999"},
    )
    return fake.as_client(user_id=7)


@pytest.fixture(autouse=True)
def docs_client_from_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("AVITO_CLIENT_ID", "docs-client-id")
    monkeypatch.setenv("AVITO_CLIENT_SECRET", "docs-client-secret")

    def from_env(
        cls: type[AvitoClient],
        *,
        env_file: str | None = ".env",
    ) -> AvitoClient:
        _ = cls
        _ = env_file
        return build_docs_client()

    monkeypatch.setattr(AvitoClient, "from_env", classmethod(from_env))
    yield
