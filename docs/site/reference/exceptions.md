# Исключения

`AvitoError` — базовый тип ошибок SDK. Специализированные исключения отражают
класс сбоя: аутентификация, авторизация, validation, rate limit, transport и
ошибки upstream API.

## Диагностические поля

Каждое публичное исключение сохраняет безопасные диагностические данные:

| Поле | Назначение |
|---|---|
| `operation` | Имя SDK-операции, во время которой возникла ошибка |
| `status` / `status_code` | HTTP-статус upstream-ответа, если он был получен |
| `request_id` | Идентификатор upstream-запроса, если API его вернул |
| `attempt` | Номер retry-попытки, если он доступен transport-слою |
| `method` | HTTP-метод запроса |
| `endpoint` | Путь endpoint без OAuth-секретов и приватных headers |

Секреты в `payload`, `headers` и `metadata` редактируются через
`sanitize_metadata()`.

## Иерархия

::: avito.core.exceptions
