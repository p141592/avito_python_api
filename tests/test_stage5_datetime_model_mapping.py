from __future__ import annotations

import json
from datetime import UTC, datetime

from avito.accounts.mappers import map_operations_history
from avito.ads.mappers import map_autoload_report_details, map_autoload_reports
from avito.messenger.mappers import map_message
from avito.promotion.mappers import map_cpa_auction_bids


def test_datetime_fields_are_parsed_into_models_and_serialized_as_iso_strings() -> None:
    operations = map_operations_history(
        {
            "operations": [
                {
                    "id": "op-1",
                    "created_at": "2025-01-02T12:00:00Z",
                    "amount": 120.0,
                    "type": "payment",
                    "status": "done",
                }
            ],
            "total": 1,
        }
    )
    message = map_message(
        {
            "id": "msg-1",
            "chat_id": "chat-1",
            "author_id": 7,
            "text": "hello",
            "created_at": "2025-01-03T08:15:00+03:00",
        }
    )
    reports = map_autoload_reports(
        {
            "reports": [
                {
                    "report_id": 501,
                    "status": "done",
                    "created_at": "2025-01-04T09:00:00+03:00",
                    "finished_at": "2025-01-04T09:10:00+03:00",
                }
            ]
        }
    )
    details = map_autoload_report_details(
        {
            "report_id": 501,
            "status": "done",
            "created_at": "2025-01-04T09:00:00+03:00",
            "finished_at": "2025-01-04T09:10:00+03:00",
            "errors_count": 0,
            "warnings_count": 1,
        }
    )
    bids = map_cpa_auction_bids(
        {
            "items": [
                {
                    "itemId": 101,
                    "pricePenny": 1500,
                    "expirationTime": "2025-01-05T18:30:00Z",
                    "availablePrices": [{"pricePenny": 1600, "goodness": 9}],
                }
            ]
        }
    )

    assert operations.operations[0].created_at == datetime(2025, 1, 2, 12, 0, tzinfo=UTC)
    assert message.created_at == datetime.fromisoformat("2025-01-03T08:15:00+03:00")
    assert reports.items[0].created_at == datetime.fromisoformat("2025-01-04T09:00:00+03:00")
    assert reports.items[0].finished_at == datetime.fromisoformat("2025-01-04T09:10:00+03:00")
    assert details.created_at == datetime.fromisoformat("2025-01-04T09:00:00+03:00")
    assert details.finished_at == datetime.fromisoformat("2025-01-04T09:10:00+03:00")
    assert bids.items[0].expiration_time == datetime(2025, 1, 5, 18, 30, tzinfo=UTC)

    assert operations.to_dict()["operations"][0]["created_at"] == "2025-01-02T12:00:00+00:00"
    assert message.to_dict()["created_at"] == "2025-01-03T08:15:00+03:00"
    assert reports.to_dict()["items"][0]["created_at"] == "2025-01-04T09:00:00+03:00"
    assert reports.to_dict()["items"][0]["finished_at"] == "2025-01-04T09:10:00+03:00"
    assert details.to_dict()["created_at"] == "2025-01-04T09:00:00+03:00"
    assert details.to_dict()["finished_at"] == "2025-01-04T09:10:00+03:00"
    assert bids.to_dict()["items"][0]["expiration_time"] == "2025-01-05T18:30:00+00:00"

    json.dumps(operations.to_dict())
    json.dumps(message.to_dict())
    json.dumps(reports.to_dict())
    json.dumps(details.to_dict())
    json.dumps(bids.to_dict())
