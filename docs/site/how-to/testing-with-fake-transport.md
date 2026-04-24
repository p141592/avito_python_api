# Тестирование с FakeTransport

`avito.testing` предоставляет `FakeTransport` — детерминированный fake transport для тестов. Он не выполняет реальных HTTP-запросов и позволяет проверять поведение consumer-кода через публичный SDK API.

## Создание клиента поверх FakeTransport

`FakeTransport.as_client()` создаёт полностью инициализированный `AvitoClient` без реального HTTP. Используйте его в тестах вместо `AvitoClient.from_env()`.

```python
from avito.testing import FakeTransport

fake = FakeTransport()
fake.add_json(
    "GET",
    "/core/v1/accounts/self",
    {"id": 7, "name": "Тест", "email": "test@example.com", "phone": "+7999"},
)

with fake.as_client(user_id=7) as avito:
    profile = avito.account().get_self()

print(profile.user_id)
print(profile.name)
```

## Скриптование последовательности ответов

`route_sequence` задаёт несколько ответов для одного маршрута. Ответы расходуются по одному. Последний ответ в очереди переиспользуется.

```python
from avito.testing import FakeTransport, json_response, route_sequence

fake = FakeTransport()
fake.add(
    "GET",
    "/core/v1/accounts/self",
    *route_sequence(
        json_response({"id": 7, "name": "Тест", "email": "a@b.com", "phone": "+7"}),
        json_response({"id": 7, "name": "Обновлён", "email": "a@b.com", "phone": "+7"}),
    ),
)

with fake.as_client(user_id=7) as avito:
    first = avito.account().get_self()
    second = avito.account().get_self()

print(first.name)
print(second.name)
```

## Инспекция вызовов

`fake.requests` содержит список `RecordedRequest` со всеми выполненными HTTP-запросами. Используйте его для проверки payload, метода и пути.

```python
from avito.testing import FakeTransport

fake = FakeTransport()
fake.add_json(
    "GET",
    "/core/v1/accounts/self",
    {"id": 7, "name": "Тест", "email": "t@e.com", "phone": "+7"},
)

with fake.as_client(user_id=7) as avito:
    avito.account().get_self()

assert len(fake.requests) == 1
req = fake.requests[0]
print(req.method)
print(req.path)
```

## Симуляция ошибок transport

`FakeResponse` позволяет вернуть любой HTTP-статус для проверки обработки ошибок.

```python
from avito.core.exceptions import AuthenticationError
from avito.testing import FakeResponse, FakeTransport

fake = FakeTransport()
fake.add(
    "GET",
    "/core/v1/accounts/self",
    FakeResponse(401, json={"error": "unauthorized", "error_description": "token expired"}),
)

with fake.as_client(user_id=7) as avito:
    try:
        avito.account().get_self()
    except AuthenticationError as exc:
        print(exc.status_code)
        print(exc.operation)
```

## Симуляция rate limit с Retry-After

Для проверки retry-поведения задайте ответ 429 с заголовком `Retry-After`. SDK учитывает заголовок при расчёте задержки повтора.

```python
from avito.core.exceptions import RateLimitError
from avito.core.retries import RetryPolicy
from avito.testing import FakeResponse, FakeTransport, json_response, route_sequence

fake = FakeTransport()
fake.add(
    "GET",
    "/core/v1/accounts/self",
    *route_sequence(
        FakeResponse(429, json={"error": "too_many_requests"}, headers={"Retry-After": "1"}),
        json_response({"id": 7, "name": "Тест", "email": "t@e.com", "phone": "+7"}),
    ),
)

policy = RetryPolicy(max_attempts=2, max_rate_limit_wait_seconds=2.0)
with fake.as_client(user_id=7, retry_policy=policy) as avito:
    profile = avito.account().get_self()

print(profile.user_id)
print(len(fake.requests))
```

Полный публичный контракт `avito.testing` описан в [reference по тестированию](../reference/testing.md). Стратегия тестирования SDK разобрана в [explanations](../explanations/testing-strategy.md).
