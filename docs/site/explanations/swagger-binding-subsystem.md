# Swagger binding subsystem

Swagger binding subsystem связывает локальный OpenAPI corpus с публичной поверхностью SDK. Его задача — доказуемо ответить на два вопроса:

- какая upstream Swagger operation покрыта каким публичным SDK-методом;
- как contract-test runner должен вызвать этот SDK-метод без реального HTTP.

Swagger/OpenAPI-файлы в `docs/avito/api/*.json` остаются единственным источником истины по HTTP-контракту: method, path, parameters, request body, content type, statuses, schemas и operation-level `deprecated`. Binding-и не дублируют эти данные. Они хранят только адресацию между SDK и Swagger.

## Основные компоненты

| Компонент | Файл | Ответственность |
|---|---|---|
| Binding decorator | `avito/core/swagger.py` | Записывает metadata на публичный SDK-метод |
| Swagger registry | `avito/core/swagger_registry.py` | Загружает `docs/avito/api/*.json`, нормализует операции и проверяет базовую валидность specs |
| Binding discovery | `avito/core/swagger_discovery.py` | Находит decorated public domain methods без создания `AvitoClient` и без HTTP |
| Linter | `avito/core/swagger_linter.py`, `scripts/lint_swagger_bindings.py` | Проверяет, что binding-и полные, уникальные и соответствуют Swagger |
| Report | `avito/core/swagger_report.py` | Формирует JSON report для docs/reference и coverage |
| Factory map | `avito/core/swagger_factory_map.py` | Даёт вспомогательную, неканоническую карту `AvitoClient factory -> domain class -> spec candidates` |
| Contract runner | `avito/testing/swagger_fake_transport.py` | Строит SDK-вызовы по binding metadata и валидирует фактический request/response через Swagger |

Каноническая карта покрытия строится только из `Swagger operation key -> discovered binding`. Markdown inventory не участвует в coverage и не является источником истины.

## Binding metadata

Публичный декоратор:

```python
@swagger_operation(
    method: str,
    path: str,
    *,
    spec: str | None = None,
    operation_id: str | None = None,
    factory: str | None = None,
    factory_args: Mapping[str, str] | None = None,
    method_args: Mapping[str, str] | None = None,
    deprecated: bool = False,
    legacy: bool = False,
)
```

Class-level metadata на domain object задаёт defaults:

```python
__swagger_domain__: str
__swagger_spec__: str
__sdk_factory__: str
__sdk_factory_args__: Mapping[str, str]
```

Приоритет значений:

1. Значения из `@swagger_operation(...)`.
2. Значения из class-level metadata.
3. Auto-resolve через registry, только если `method + normalized_path` совпадает ровно с одной Swagger operation во всём corpus.

Decorator записывает metadata в `func.__swagger_binding__` и, для явно разрешённых multi-operation SDK methods, в `func.__swagger_bindings__`. Он не меняет поведение метода и не читает Swagger-файлы на import time.

## Operation identity

Primary key операции:

```text
spec + method + normalized_path
```

Нормализация:

- `method` приводится к uppercase;
- trailing slash удаляется, кроме `/`;
- path хранится в Swagger format: `/path/{param}`;
- path остаётся case-sensitive;
- syntax path parameter кроме `{name}` запрещён.

`operation_id` является дополнительной проверкой. Он помогает поймать ошибочный binding, но не является primary identity.

## Expression mappings

`factory_args` и `method_args` описывают, как generated contract data превращается в вызов публичного SDK:

| Expression | Источник |
|---|---|
| `path.<name>` | path parameter Swagger operation |
| `query.<name>` | query parameter Swagger operation |
| `header.<name>` | header parameter Swagger operation |
| `body` | весь request body |
| `body.<field>` | поле request body |
| `constant.<name>` | контролируемая тестовая константа |

Expressions не являются Python-кодом. Произвольные callables, dotted paths вне whitelist и transport/request DTO запрещены.

Текущая реализация валидирует `path.*`, `query.*`, `header.*`, наличие `requestBody` для `body`/`body.*` и наличие `constant.*` в test constants registry. Если требуется строгая field-level проверка `body.<field>` против JSON schema properties, registry должен дополнительно извлекать request body schema metadata.

## Discovery

Discovery импортирует пакет `avito`, но не создаёт `AvitoClient`, не читает обязательные env vars и не делает сетевых вызовов. Сканируются публичные domain classes из `avito/<domain>/domain.py` и заранее описанные non-domain exceptions, например low-level auth token bindings.

Игнорируются:

- private methods;
- internal helpers;
- summary/helper methods на `AvitoClient`, если они не соответствуют одной конкретной upstream operation;
- section clients как canonical target, кроме явно задокументированных legacy/non-domain exceptions.

## Linter modes

Основные команды:

```bash
poetry run python scripts/lint_swagger_bindings.py
poetry run python scripts/lint_swagger_bindings.py --strict
poetry run python scripts/lint_swagger_bindings.py --json --strict --output swagger-bindings-report.json
make swagger-lint
```

Non-strict mode валидирует specs и уже найденные bindings. Strict mode дополнительно требует, чтобы каждая Swagger operation имела ровно один binding. `make swagger-lint` запускает strict mode и входит в `make check`.

JSON report используется как стабильный machine-readable API для generated reference и coverage:

```json
{
  "summary": {
    "specs": 23,
    "operations_total": 204,
    "deprecated_operations": 7,
    "bound": 204,
    "unbound": 0,
    "duplicate": 0,
    "ambiguous": 0
  },
  "operations": [],
  "bindings": [],
  "factory_mapping": {},
  "errors": []
}
```

## Deprecated and legacy policy

Operation-level `deprecated: true` in Swagger requires:

- `deprecated=True` on binding;
- `legacy=True` on binding;
- runtime `DeprecationWarning` on the public SDK method through `deprecated_method(...)`.

`legacy=True` on a non-deprecated operation is forbidden unless a separate allowlist entry exists with a reason and removal date. Deprecated schema fields, properties and enum values do not create operation-level legacy requirements.

## Multi-operation SDK methods

The strict invariant is:

```text
each Swagger operation -> exactly one discovered binding
```

One SDK method may have multiple bindings only when one public method intentionally covers multiple upstream operations or modes. Such cases must be explicit through stacked `@swagger_operation(...)` decorators and must remain visible to discovery through `__swagger_bindings__`.

This exception is narrow. It must not be used to hide duplicate public methods or to bind unrelated operations to a generic method.

## Contract tests

`SwaggerFakeTransport` uses discovered binding metadata to:

1. Build an `AvitoClient` with fake transport.
2. Create the correct domain object through `AvitoClient` factory and `factory_args`.
3. Call the public SDK method with `method_args`.
4. Match the actual HTTP request against Swagger method/path.
5. Validate required path/query/header parameters and request body/content type.
6. Return declared Swagger response statuses only.
7. Let normal SDK mapping and exception mapping run.

Contract tests must stay network-free. They are not a replacement for domain tests, but they catch binding drift: a method can be present in docs yet still fail contract invocation if factory args, method args, path, body or status handling are wrong.

## API method change checklist

When adding or changing a public API method that corresponds to Avito API:

1. Confirm the upstream operation in `docs/avito/api/*.json`.
2. Add or update the domain method, section client call, mapper and public models.
3. Add `@swagger_operation(...)` on the public domain method without schemas/statuses/content types in the decorator.
4. Add or update class-level metadata if the domain class is new.
5. Document the public method through docstring so generated reference explains arguments, return model, pagination/dry-run/idempotency behavior and common exceptions.
6. Add focused domain tests with `FakeTransport`.
7. Add or adjust mapper/model tests when response or serialization changes.
8. Ensure the binding is exercised by strict `make swagger-lint` and, when needed, `SwaggerFakeTransport` contract tests.
9. Update user-facing docs when the method creates a new workflow, changes behavior, or introduces a non-obvious contract.

Minimum local verification for API-surface changes:

```bash
make swagger-lint
poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py
poetry run pytest tests/domains/<domain>/
poetry run mypy avito
poetry run ruff check .
```

Before merging a complete API change, run:

```bash
make check
```
