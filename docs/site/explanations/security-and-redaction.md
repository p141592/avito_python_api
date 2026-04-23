# Security и redaction

SDK не является secret manager, но обязан не ухудшать безопасность consumer-приложения: не печатать OAuth-секреты в исключениях, не возвращать access token из diagnostics и не смешивать безопасный debug snapshot с transport internals.

## Что SDK редактирует

Секретные значения редактируются в error metadata и diagnostic paths: access token, refresh token, `client_secret`, заголовок `Authorization` и близкие OAuth-поля. Это применяется к логируемым metadata и исключениям, чтобы стандартный catch/log `AvitoError` не раскрывал credentials.

`debug_info()` возвращает только безопасный снимок: `base_url`, `user_id`, флаг auth, таймауты и retry-настройки. В нём нет access token, `client_secret` и raw headers.

## Что остаётся ответственностью consumer-кода

Модели SDK могут содержать пользовательские данные: телефоны, email, тексты сообщений, адреса, цены, идентификаторы заказов. `to_dict()` и `model_dump()` сериализуют публичную модель, а не применяют бизнес-редакцию персональных данных. Если consumer-код пишет эти данные в логи, он должен применять собственную политику redaction.

## Ошибки

Ошибки SDK сохраняют поля `operation`, `status`, `request_id`, `attempt`, `method`, `endpoint`. Эти поля достаточны для диагностики большинства интеграционных сбоев и не требуют раскрывать raw request body или OAuth headers.

## Практическое правило

Логируйте typed exception metadata и `debug_info()`. Не логируйте raw payload, binary content и полные `to_dict()` пользовательских моделей без фильтрации на стороне приложения.

Поля `debug_info()` описаны в [reference по клиенту](../reference/client.md), а metadata ошибок — в [reference по исключениям](../reference/exceptions.md).
