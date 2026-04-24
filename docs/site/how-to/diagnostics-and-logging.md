# Диагностика и логирование

SDK предоставляет безопасный диагностический снимок через `debug_info()` и типизированные исключения с полной информацией об операции. Это упрощает отладку без риска утечки секретов в логи.

## Диагностический снимок

`debug_info()` возвращает `TransportDebugInfo` — снимок transport-настроек без OAuth-секретов. Его безопасно печатать в логи и передавать в отчёты об ошибках.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    info = avito.debug_info()

print(info.base_url)
print(info.retry_max_attempts)
print(info.timeout_read)
print(info.requires_auth)
```

## Поля исключений

Каждое исключение SDK содержит поля для диагностики:

- `operation` — имя SDK-операции (например, `ads.get_item`);
- `status_code` — HTTP-статус ответа;
- `error_code` — код ошибки из тела ответа API;
- `message` — читаемое описание ошибки;
- `metadata` — дополнительные поля с редактированными секретами.

```text
from avito import AvitoClient
from avito.core.exceptions import AvitoError

with AvitoClient.from_env() as avito:
    try:
        item = avito.ad(item_id=999, user_id=7).get()
    except AvitoError as exc:
        print(exc.operation)
        print(exc.status_code)
        print(exc.error_code)
        print(str(exc))
```

## Обработка специфичных ошибок

SDK предоставляет иерархию исключений. Ловите конкретные типы для разной обработки:

```text
from avito.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    NotFoundError,
    AvitoError,
)

try:
    result = avito.account().get_self()
except AuthenticationError:
    # 401 — протух токен, нужно обновить credentials
    ...
except RateLimitError as exc:
    # 429 — слишком частые запросы
    print(exc.status_code)
except AuthorizationError:
    # 403 — нет доступа к ресурсу
    ...
except AvitoError as exc:
    # любая другая ошибка SDK
    print(str(exc))
```

## Безопасное логирование

`debug_info()` — единственный публичный способ получить диагностику без секретов. Не логируйте `to_dict()` / `model_dump()` моделей, которые могут содержать чувствительные данные пользователя.

```python
from avito import AvitoClient

import logging
logger = logging.getLogger(__name__)

with AvitoClient.from_env() as avito:
    info = avito.debug_info()
    logger.info("SDK инициализирован: base_url=%s, retry=%s", info.base_url, info.retry_max_attempts)
```

## После close()

После `close()` или выхода из контекстного менеджера любой SDK-вызов поднимает `ConfigurationError`. Проверяйте это в долгоживущих сервисах.

```python
from avito import AvitoClient
from avito.core.exceptions import ConfigurationError

avito = AvitoClient.from_env()
avito.close()

try:
    avito.account().get_self()
except ConfigurationError as exc:
    print(str(exc))
```

Полный контракт исключений описан в [reference по исключениям](../reference/exceptions.md). Security-модель SDK разобрана в [explanations](../explanations/security-and-redaction.md).
