# Авторизация и конфигурация

SDK поддерживает три публичных способа создать клиент. Для приложений и CLI обычно удобен `AvitoClient.from_env()`: секреты остаются вне кода, а конфигурация читается одинаково локально и в CI.

```bash
export AVITO_CLIENT_ID="client-id"
export AVITO_CLIENT_SECRET="client-secret"
```

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    profile = avito.account().get_self()

print(profile.user_id)
```

Для коротких скриптов можно передать ключи явно:

```python
from avito import AvitoClient

with AvitoClient(client_id="client-id", client_secret="client-secret") as avito:
    info = avito.debug_info()

print(info.base_url)
```

Для полного контроля используйте `AvitoSettings` и `AuthSettings`.

```python
from avito import AuthSettings, AvitoClient, AvitoSettings

settings = AvitoSettings(
    user_id=123,
    auth=AuthSettings(
        client_id="client-id",
        client_secret="client-secret",
    ),
)

with AvitoClient(settings) as avito:
    info = avito.debug_info()

print(info.user_id)
```

Значения из process environment имеют приоритет над `.env`. Если обязательные ключи отсутствуют, SDK поднимает `ConfigurationError` при создании клиента, до первого HTTP-запроса. Безопасный снимок `debug_info()` не содержит `client_secret`, access token или заголовок `Authorization`.
