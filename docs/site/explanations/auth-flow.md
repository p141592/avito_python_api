# OAuth и токены

SDK прячет OAuth-обмен за `AuthProvider`, чтобы пользовательский код работал с доменными методами, а не с access token, refresh token и заголовками `Authorization`.

```mermaid
sequenceDiagram
    participant App as Пользовательский код
    participant Client as AvitoClient
    participant Domain as Домен
    participant Transport as Transport
    participant Auth as AuthProvider
    participant API as Avito API

    App->>Client: AvitoClient.from_env()
    App->>Domain: account().get_self()
    Domain->>Transport: GET /core/v1/accounts/self
    Transport->>Auth: get_access_token()
    Auth-->>Transport: access token
    Transport->>API: request + Authorization
    API-->>Transport: JSON response
    Transport-->>Domain: payload
    Domain-->>App: typed model
```

## Где живёт ответственность

`AvitoClient` создаёт общий контекст: настройки, auth и transport. Доменный объект выбирает бизнес-операцию. Section client знает HTTP path и payload. `Transport` добавляет токен и применяет retry. `AuthProvider` кэширует токен и обновляет его, если upstream отвечает `401`.

Такой порядок важен для public contract: публичный метод не принимает access token, не возвращает OAuth-payload и не требует от пользователя повторять refresh-flow.

## Ошибка 401

`401` считается ошибкой аутентификации, а не авторизации. SDK инвалидирует токен там, где это допустимо, и поднимает `AuthenticationError`, если запрос не может быть выполнен успешно. `403` остаётся отдельным `AuthorizationError`: эти типы не наследуются друг от друга.

## Autoteka

Часть операций Автотеки использует отдельные OAuth-настройки. Они лежат в `AuthSettings` рядом с основными credentials, но не смешиваются с публичными методами домена: пользователь вызывает `autoteka_vehicle()` и `autoteka_report()`, а выбор token endpoint остаётся внутренним поведением auth-слоя.

Список env-переменных смотрите в [reference по конфигурации](../reference/config.md).
