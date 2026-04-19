from __future__ import annotations

import inspect

from avito import AvitoClient
from avito.promotion.models import (
    CampaignListFilter,
    CampaignOrderBy,
    CampaignUpdateTimeFilter,
    CreateAutostrategyBudgetRequest,
    ListAutostrategyCampaignsRequest,
)
from avito.ratings import Review


def test_readme_uses_current_autostrategy_request_models() -> None:
    budget_request = CreateAutostrategyBudgetRequest(
        campaign_type="AS",
        start_time="2026-04-20T00:00:00Z",
        finish_time="2026-04-27T00:00:00Z",
        items=[42, 43],
    )
    campaigns_request = ListAutostrategyCampaignsRequest(
        limit=50,
        status_id=[1, 2],
        order_by=[CampaignOrderBy(column="startTime", direction="asc")],
        filter=CampaignListFilter(
            by_update_time=CampaignUpdateTimeFilter(
                from_time="2026-04-01T00:00:00Z",
                to_time="2026-04-30T00:00:00Z",
            )
        ),
    )

    assert budget_request.to_payload() == {
        "campaignType": "AS",
        "startTime": "2026-04-20T00:00:00Z",
        "finishTime": "2026-04-27T00:00:00Z",
        "items": [42, 43],
    }
    assert campaigns_request.to_payload() == {
        "limit": 50,
        "statusId": [1, 2],
        "orderBy": [{"column": "startTime", "direction": "asc"}],
        "filter": {
            "byUpdateTime": {
                "from": "2026-04-01T00:00:00Z",
                "to": "2026-04-30T00:00:00Z",
            }
        },
    }


def test_readme_references_current_public_method_names() -> None:
    assert hasattr(AvitoClient, "autoload_archive")
    assert hasattr(AvitoClient, "cpa_archive")
    assert hasattr(Review, "list")
    assert not hasattr(AvitoClient, "autoload_legacy")
    assert not hasattr(AvitoClient, "cpa_legacy")
    assert not hasattr(Review, "list_reviews_v1")

    review_signature = str(inspect.signature(Review.list))
    assert "query" in review_signature
