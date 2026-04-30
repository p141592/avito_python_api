# Transport и retry

`Transport` — единственный слой, который работает с `httpx`, таймаутами, retry
и mapping HTTP-ошибок. Домены и `OperationExecutor` не повторяют эту логику,
иначе публичное поведение разных разделов начало бы расходиться.

```mermaid
flowchart TD
    call[OperationExecutor request] --> auth{Нужен токен?}
    auth -- да --> token[AuthProvider]
    auth -- нет --> send[httpx request]
    token --> send
    send --> status{Ответ}
    status -- 2xx --> map[JSON, empty или binary response]
    status -- 401 --> refresh[Инвалидация токена]
    refresh --> retry401{Можно повторить?}
    retry401 -- да --> token
    retry401 -- нет --> error[Typed exception]
    status -- 429/5xx --> retry{Retry допустим?}
    retry -- да --> wait[Backoff / Retry-After]
    wait --> send
    retry -- нет --> error
    status -- 4xx --> error
```

## Что повторяется

Retry применяется только там, где операция помечена как безопасная для повтора.
Read/list/probe операции обычно допускают retry. Write-операции получают retry
только при явной идемпотентности, например через `idempotency_key`, или когда
конкретный `OperationSpec` помечает операцию как безопасную.

`429` учитывает `Retry-After`, если upstream его вернул. Если `Retry-After` отсутствует, transport использует обычный exponential backoff с jitter. Для `5xx` используется retry-политика transport-слоя. Ошибки маппинга не повторяются: если JSON уже получен, но не соответствует контракту модели, это `ResponseMappingError`, а не сетевой сбой.

Чтобы снижать вероятность `429` до ответа upstream, можно включить локальный token bucket через `AVITO_RATE_LIMIT_ENABLED=true`. Лимитер применяется в transport-слое перед отправкой запроса и дополнительно учитывает `X-RateLimit-Remaining: 0`, когда API возвращает этот заголовок.

## Почему retry не в доменах

Доменный объект должен описывать публичный сценарий: `order_label().create()` или `ad_stats().get_item_stats()`. Если retry появится на этом уровне, одинаковые HTTP-коды начнут вести себя по-разному в разных пакетах. Поэтому retry централизован и проверяется через transport/fake transport.

Подробные исключения смотрите в [модели ошибок](error-model.md) и [reference по исключениям](../reference/exceptions.md).
