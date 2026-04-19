from __future__ import annotations

import inspect

from avito import AvitoClient
from avito.autoteka import AutotekaMonitoring, AutotekaReport, AutotekaVehicle
from avito.autoteka.models import CatalogResolveRequest, MonitoringBucketRequest
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
    from avito.ads.domain import AdPromotion

    assert hasattr(AdPromotion, "apply_vas_direct")
    assert not hasattr(AdPromotion, "apply_vas_v2")

    assert hasattr(AvitoClient, "autoload_archive")
    assert hasattr(AvitoClient, "cpa_archive")
    assert hasattr(Review, "list")
    assert hasattr(AutotekaVehicle, "resolve_catalog")
    assert hasattr(AutotekaReport, "list_reports")
    assert hasattr(AutotekaMonitoring, "delete_bucket")
    assert hasattr(AutotekaMonitoring, "remove_bucket")
    assert not hasattr(AvitoClient, "autoload_legacy")
    assert not hasattr(AvitoClient, "cpa_legacy")
    assert not hasattr(Review, "list_reviews_v1")
    assert not hasattr(AutotekaVehicle, "get_catalogs_resolve")
    assert not hasattr(AutotekaReport, "list_report_list")
    assert not hasattr(AutotekaMonitoring, "list_monitoring_bucket_delete")
    assert not hasattr(AutotekaMonitoring, "delete_monitoring_bucket_remove")

    review_signature = str(inspect.signature(Review.list))
    assert "query" in review_signature


def test_auth_settings_env_var_names_match_readme() -> None:
    from avito.auth.settings import AuthSettings

    supported = AuthSettings.supported_env_vars()
    alternate_aliases = supported.get("alternate_token_url", ())

    assert "AVITO_AUTH__ALTERNATE_TOKEN_URL" in alternate_aliases
    assert "AVITO_ALTERNATE_TOKEN_URL" in alternate_aliases
    assert "ALTERNATE_TOKEN_URL" in alternate_aliases

    all_aliases = {alias for aliases in supported.values() for alias in aliases}
    assert not any("LEGACY" in a for a in all_aliases)


def test_readme_uses_current_autoteka_request_models() -> None:
    assert CatalogResolveRequest(brand_id=1).to_payload() == {"brandId": 1}
    assert MonitoringBucketRequest(vehicles=["VIN-1"]).to_payload() == {"vehicles": ["VIN-1"]}
