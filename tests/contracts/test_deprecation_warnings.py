from __future__ import annotations

import warnings
from collections.abc import Callable

import httpx
import pytest

from avito.ads import AutoloadArchive
from avito.core.deprecation import _WARNED_SYMBOLS
from avito.cpa import CpaArchive, CpaChat
from scripts.parse_inventory import InventoryRow, parse_inventory
from tests.helpers.transport import make_transport


def response_for(path: str) -> httpx.Response:
    if path == "/cpa/v1/call/101":
        return httpx.Response(200, content=b"ID3", headers={"content-type": "audio/mpeg"})
    if path == "/cpa/v1/chatsByTime":
        return httpx.Response(200, json={"chats": []})
    if path == "/cpa/v2/balanceInfo":
        return httpx.Response(200, json={"balance": -5000, "advance": 1000, "debt": 0})
    if path == "/cpa/v2/callById":
        return httpx.Response(200, json={"calls": {"id": 101}})
    if path == "/autoload/v1/profile":
        return httpx.Response(200, json={"userId": 7, "isEnabled": True, "uploadUrl": "https://example.test/upload"})
    if path == "/autoload/v2/reports/last_completed_report":
        return httpx.Response(200, json={"reportId": 11, "status": "completed"})
    if path == "/autoload/v2/reports/101":
        return httpx.Response(200, json={"reportId": 101, "status": "completed"})
    raise AssertionError(f"Неожиданный маршрут теста deprecated: {path}")


def make_deprecated_transport() -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/autoload/v1/profile" and request.method == "POST":
            return httpx.Response(200, json={"success": True})
        return response_for(request.url.path)

    return make_transport(httpx.MockTransport(handler))


def deprecated_cases() -> list[tuple[InventoryRow, Callable[[], object]]]:
    transport = make_deprecated_transport()
    cpa_archive = CpaArchive(transport, call_id=101)
    cpa_chat = CpaChat(transport)
    autoload_archive = AutoloadArchive(transport, report_id=101)
    calls: dict[tuple[str, str], Callable[[], object]] = {
        ("cpa", "CpaArchive.get_call"): lambda: cpa_archive.get_call(),
        ("cpa", "CpaChat.list"): lambda: cpa_chat.list(
            created_at_from="2026-04-18T00:00:00+03:00",
            version=1,
        ),
        ("cpa", "CpaArchive.get_balance_info"): lambda: cpa_archive.get_balance_info(),
        ("cpa", "CpaArchive.get_call_by_id"): lambda: cpa_archive.get_call_by_id(call_id=101),
        ("ads", "AutoloadArchive.get_profile"): lambda: autoload_archive.get_profile(),
        ("ads", "AutoloadArchive.save_profile"): lambda: autoload_archive.save_profile(is_enabled=True),
        ("ads", "AutoloadArchive.get_last_completed_report"): (
            lambda: autoload_archive.get_last_completed_report()
        ),
        ("ads", "AutoloadArchive.get_report"): lambda: autoload_archive.get_report(),
    }

    cases: list[tuple[InventoryRow, Callable[[], object]]] = []
    for row in parse_inventory():
        if not row.deprecated:
            continue
        key = (row.sdk_package, f"{row.domain_object}.{row.sdk_public_method}")
        if key not in calls:
            raise AssertionError(f"Нет deprecated-test case для {key}")
        cases.append((row, calls[key]))
    return cases


@pytest.mark.parametrize(("row", "call"), deprecated_cases())
def test_deprecated_inventory_symbols_warn_once(
    row: InventoryRow,
    call: Callable[[], object],
) -> None:
    _WARNED_SYMBOLS.clear()

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always", DeprecationWarning)
        call()
        call()

    deprecation_warnings = [
        warning for warning in recorded if issubclass(warning.category, DeprecationWarning)
    ]
    assert len(deprecation_warnings) == 1

    message = str(deprecation_warnings[0].message)
    assert row.replacement is not None
    assert row.removal_version is not None
    assert row.deprecated_since is not None
    assert row.replacement in message
    assert row.removal_version in message
    assert row.deprecated_since in message
