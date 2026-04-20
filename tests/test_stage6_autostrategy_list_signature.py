from __future__ import annotations

import json
from datetime import datetime

import httpx

from avito.auth import AuthSettings
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts
from avito.promotion import AutostrategyCampaign


def make_transport(handler: httpx.MockTransport) -> Transport:
    settings = AvitoSettings(
        base_url="https://api.avito.ru",
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


def test_autostrategy_list_accepts_keyword_fields_without_public_dto() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/autostrategy/v1/campaigns"
        assert json.loads(request.content.decode()) == {
            "limit": 20,
            "offset": 10,
            "statusId": [1, 2],
            "orderBy": [{"column": "startTime", "direction": "asc"}],
            "filter": {
                "byUpdateTime": {
                    "from": "2026-04-01T00:00:00",
                    "to": "2026-04-30T00:00:00",
                }
            },
        }
        return httpx.Response(
            200,
            json={
                "campaigns": [
                    {
                        "campaignId": 77,
                        "campaignType": "AS",
                        "title": "Весенняя кампания",
                        "statusId": 1,
                        "version": 3,
                    }
                ],
                "totalCount": 1,
            },
        )

    transport = make_transport(httpx.MockTransport(handler))
    campaigns = AutostrategyCampaign(transport).list(
        limit=20,
        offset=10,
        status_id=[1, 2],
        order_by=[("startTime", "asc")],
        updated_from=datetime(2026, 4, 1, 0, 0, 0),
        updated_to=datetime(2026, 4, 30, 0, 0, 0),
    )

    assert campaigns.total_count == 1
    assert campaigns.items[0].campaign_id == 77
