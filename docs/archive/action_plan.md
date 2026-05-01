# Swagger Binding Architecture Status

Статус: миграционный action plan завершен. Документ сохранен как краткий статус для восстановления контекста.

## Текущее состояние

- Swagger/OpenAPI specs в `docs/avito/api/*.json` остаются единственным источником HTTP-контрактов.
- Canonical coverage map строится из `@swagger_operation(...)` bindings на публичных domain methods.
- Strict invariant соблюден: каждая Swagger operation имеет ровно один binding, каждый discovered binding указывает на ровно одну Swagger operation.
- Summary/helper methods в `AvitoClient` не получают Swagger bindings, если они не соответствуют одной upstream Swagger operation.
- Deprecated Swagger operations требуют `deprecated=True`, `legacy=True` и runtime `DeprecationWarning`.

## Подтвержденные метрики

- Swagger specs: 23.
- Swagger operations: 204.
- Deprecated operations: 7.
- Bound operations: 204.
- Unbound/duplicate/ambiguous: 0.
- API-domain legacy files: 0.

## Поддерживаемые команды

```bash
make swagger-lint
make swagger-coverage
make architecture-lint
make check
make docs-strict
```

## Правила для будущих API-изменений

- Сначала сверить контракт с `docs/avito/api/*.json`.
- Добавить или обновить public domain method, `OperationSpec`, typed models и request/query dataclasses.
- Поставить один `@swagger_operation(...)` на публичный SDK method.
- Не дублировать schemas, statuses, content types, request/response models или error models в decorator.
- Для write-операций сохранять одинаковую сборку payload в обычном и `dry_run=True` режиме.
- После изменения публичной API-поверхности запускать strict Swagger lint, domain tests, mypy и ruff.
