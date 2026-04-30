from __future__ import annotations

import subprocess

import download_avito_api_specs as downloader
import pytest


def test_run_curl_uses_timeout_options(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command == [
            "curl",
            "-fsSL",
            "--connect-timeout",
            "30",
            "--max-time",
            "180",
            "https://developers.avito.ru/web/1/openapi/info/delivery-sandbox",
        ]
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout='{"ok": true}',
            stderr="",
        )

    monkeypatch.setattr(downloader.subprocess, "run", fake_run)

    body = downloader.run_curl(
        "https://developers.avito.ru/web/1/openapi/info/delivery-sandbox",
        "https://developers.avito.ru/api-catalog/delivery-sandbox/documentation",
    )

    assert body == '{"ok": true}'


def test_run_curl_reports_public_catalog_url_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=command,
            returncode=28,
            stdout="",
            stderr="curl: (28) SSL connection timeout",
        )

    monkeypatch.setattr(downloader.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError) as exc_info:
        downloader.run_curl(
            "https://developers.avito.ru/web/1/openapi/info/delivery-sandbox",
            "https://developers.avito.ru/api-catalog/delivery-sandbox/documentation",
        )

    assert str(exc_info.value) == (
        "Не удалось скачать https://developers.avito.ru/api-catalog/delivery-sandbox/documentation: "
        "curl: (28) SSL connection timeout"
    )


def test_fetch_catalog_builds_public_documentation_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = {
        "https://developers.avito.ru/api-catalog": (
            '<script src="/dstatic/build/open-api-dev-portal.hash.js"></script>'
        ),
        "https://developers.avito.ru/dstatic/build/open-api-dev-portal.hash.js": (
            'const base="/web/7/openapi";'
        ),
        "https://developers.avito.ru/web/7/openapi/list": (
            '[{"slug": "delivery-sandbox", "title": "Доставка"}]'
        ),
    }

    def fake_run_curl(url: str, source_url: str) -> str:
        assert source_url == "https://developers.avito.ru/api-catalog"
        return responses[url]

    monkeypatch.setattr(downloader, "run_curl", fake_run_curl)

    assert downloader.fetch_catalog() == [
        downloader.ApiCatalogItem(
            slug="delivery-sandbox",
            title="Доставка",
            documentation_url=(
                "https://developers.avito.ru/api-catalog/delivery-sandbox/documentation"
            ),
        )
    ]
