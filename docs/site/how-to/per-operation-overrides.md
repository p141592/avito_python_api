# Per-operation overrides

SDK даёт два вида переопределения поведения: глобальные настройки `AvitoSettings` (таймауты, retry-политика) и параметры конкретных методов (`idempotency_key`, `limit` для пагинации). Глобальные настройки задаются один раз при создании клиента.

## Таймауты

`ApiTimeouts` управляет таймаутами connect, read, write и pool. Настраивается в `AvitoSettings` или через env-переменные.

```python
from avito import AvitoSettings
from avito.core.types import ApiTimeouts

settings = AvitoSettings(
    timeouts=ApiTimeouts(
        connect=3.0,
        read=30.0,
        write=20.0,
        pool=5.0,
    )
)

print(settings.timeouts.read)
```

Env-переменные: `AVITO_TIMEOUT_CONNECT`, `AVITO_TIMEOUT_READ`, `AVITO_TIMEOUT_WRITE`, `AVITO_TIMEOUT_POOL`.

## Retry-политика

`RetryPolicy` задаёт число попыток, backoff-фактор, максимальную задержку и список retryable HTTP-методов.

```python
from avito import AvitoSettings
from avito.core.retries import RetryPolicy

settings = AvitoSettings(
    retry_policy=RetryPolicy(
        max_attempts=5,
        backoff_factor=1.0,
        max_delay=60.0,
        retry_on_rate_limit=True,
    )
)

print(settings.retry_policy.max_attempts)
```

Env-переменные: `AVITO_RETRY_MAX_ATTEMPTS`, `AVITO_RETRY_BACKOFF_FACTOR`, `AVITO_RETRY_MAX_DELAY`.

## Idempotency key для write-операций

Write-операции с `dry_run=False` принимают `idempotency_key` для безопасного повтора при сетевых ошибках. Один и тот же ключ гарантирует, что повторный вызов не создаст дублирующую операцию на стороне API.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    result = avito.ad(item_id=101, user_id=7).update_price(
        price=10900,
        idempotency_key="price-update-101-2026-04-24",
    )

print(result.item_id)
print(result.price)
```

Ключ должен быть уникальным для каждой логической операции. При повторе используйте тот же ключ.

## Размер страницы для пагинации

List-методы принимают `limit` для управления числом элементов на странице. Меньший `limit` снижает latency первого запроса, больший — уменьшает число запросов при `materialize()`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(limit=5)
    items = listings.materialize()

print(len(items))
```

## Канонический набор overrides

| Тип операции | Разрешённые overrides |
|---|---|
| read / list / probe | `AvitoSettings.timeouts`, `AvitoSettings.retry_policy` |
| write при `dry_run=False` | `AvitoSettings.timeouts`, `AvitoSettings.retry_policy`, `idempotency_key` |
| write при `dry_run=True` | `AvitoSettings.timeouts` |
| pagination-чтение | `AvitoSettings.timeouts`, `AvitoSettings.retry_policy`, `limit` |

Полный контракт настроек описан в [reference по конфигурации](../reference/config.md). Правила идемпотентности разобраны в [рецепте по идемпотентности](idempotency.md).
