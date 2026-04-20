from __future__ import annotations

import httpx

from avito.tariffs import Tariff
from tests.helpers.transport import make_transport


def test_tariff_flow() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tariff/info/1"
        return httpx.Response(
            200,
            json={
                "current": {
                    "level": "Тариф Максимальный",
                    "isActive": True,
                    "startTime": 1713427200,
                    "closeTime": 1716029200,
                    "bonus": 10,
                    "packages": [{"id": 1}, {"id": 2}],
                    "price": {"price": 1990, "originalPrice": 2490},
                },
                "scheduled": {
                    "level": "Тариф Базовый",
                    "isActive": False,
                    "startTime": 1716029300,
                    "closeTime": None,
                    "bonus": 0,
                    "packages": [],
                    "price": {"price": 990, "originalPrice": 990},
                },
            },
        )

    tariff = Tariff(make_transport(httpx.MockTransport(handler)))
    info = tariff.get_tariff_info()

    assert info.current is not None
    assert info.current.level == "Тариф Максимальный"
    assert info.current.packages_count == 2
