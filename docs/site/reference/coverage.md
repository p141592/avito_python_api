# Покрытие API

Эта страница генерируется при сборке MkDocs из Swagger binding report.
Исходный код генератора: `docs/site/assets/_gen_reference.py`.

Swagger/OpenAPI-спецификации в `docs/avito/api/` остаются источником истины,
а карта покрытия SDK строится из Swagger operation bindings на публичных
SDK-методах. Локальная проверка:

```bash
poetry run python scripts/lint_swagger_bindings.py --json --strict --output swagger-bindings-report.json
```

Сгенерированная страница показывает количество операций, bound/deprecated
статусы по каждому spec и ссылку на публичную карту операций.
