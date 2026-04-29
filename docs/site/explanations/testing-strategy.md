# Стратегия тестирования

SDK тестируется через публичные контракты: доменные методы, typed-модели, exceptions и `avito.testing`. Тесты не должны подменять приватные поля клиента или зависеть от настоящего HTTP там, где сценарий можно проверить fake transport.

## Уровни

| Уровень | Что проверяет |
|---|---|
| Unit | Мапперы, сериализация моделей, validation |
| Contract | Публичная поверхность, исключения, deprecated warnings |
| Domain | Доменные методы поверх `FakeTransport` |
| Docs | README/tutorials/how-to snippets через `mktestdocs` |
| Build gates | Swagger binding discovery, reference surface, docstring contract |

## FakeTransport

`FakeTransport` сценарно описывает HTTP-ответы и записывает запросы. Это публичный testing namespace, поэтому consumer-код может строить тесты без реального Avito API, без OAuth-секретов и без monkeypatch приватных атрибутов.

Docs-harness использует тот же подход: `AvitoClient.from_env()` в markdown-примерах возвращает клиент поверх fake transport, поэтому copy-paste snippets проходят в CI без сетевых запросов.

## Почему не мокать domain methods

Если тест подменяет `account().get_self()` напрямую, он проверяет только consumer-код. Если тест строит `AvitoClient` поверх fake transport, он дополнительно проверяет HTTP path, payload, mapper и публичную модель. Поэтому fake transport ближе к реальному интеграционному контракту.

Практический reference по testing API смотрите в [reference по тестированию](../reference/testing.md).
