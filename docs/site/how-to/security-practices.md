# Безопасная работа с SDK

Этот рецепт фиксирует практики consumer-кода, которые сохраняют security-гарантии SDK: не допускают утечки секретов в логи, исключения и сериализованные данные.

## Хранение секретов в переменных окружения

Никогда не хардкодьте `client_id` и `client_secret` в исходном коде. Используйте `.env` или переменные окружения процесса:

```bash
AVITO_CLIENT_ID=your_client_id
AVITO_CLIENT_SECRET=your_client_secret
```

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    profile = avito.account().get_self()

print(profile.user_id)
```

SDK читает `AVITO_CLIENT_ID` и `AVITO_CLIENT_SECRET` автоматически. Файл `.env` добавьте в `.gitignore`.

## Что SDK редактирует автоматически

SDK гарантирует, что секреты не попадают в диагностику и исключения:

- `debug_info()` не возвращает `client_secret`, `access_token` или `refresh_token`;
- исключения `AvitoError` редактируют поля `authorization`, `token`, `client_secret` и аналогичные в `metadata` и `headers`;
- строковое представление исключения `str(exc)` содержит только операцию, статус и код ошибки.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    info = avito.debug_info()

print(info.base_url)
print(info.requires_auth)
```

## Осторожно с to_dict() и model_dump()

Публичные SDK-модели реализуют `to_dict()` / `model_dump()` для сериализации. Они могут содержать пользовательские данные (телефон, email, имя). Не передавайте результат напрямую в системы логирования без фильтрации.

```text
# Небезопасно — логируем всё подряд
profile = avito.account().get_self()
logger.info("Profile: %s", profile.to_dict())  # phone, email попадут в логи

# Безопасно — логируем только нужные поля
logger.info("User: id=%s, name=%s", profile.user_id, profile.name)
```

## user_agent_suffix без секретов

`user_agent_suffix` идентифицирует интеграцию в HTTP-заголовках. SDK запрещает включать в него секреты:

```text
# Правильно
settings = AvitoSettings(user_agent_suffix="my-crm/1.0")

# Ошибка — SDK поднимет ConfigurationError
settings = AvitoSettings(user_agent_suffix="token=abc123")
```

## Логирование через debug_info()

При логировании состояния клиента используйте только `debug_info()`:

```python
from avito import AvitoClient
import logging

logger = logging.getLogger(__name__)

with AvitoClient.from_env() as avito:
    info = avito.debug_info()
    logger.info(
        "Клиент Avito: base_url=%s, retry=%d, timeout_read=%.1f",
        info.base_url,
        info.retry_max_attempts,
        info.timeout_read,
    )
    profile = avito.account().get_self()

print(profile.user_id)
```

Security-модель SDK подробно описана в [explanations/security-and-redaction.md](../explanations/security-and-redaction.md). Диагностика и обработка ошибок — в [рецепте по диагностике](diagnostics-and-logging.md).
