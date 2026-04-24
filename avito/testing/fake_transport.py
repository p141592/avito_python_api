"""Публичный тестовый transport и вспомогательные утилиты для SDK-контрактных тестов."""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import cast

import httpx

from avito.auth import AuthProvider, AuthSettings
from avito.client import AvitoClient
from avito.config import AvitoSettings
from avito.core import Transport
from avito.core.retries import RetryPolicy
from avito.core.types import ApiTimeouts

JsonValue = dict[str, object] | list[object] | str | int | float | bool | None
FakeResponse = httpx.Response


@dataclass(slots=True, frozen=True)
class RecordedRequest:
    """Зафиксированный HTTP-запрос, перехваченный FakeTransport."""

    method: str
    path: str
    params: dict[str, str]
    headers: dict[str, str]
    json_body: JsonValue
    content: bytes


RouteResponder = Callable[[RecordedRequest], httpx.Response] | httpx.Response


class FakeTransport:
    """Deterministic fake transport for SDK contract tests."""

    def __init__(self, *, base_url: str = "https://api.avito.ru") -> None:
        self.base_url = base_url.rstrip("/")
        self.requests: list[RecordedRequest] = []
        self._routes: dict[tuple[str, str], deque[RouteResponder]] = {}

    def add(
        self,
        method: str,
        path: str,
        *responses: RouteResponder,
    ) -> FakeTransport:
        """Регистрирует один или несколько ответов для HTTP-маршрута."""

        key = (method.upper(), path)
        bucket = self._routes.setdefault(key, deque())
        bucket.extend(responses)
        return self

    def add_json(
        self,
        method: str,
        path: str,
        payload: JsonValue,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> FakeTransport:
        """Регистрирует JSON-ответ для HTTP-маршрута."""

        return self.add(
            method,
            path,
            httpx.Response(
                status_code,
                json=payload,
                headers=dict(headers or {}),
            ),
        )

    def build(
        self,
        *,
        retry_policy: RetryPolicy | None = None,
        user_id: int | None = None,
    ) -> Transport:
        """Создаёт низкоуровневый Transport поверх fake transport (internal helper)."""

        settings = AvitoSettings(
            base_url=self.base_url,
            user_id=user_id,
            auth=AuthSettings(),
            retry_policy=retry_policy or RetryPolicy(),
            timeouts=ApiTimeouts(),
        )
        return Transport(
            settings,
            auth_provider=None,
            client=httpx.Client(
                transport=httpx.MockTransport(self._handle), base_url=self.base_url
            ),
            sleep=lambda _: None,
        )

    def as_client(
        self,
        *,
        user_id: int | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> AvitoClient:
        """Создает публичный `AvitoClient` поверх fake transport без реального HTTP."""

        auth_settings = AuthSettings(client_id="fake-client-id", client_secret="fake-client-secret")
        settings = AvitoSettings(
            base_url=self.base_url,
            user_id=user_id,
            auth=auth_settings,
            retry_policy=retry_policy or RetryPolicy(),
            timeouts=ApiTimeouts(),
        )
        auth_provider = AuthProvider(auth_settings)
        transport = Transport(
            settings,
            auth_provider=None,
            client=httpx.Client(
                transport=httpx.MockTransport(self._handle), base_url=self.base_url
            ),
            sleep=lambda _: None,
        )
        return AvitoClient._from_transport(
            settings,
            transport=transport,
            auth_provider=auth_provider,
        )

    def count(self, *, method: str | None = None, path: str | None = None) -> int:
        """Возвращает число перехваченных запросов с опциональной фильтрацией."""

        return len(
            [
                request
                for request in self.requests
                if (method is None or request.method == method.upper())
                and (path is None or request.path == path)
            ]
        )

    def last(self, *, method: str | None = None, path: str | None = None) -> RecordedRequest:
        """Возвращает последний перехваченный запрос с опциональной фильтрацией."""

        matches = [
            request
            for request in self.requests
            if (method is None or request.method == method.upper())
            and (path is None or request.path == path)
        ]
        if not matches:
            raise AssertionError(f"No requests matched method={method!r} path={path!r}")
        return matches[-1]

    def _handle(self, request: httpx.Request) -> httpx.Response:
        recorded = RecordedRequest(
            method=request.method.upper(),
            path=request.url.path,
            params=dict(request.url.params),
            headers=dict(request.headers),
            json_body=self._decode_json(request),
            content=request.content,
        )
        self.requests.append(recorded)

        key = (recorded.method, recorded.path)
        if key not in self._routes:
            available = ", ".join(f"{method} {path}" for method, path in sorted(self._routes))
            raise AssertionError(
                "Маршрут не прописан в FakeTransport: "
                f"{recorded.method} {recorded.path}. "
                f"Добавьте route_sequence или add_json для этого пути. Доступные: {available}"
            )

        responders = self._routes[key]
        responder = responders[0] if len(responders) == 1 else responders.popleft()
        response = responder(recorded) if callable(responder) else responder
        response.request = request
        return response

    @staticmethod
    def _decode_json(request: httpx.Request) -> JsonValue:
        if not request.content:
            return None
        try:
            # `json.loads()` возвращает `Any` только на границе JSON-декодирования.
            return cast(JsonValue, json.loads(request.content.decode()))
        except json.JSONDecodeError:
            return None


def json_response(
    payload: JsonValue,
    *,
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    """Создаёт httpx.Response с JSON-телом для использования в FakeTransport."""

    return httpx.Response(status_code, json=payload, headers=dict(headers or {}))


def route_sequence(*responses: RouteResponder) -> Iterable[RouteResponder]:
    """Упаковывает несколько ответов в последовательность для FakeTransport.add()."""

    return responses


__all__ = (
    "FakeResponse",
    "FakeTransport",
    "JsonValue",
    "RecordedRequest",
    "json_response",
    "route_sequence",
)
