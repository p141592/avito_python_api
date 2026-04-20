from __future__ import annotations

from datetime import datetime

from avito.autoteka.models import CatalogResolveRequest, MonitoringBucketRequest
from avito.promotion.models import (
    CampaignListFilter,
    CampaignOrderBy,
    CampaignUpdateTimeFilter,
    CreateAutostrategyBudgetRequest,
    ListAutostrategyCampaignsRequest,
)


def test_autostrategy_request_models_produce_correct_payload() -> None:
    budget_request = CreateAutostrategyBudgetRequest(
        campaign_type="AS",
        start_time=datetime.fromisoformat("2026-04-20T00:00:00+00:00"),
        finish_time=datetime.fromisoformat("2026-04-27T00:00:00+00:00"),
        items=[42, 43],
    )
    campaigns_request = ListAutostrategyCampaignsRequest(
        limit=50,
        status_id=[1, 2],
        order_by=[CampaignOrderBy(column="startTime", direction="asc")],
        filter=CampaignListFilter(
            by_update_time=CampaignUpdateTimeFilter(
                from_time=datetime.fromisoformat("2026-04-01T00:00:00+00:00"),
                to_time=datetime.fromisoformat("2026-04-30T00:00:00+00:00"),
            )
        ),
    )

    assert budget_request.to_payload() == {
        "campaignType": "AS",
        "startTime": "2026-04-20T00:00:00+00:00",
        "finishTime": "2026-04-27T00:00:00+00:00",
        "items": [42, 43],
    }
    assert campaigns_request.to_payload() == {
        "limit": 50,
        "statusId": [1, 2],
        "orderBy": [{"column": "startTime", "direction": "asc"}],
        "filter": {
            "byUpdateTime": {
                "from": "2026-04-01T00:00:00+00:00",
                "to": "2026-04-30T00:00:00+00:00",
            }
        },
    }


def test_autoteka_request_models_produce_correct_payload() -> None:
    assert CatalogResolveRequest(brand_id=1).to_payload() == {"brandId": 1}
    assert MonitoringBucketRequest(vehicles=["VIN-1"]).to_payload() == {"vehicles": ["VIN-1"]}
