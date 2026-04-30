# Architecture TODO

Статус: исторический migration TODO завершен и заменен текущим списком улучшений.

## Завершено

- Все API-домены переведены на v2 layout без domain-level `client.py`, `mappers.py`, standalone `enums.py`.
- Все 204 Swagger operations имеют ровно один discovered SDK binding.
- Strict Swagger lint входит в общий quality gate.
- Архитектурный линтер запрещает возврат legacy-файлов, legacy-imports и старого mapper/request-public-model пути.

## Актуальные следующие шаги

1. Поддерживать `OperationSpec[T]` и `_execute() -> T` без возврата к `# type: ignore[return-value]`.
2. Постепенно дробить крупные домены на `models/` и `operations/` пакеты: сначала `orders`, затем `promotion`, затем `ads`.
3. Разделить быстрый offline gate и fresh-Swagger update gate, чтобы обычный `make check` меньше зависел от сети.
4. Добавить явный coverage threshold после добора тестов для core-модулей с самым низким покрытием.
5. Регулярно обновлять `architecture-inventory-report.json` и Swagger report при изменении публичной API-поверхности.

## Проверки

Минимальная проверка архитектурного состояния:

```bash
poetry run python scripts/lint_architecture.py
poetry run python scripts/lint_swagger_bindings.py --strict
poetry run mypy avito
poetry run ruff check .
poetry run pytest
```
