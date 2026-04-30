# Swagger Binding Architecture Action Plan

## Контекст для быстрого восстановления

Репозиторий: `/Users/n.baryshnikov/Projects/avito_python_api`.

Цель новой архитектуры: заменить старую inventory-архитектуру машинно-проверяемой canonical coverage map на базе:

1. Swagger/OpenAPI спецификаций из `docs/avito/api/*.json`.
2. `@swagger_operation(...)` bindings на публичных SDK domain methods.
3. `swagger-lint`, который строит и валидирует карту покрытия.

`docs/avito/inventory.md` считается артефактом старой архитектуры. Он не должен быть источником истины и не должен участвовать в новых проверках покрытия.

Текущий Swagger corpus:

- 23 файла в `docs/avito/api`.
- 204 операции.
- 7 deprecated операций.

Ключевой инвариант новой архитектуры:

```text
Swagger operation
<-> exactly one @swagger_operation SDK method
-> SwaggerFakeTransport validates actual HTTP request/response
-> contract tests validate all statuses and errors from Swagger
```

Важные локальные точки:

- `STYLEGUIDE.md` является нормативным документом и имеет приоритет.
- Публичный фасад: `avito/client.py`, класс `AvitoClient`.
- Публичные domain methods: `avito/<domain>/domain.py`.
- Section clients: `avito/<domain>/client.py`.
- Старые inventory-ссылки в `CLAUDE.md`, README, docs и генераторах документации мигрированы на binding discovery.
- `Makefile` сейчас имеет `check: test typecheck lint swagger-lint build`; strict `swagger-lint` уже входит в общий gate.

Ограничения архитектуры:

- Декоратор не должен дублировать Swagger-контракт.
- В binding запрещены response/request schemas, statuses, content types, response models, request models, error models.
- Swagger остаётся единственным источником HTTP method/path/parameters/body/status/schema/deprecated state.
- Binding описывает только соответствие SDK method операции Swagger и способ построить SDK-вызов для contract tests.

## Design Decisions

1. `docs/avito/inventory.md` retired. Новая canonical coverage map строится только из Swagger specs и discovered bindings.
2. Canonical bindings ставятся на публичные domain methods в `avito/<domain>/domain.py`.
3. Section clients в `avito/<domain>/client.py` не являются canonical public binding target, кроме заранее описанного legacy-исключения.
4. Summary/helper methods в `AvitoClient` не получают Swagger bindings, если они не соответствуют одной конкретной upstream Swagger operation.
5. Private methods, `_require_*` helpers и internal serialization helpers не участвуют в discovery.
6. Discovery не должен создавать `AvitoClient`, читать обязательные env vars, ходить в сеть или выполнять реальные HTTP calls.
7. `avito/core/swagger.py` не должен загружать Swagger files на import time.
8. `operation_id` является дополнительной проверкой, но не primary identity. Primary identity: `spec + method + normalized_path`.
9. Allowlist для deprecated/legacy/completeness исключений по умолчанию запрещён. Если он понадобится, запись должна иметь причину и дату удаления.
10. `deprecated` в binding сверяется только с operation-level `deprecated` из Swagger operation. Deprecated schema fields, enum values и properties не влияют на operation binding.

## Decorator Contract

Модуль:

```text
avito/core/swagger.py
```

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

Binding model:

```python
@dataclass(frozen=True, slots=True)
class SwaggerOperationBinding:
    method: str
    path: str
    spec: str | None
    operation_id: str | None
    factory: str | None
    factory_args: Mapping[str, str]
    method_args: Mapping[str, str]
    deprecated: bool
    legacy: bool
```

Декоратор записывает metadata в `func.__swagger_binding__`, не меняет поведение метода и не читает Swagger files на import time.

Class-level metadata на публичных domain objects:

```python
__swagger_domain__: str
__swagger_spec__: str
__sdk_factory__: str
__sdk_factory_args__: Mapping[str, str]
```

Section clients могут иметь binding metadata только как заранее описанное legacy-исключение.

## Path Normalization

Правила normalizing для identity и линтера:

1. `method` приводится к uppercase.
2. `path` хранится в Swagger format: `/path/{param}`.
3. Trailing slash удаляется, кроме path `/`.
4. Path parameter syntax кроме `{name}` запрещён.
5. Path остаётся case-sensitive.
6. Primary operation key: `spec + method + normalized_path`.
7. Если `spec` не указан, auto-resolve по `method + normalized_path` разрешён только при ровно одном совпадении среди всех Swagger files.

## Execution Modes

`scripts/lint_swagger_bindings.py` должен поддерживать несколько режимов, чтобы внедрение можно было вести поэтапно:

1. Default / non-strict mode:
   - валидирует Swagger files;
   - валидирует только уже найденные SDK bindings;
   - не требует покрытия всех 204 операций;
   - подходит для Этапов 1-5.
2. Strict mode:
   - включает все default-проверки;
   - требует, чтобы каждая Swagger operation имела ровно один SDK binding;
   - включается в `make check` только после завершения доменной разметки.
3. JSON report mode:
   - отдаёт machine-readable отчёт по операциям, bindings, missing/duplicate/ambiguous cases;
   - используется docs/reference generator и coverage badge;
   - заменяет старые inventory-derived reports.

CLI contract:

```bash
poetry run python scripts/lint_swagger_bindings.py
poetry run python scripts/lint_swagger_bindings.py --strict
poetry run python scripts/lint_swagger_bindings.py --json
poetry run python scripts/lint_swagger_bindings.py --json --output swagger-bindings-report.json
```

Exit codes:

- `0`: ошибок нет;
- `1`: найдены validation errors;
- `2`: ошибка CLI usage, чтения specs или некорректной среды запуска.

## JSON Report Contract

JSON report должен быть стабильным API для docs/reference generator и badge.

Минимальная структура:

```json
{
  "summary": {
    "specs": 23,
    "operations_total": 204,
    "deprecated_operations": 7,
    "bound": 0,
    "unbound": 204,
    "duplicate": 0,
    "ambiguous": 0
  },
  "operations": [],
  "bindings": [],
  "errors": []
}
```

`operations[]` содержит `spec`, `method`, `path`, `operation_id`, `deprecated`, `status`, `binding`.

`bindings[]` содержит `module`, `class`, `method`, `operation_key`, `factory`, `factory_args`, `method_args`.

`errors[]` содержит `code`, `message`, `operation_key`, `sdk_method`.

## Definition of Done

Критерии готовности этапов:

- Этап 0 готов, когда в документации больше нет утверждения, что inventory является canonical source of truth.
- Этап 1 готов, когда unit-тесты декоратора проходят, а `avito/core/swagger.py` не импортирует и не читает `docs/avito/api`.
- Этап 2 готов, когда registry стабильно извлекает 23 specs, 204 operations и 7 deprecated operations.
- Этап 3 готов, когда discovery на пустой/частичной разметке не требует env vars, сети и создания `AvitoClient`.
- Этап 4 готов, когда `make swagger-lint` работает в non-strict режиме и возвращает стабильные actionable error codes.
- Этап 5 готов по домену, когда все его public operation methods имеют bindings и проходят `make swagger-lint` в non-strict режиме.
- Этап 6 готов, когда strict mode подтверждает ровно один binding на каждую из 204 Swagger operations.
- Этап 7 готов, когда все `factory_args` и `method_args` проходят validation against Swagger parameters/request body.
- Этап 8 готов, когда contract tests проверяют generated SDK calls через `SwaggerFakeTransport` без реального HTTP.
- Этап 9 готов, когда `make check` включает `swagger-lint --strict` и проходит полностью.

## Этап 0. Зафиксировать миграционное решение

1. Обновить `CLAUDE.md`, README и docs: заменить “inventory is canonical mapping” на “Swagger bindings are canonical coverage map”.
2. Проверить, что старые `check_inventory_*` скрипты и ссылки больше не участвуют в `Makefile`, docs или CI.
3. Зафиксировать, что documentation/reference должны генерироваться из binding discovery, а не из markdown inventory.

## Этап 1. Базовый декоратор

1. Создать `avito/core/swagger.py`.
2. Реализовать `SwaggerOperationBinding`:
   - `@dataclass(frozen=True, slots=True)`;
   - `method` normalizes to uppercase;
   - `factory_args` и `method_args` stored as immutable mappings;
   - без загрузки Swagger на import time.
3. Реализовать `swagger_operation(...)` с публичной сигнатурой из раздела `Decorator Contract`.
4. Экспортировать публичный API из `avito/core/__init__.py`, если это соответствует локальному паттерну.
5. Добавить unit-тесты:
   - metadata пишется в `func.__swagger_binding__`;
   - поведение decorated method не меняется;
   - mappings immutable;
   - лишние/запрещённые kwargs невозможны через сигнатуру.

## Этап 2. Swagger registry для линтера

1. Создать импортируемый parser/helper-модуль для registry и discovery.
2. Оставить `scripts/lint_swagger_bindings.py` тонким CLI wrapper-ом.
3. Загружать все `docs/avito/api/*.json`.
4. Извлекать операции в структуру:
   - `spec`;
   - `method`;
   - `path`;
   - `operation_id`;
   - `deprecated`;
   - path/query/header parameters;
   - request body metadata.
5. Проверять базовую валидность specs:
   - JSON валиден;
   - есть `paths`;
   - operation keys уникальны;
   - path parameters из URL совпадают с описанными параметрами.

## Этап 3. Discovery SDK bindings

1. В discovery-коде импортировать пакет `avito` без создания `AvitoClient`.
2. Обойти публичные domain-классы из `avito/<domain>/domain.py` и найти методы с `__swagger_binding__`.
3. Для каждого binding вычислить effective metadata:
   - method-level values;
   - class-level `__swagger_spec__`, `__sdk_factory__`, `__sdk_factory_args__`;
   - auto-resolve только если совпадение однозначно.
4. Сформировать canonical map: `Swagger operation key -> SDK method`.
5. Явно игнорировать section clients, private methods, summary methods и internal helpers.

## Этап 3.5. Baseline coverage report

1. Реализовать non-authoritative baseline report на базе Swagger registry и binding discovery.
2. Для каждой операции показать:
   - `spec`;
   - `method`;
   - `path`;
   - `operation_id`;
   - `deprecated`;
   - binding status: `bound`, `unbound`, `duplicate`, `ambiguous`.
3. Если возможно безопасно угадать SDK target, показывать guessed domain/class/method как подсказку, но не как источник истины.
4. Использовать report как рабочий инструмент разметки доменов.
5. Не возвращать `docs/avito/inventory.md` и не делать markdown inventory canonical.

## Этап 4. MVP линтера

1. Реализовать проверки:
   - binding указывает на существующую Swagger operation;
   - `spec` существует;
   - `operation_id`, если указан, совпадает;
   - duplicate bindings запрещены;
   - `deprecated` / `legacy` согласованы со Swagger;
   - factory существует на `AvitoClient`.
2. Добавить signature validation для factory и decorated SDK method:
   - `factory_args` соответствуют сигнатуре factory;
   - `method_args` соответствуют сигнатуре SDK method;
   - required параметры покрыты mapping-ом;
   - лишние mapping keys запрещены.
3. Сделать actionable ошибки с кодами вида `[SWAGGER_BINDING_NOT_FOUND]`.
4. Добавить `make swagger-lint`, запускающий non-strict mode.
5. Пока не включать strict completeness в `make check`, если binding-и ещё не расставлены на все 204 операции.

## Этап 4.5. Deprecated / legacy policy

1. Зафиксировать policy для 7 operation-level deprecated Swagger operations.
2. Определить, когда binding обязан иметь `legacy=True`.
3. Проверить, что deprecated public methods имеют runtime deprecation behavior, если это требуется STYLEGUIDE.
4. Запретить `legacy=True` на non-deprecated operation без явного исключения.
5. Если исключения всё же понадобятся, создать отдельный allowlist-файл с причиной и датой удаления.

Policy:

- Operation-level `deprecated: true` из Swagger требует `deprecated=True` и `legacy=True` в binding.
- Deprecated binding обязан указывать на public SDK method с runtime `DeprecationWarning` через `deprecated_method(...)`.
- `legacy=True` на non-deprecated Swagger operation запрещён без отдельного allowlist-исключения.
- Deprecated schema fields, properties и enum values не создают deprecated/legacy binding requirement.
- Текущие operation-level deprecated операции: `CPAАвито.json GET /cpa/v1/call/{call_id}`, `CPAАвито.json POST /cpa/v2/balanceInfo`, `CPAАвито.json POST /cpa/v2/callById`, `Автозагрузка.json GET /autoload/v1/profile`, `Автозагрузка.json POST /autoload/v1/profile`, `Автозагрузка.json GET /autoload/v2/reports/last_completed_report`, `Автозагрузка.json GET /autoload/v2/reports/{report_id}`.

## Этап 4.75. Factory/domain mapping inventory

1. Построить рабочую таблицу `AvitoClient factory -> domain class -> spec candidates`.
2. Проверить, что каждый factory можно introspect-ить без создания `AvitoClient`.
3. Выявить операции, которые сейчас представлены summary/helper methods и не должны получать direct binding.
4. Использовать таблицу как подготовку к доменной разметке, но не делать её source of truth.

Результат этапа хранится как non-authoritative `factory_mapping` section в JSON report. Она помогает расставлять domain bindings, но canonical coverage по-прежнему считается только из Swagger operations и discovered `@swagger_operation` bindings.

## Этап 5. Расстановка binding-ов по доменам

Делать маленькими PR/commit-ами по одному домену:

1. `accounts`, `tariffs`, `ratings` как самые маленькие.
2. `messenger`.
3. `promotion`.
4. `ads` / autoload legacy.
5. `orders` / delivery / stock.
6. `jobs`.
7. `cpa` / calltracking.
8. `autoteka`.
9. `realty`.

Для каждого домена:

- добавить class-level metadata;
- расставить `@swagger_operation`;
- описать `factory_args` и `method_args`;
- запускать `make test`, `make typecheck`, `make lint`, `make swagger-lint`;
- не добавлять request/response schemas в decorators.

Для каждого домена в changelog фиксировать:

- сколько операций стало bound;
- сколько осталось unbound;
- какие deprecated/legacy решения приняты;
- какие проверки запускались.

## Этап 6. Strict completeness

1. Включить проверку: каждая из 204 Swagger operations имеет ровно один binding.
2. Включить проверку: каждый binding уникален.
3. Перевести `make swagger-lint` на strict mode.
4. Сделать `make swagger-lint` частью `make check`.
5. Обновить badge/docs покрытия: coverage теперь считается из Swagger registry + binding discovery.

## Этап 6.5. Documentation migration

1. Перевести generated reference/coverage docs на JSON report или импортируемый discovery API.
2. Удалить или переписать оставшиеся inventory-derived docs paths.
3. Обновить README badge/description: coverage считается из Swagger bindings.
4. Проверить, что `docs/site/reference/coverage.md` и related pages не называют inventory источником истины.

## Этап 7. Path expression validation

1. Проверять `path.<name>` против path params.
2. Проверять `query.<name>` против query params.
3. Проверять `header.<name>` против header params.
4. Проверять `body` и `body.<field>` против request body.
5. Ввести test constants registry для `constant.<name>`.
6. Запретить любые expressions вне whitelist.

## Этап 8. Contract tests

1. Реализовать `SwaggerFakeTransport`.
2. На основе binding-а строить SDK вызов из generated request data.
3. Request-contract tests: проверять, что SDK делает HTTP request, соответствующий Swagger:
   - method;
   - path;
   - path/query/header params;
   - body shape;
   - content type.
4. Response-contract tests: проверять happy-path response mapping в typed SDK models.
5. Error-contract tests: проверять statuses и exception mapping из Swagger.
6. Отдельно проверить deprecated/legacy операции.
7. Начать с read-only операций, потом расширить на write-операции и idempotency.

## Этап 9. Финальный gate

1. Запустить:
   - `make test`;
   - `make typecheck`;
   - `make lint`;
   - `make swagger-lint`;
   - `make build`.
2. Затем `make check`, где `swagger-lint` уже должен быть включён.
3. Проверить, что старый inventory нигде не упоминается как источник истины.

## Этап 10. Устранение выявленных несоответствий после выполнения плана

Цель: отдельным новым этапом закрыть несоответствия, найденные после выполнения Этапов 0-9, не переписывая историю уже выполненных пунктов.

Не входит в этот этап:

- дефект публичного Swagger corpus с несовпадением `{userId}` / `{itemId}` и `pathUserId` / `pathItemId`;
- patch/override pipeline для upstream specs.

### 10.1. Запрет нескольких bindings на один SDK method

Требование: несколько Swagger bindings на один SDK method запрещены. Каждая Swagger operation должна иметь собственный discovered SDK method target.

1. Найти все SDK methods, на которых discovery видит больше одного Swagger binding.
2. Для каждого случая выбрать явное разделение:
   - отдельные public SDK methods, если операции являются разными пользовательскими действиями;
   - отдельные documented wrappers, если один сценарий раньше скрывал несколько upstream modes;
   - отдельные low-level auth SDK targets для token operations, если они остаются non-domain binding exception.
3. Удалить поддержку stacked `@swagger_operation(...)` из декоратора:
   - не накапливать `func.__swagger_bindings__`;
   - повторная установка binding на метод должна быть ошибкой или должна явно запрещаться тестом.
4. Обновить discovery:
   - читать только `func.__swagger_binding__`;
   - считать `__swagger_bindings__` или несколько bindings на одном method ошибкой совместимости.
5. Обновить linter:
   - добавить error code `SWAGGER_BINDING_METHOD_MULTIPLE`;
   - падать, если один `sdk_method` связан больше чем с одной operation;
   - не вводить allowlist для multi-binding methods.
6. Обновить JSON report:
   - оставить `bindings[]` как плоский список one binding per sdk_method;
   - добавить ошибку в `errors[]`, если обнаружено legacy `__swagger_bindings__`.
7. Обновить docs:
   - `docs/site/explanations/swagger-binding-subsystem.md`;
   - `STYLEGUIDE.md`;
   - `CLAUDE.md`;
   - убрать формулировки, допускающие multi-operation SDK methods.
8. Добавить тесты:
   - декоратор запрещает stacked bindings;
   - discovery/linter ловят legacy `__swagger_bindings__`;
   - strict report остаётся `204/204 bound`, `0 duplicate`, `0 ambiguous`, `0 errors`.

### 10.2. Schema-aware validation для `body.<field>`

Требование: `body.<field>` должен проверяться против request body schema/properties, а не только против наличия `requestBody`.

1. Расширить `SwaggerRequestBody` в `avito/core/swagger_registry.py`:
   - хранить `content_types`;
   - хранить top-level body field names/properties;
   - хранить флаг, что schema была успешно извлечена.
2. Добавить schema resolver для локальных `$ref`:
   - `#/components/schemas/<name>`;
   - object schemas с `properties`;
   - `allOf`/`oneOf`/`anyOf` только если можно безопасно извлечь top-level properties; иначе фиксировать unsupported schema state.
3. В `swagger_linter.py` изменить проверку `body.<field>`:
   - если `requestBody` отсутствует — текущая ошибка `SWAGGER_BINDING_BODY_MISSING`;
   - если schema/properties доступны и поля нет — новая ошибка `SWAGGER_BINDING_BODY_FIELD_NOT_FOUND`;
   - если schema не поддержана для field-level validation — новая actionable ошибка `SWAGGER_BINDING_BODY_SCHEMA_UNSUPPORTED`.
4. Добавить tests для registry:
   - inline object schema;
   - `$ref` schema;
   - missing properties;
   - unsupported schema shape.
5. Добавить tests для linter:
   - valid `body.<field>`;
   - invalid `body.missing`;
   - `body.<field>` при unsupported schema;
   - `body` остаётся валидным при любом request body.
6. Обновить JSON report/errors contract, если добавляются новые error codes.
7. Обновить `docs/site/explanations/swagger-binding-subsystem.md`, убрав оговорку, что field-level validation ещё не реализована.

### 10.3. Усиление contract tests до полного binding/status coverage

Требование: contract tests должны параметризованно покрывать все discovered bindings и все Swagger error status contracts, а не только representative samples/status categories.

1. Добавить parametrized request-contract test по всем discovered bindings:
   - загрузить registry;
   - загрузить discovery;
   - для каждого binding зарегистрировать success response;
   - вызвать SDK method через `SwaggerFakeTransport.invoke_binding`;
   - проверить, что request matched Swagger method/path и прошёл validation path/query/header/body/content-type.
2. Добавить deterministic payload generator:
   - использовать Swagger response schema, где она доступна;
   - использовать controlled payload registry для операций, где mapper требует доменно-специфичную форму;
   - запрещать неописанные silent fallbacks, которые маскируют отсутствие payload contract.
3. Добавить parametrized error-contract test по всем Swagger error responses:
   - для каждой operation и каждого numeric error status зарегистрировать `error_payload(status)`;
   - вызвать соответствующий binding;
   - проверить exception type по transport error mapping;
   - проверить, что message/metadata не нарушают публичный error contract.
4. Добавить coverage assertions:
   - количество request-contract cases равно количеству discovered bindings;
   - количество error-contract cases равно количеству numeric Swagger error responses;
   - deprecated operations входят в общий набор и дополнительно проверяют `DeprecationWarning`.
5. Если generated call невозможен для отдельной операции, тест должен падать. Allowlist для contract gaps не вводить без отдельного решения.
6. Обновить `SwaggerFakeTransport`, если нужно:
   - добавить schema-aware success payload generation helpers;
   - расширить test constants registry;
   - улучшить diagnostics при невозможности построить вызов.
7. Обновить docs/testing notes:
   - `docs/site/explanations/swagger-binding-subsystem.md`;
   - `docs/site/explanations/testing-strategy.md`;
   - `STYLEGUIDE.md`, если меняется обязательный verification set.

### 10.4. Verification

```bash
pytest tests/core/test_swagger.py tests/core/test_swagger_discovery.py tests/core/test_swagger_linter.py tests/core/test_swagger_report.py
pytest tests/core/test_swagger_registry.py tests/contracts/test_swagger_contracts.py
make swagger-lint
mypy avito
ruff check avito tests/core tests/contracts/test_swagger_contracts.py
make docs-strict
make check
```

## Критичный порядок

Не начинать с `SwaggerFakeTransport`. Сначала нужна стабильная карта `Swagger operation -> SDK method`.

Самый безопасный MVP:

1. Декоратор.
2. Swagger registry.
3. Binding discovery.
4. Baseline coverage report.
5. Линтер в non-strict режиме.
6. Deprecated/legacy policy.
7. Factory/domain mapping inventory.
8. Доменные binding-и.
9. Strict completeness.
10. Documentation migration.
11. Contract tests.

## Changelog

Записи добавляются при выполнении или изменении плана.

Формат:

| Date | Change | Status | Verification |
|---|---|---|---|
| 2026-04-29 | Создан `action_plan.md` с контекстом, этапами реализации и changelog. | Done | Manual review |
| 2026-04-29 | Добавлены design decisions, execution modes, definition of done, baseline report, deprecated/legacy policy и documentation migration. | Done | Manual review |
| 2026-04-29 | Удалены ссылки на внешний контекст, добавлены decorator contract, path normalization, CLI/JSON report contract, factory inventory и разбиение contract tests. | Done | Manual review |
| 2026-04-29 | Выполнен Этап 0: README, CLAUDE/AGENTS, docs и PR template переведены на Swagger bindings; inventory checks удалены из docs CI. | Done | `rg` по inventory/check_inventory/canonical source; manual review |
| 2026-04-29 | Выполнен Этап 1: добавлен `avito/core/swagger.py`, экспорт core API и unit-тесты декоратора. | Done | `pytest tests/core/test_swagger.py`; `pytest`; `mypy avito`; `ruff check` |
| 2026-04-29 | Выполнен Этап 2: добавлен Swagger registry/parser, тонкий `lint_swagger_bindings.py` wrapper и тесты на corpus 23/204/7. | Done | `pytest tests/core/test_swagger_registry.py`; `python scripts/lint_swagger_bindings.py`; `mypy avito`; `ruff check` |
| 2026-04-29 | Выполнен Этап 3: добавлен discovery публичных domain bindings с class-level defaults, auto-resolve spec и canonical map. | Done | `pytest tests/core/test_swagger_discovery.py`; `pytest`; `mypy avito`; `ruff check` |
| 2026-04-29 | Выполнен Этап 3.5: добавлен baseline JSON report по Swagger registry + binding discovery, статусы `bound`/`unbound`/`duplicate`/`ambiguous` и JSON-режим CLI. | Done | `pytest tests/core/test_swagger.py tests/core/test_swagger_registry.py tests/core/test_swagger_discovery.py tests/core/test_swagger_report.py`; `ruff check avito/core/swagger_report.py scripts/lint_swagger_bindings.py tests/core/test_swagger_report.py`; `mypy avito`; `python scripts/lint_swagger_bindings.py --json --output /tmp/swagger-bindings-report.json` |
| 2026-04-29 | Выполнен Этап 4: добавлен MVP Swagger binding linter, validation ошибок binding/spec/operation_id/duplicate/deprecated/legacy/factory/signature, `make swagger-lint` и исправлены 2 path parameter mismatch в локальном Swagger corpus. | Done | `pytest tests/core/test_swagger.py tests/core/test_swagger_registry.py tests/core/test_swagger_discovery.py tests/core/test_swagger_report.py tests/core/test_swagger_linter.py`; `make swagger-lint`; `pytest`; `mypy avito`; `ruff check .`; `python scripts/lint_swagger_bindings.py --json --output /tmp/swagger-bindings-report-stage4.json` |
| 2026-04-29 | Выполнен Этап 4.5: зафиксирована deprecated/legacy policy для 7 operation-level deprecated operations, runtime deprecation metadata добавлена в `deprecated_method`, linter требует `legacy=True` и runtime warning для deprecated bindings. | Done | `pytest tests/core/test_swagger_registry.py tests/core/test_swagger_linter.py`; `make swagger-lint`; `pytest`; `mypy avito`; `ruff check .` |
| 2026-04-29 | Выполнен Этап 4.75: добавлен non-authoritative factory/domain mapping report для `AvitoClient factory -> domain class -> spec candidates`, introspection без создания клиента и список summary/helper methods без direct binding. | Done | `pytest tests/core/test_swagger_factory_map.py tests/core/test_swagger_report.py tests/core/test_swagger_linter.py`; `python scripts/lint_swagger_bindings.py --json --output /tmp/swagger-bindings-report-stage475.json`; `make swagger-lint`; `pytest`; `mypy avito`; `ruff check .` |
| 2026-04-29 | Выполнен Этап 5: расставлены Swagger bindings на все публичные domain operation methods: accounts 8, tariffs 1, ratings 4, messenger 18, promotion 24, ads/autoload 28, orders/delivery/stock 44, jobs 22, cpa/calltracking 13, autoteka 26, realty 7. Coverage report: bound 195, unbound 9, duplicate 0, ambiguous 0. Unbound остались только token operations и альтернативные ветки существующих мульти-режимных методов (`version=1`, `ids`, `extended=True`). | Done | `make swagger-lint`; `poetry run python scripts/lint_swagger_bindings.py --json --output /tmp/swagger-stage5-after.json`; AST-check public domain methods without bindings; `pytest`; `mypy avito`; `ruff check .` |
| 2026-04-29 | Выполнен Этап 6: strict completeness включён в CLI и `make check`; временные multi-binding targets для альтернативных upstream modes и OAuth token operations закрыли coverage до 204/204 bound, 0 unbound, 0 duplicate, 0 ambiguous. | Done | `poetry run python scripts/lint_swagger_bindings.py --json --strict --output /tmp/swagger-stage6.json`; `make swagger-lint`; `make check` |
| 2026-04-29 | Выполнен Этап 6.5: generated reference/coverage переведены на Swagger binding report, docs CI/docs-report используют strict report, оставшиеся ссылки на удалённые docs-report scripts убраны. | Done | `make docs-strict`; `make docs-report`; `rg` по inventory/check_inventory/удалённым docs scripts; manual review generated `site/reference/coverage` и `site/reference/operations` |
| 2026-04-29 | Выполнен Этап 7: linter валидирует `path.<name>`, `query.<name>`, `header.<name>`, `body`/`body.<field>` и `constant.<name>` expressions; class-level factory defaults фильтруются по Swagger operation; исправлены bindings для autoload query/upload и Autoteka token. | Done | `pytest tests/core/test_swagger*.py`; `poetry run python scripts/lint_swagger_bindings.py --json --strict --output /tmp/swagger-stage7.json`; `make swagger-lint`; `mypy avito`; `ruff check avito tests/core/test_swagger_linter.py` |
| 2026-04-29 | Выполнен Этап 8: добавлен `SwaggerFakeTransport`, generated SDK call invocation по discovered bindings, request validation для method/path/path-query-header params/body/content-type, response happy-path mapping, error status mapping для всех Swagger error status categories и deprecated/legacy runtime warning contract. | Done | `poetry run pytest tests/contracts/test_swagger_contracts.py tests/core/test_swagger_registry.py tests/core/test_swagger_linter.py tests/contracts/test_public_surface.py`; `poetry run python scripts/lint_swagger_bindings.py --strict`; `poetry run mypy avito`; `poetry run ruff check avito tests/contracts/test_swagger_contracts.py tests/contracts/test_public_surface.py tests/core/test_swagger_registry.py`; `poetry run pytest`; `make check` |
| 2026-04-29 | Выполнен Этап 9: финальный gate пройден отдельными командами и через `make check`; проверено, что старый markdown inventory не упоминается как источник истины. | Done | `make test`; `make typecheck`; `make lint`; `make swagger-lint`; `make build`; `make check`; `rg` по `inventory`/`check_inventory`/`source of truth` |
| 2026-04-29 | Добавлен новый Этап 10 для устранения несоответствий после выполнения плана: запрет нескольких bindings на один SDK method, schema-aware validation для `body.<field>`, усиление contract tests до полного binding/status coverage. Upstream Swagger mismatch не входит в этап и остаётся отдельной задачей. | Planned | Manual review |
| 2026-04-29 | Выполнен Этап 10.1: multi-binding SDK methods разделены на отдельные discovered targets, stacked decorators запрещены, discovery/linter ловят legacy `__swagger_bindings__`, docs больше не допускают multi-operation SDK methods. | Done | `poetry run pytest tests/core/test_swagger.py tests/core/test_swagger_discovery.py tests/core/test_swagger_linter.py tests/core/test_swagger_report.py`; `poetry run python scripts/lint_swagger_bindings.py --json --strict --output /tmp/swagger-10-1.json`; `jq` check for duplicate `sdk_method`; `make swagger-lint`; `poetry run mypy avito`; `poetry run ruff check avito tests/core docs/site/assets/_gen_reference.py` |
| 2026-04-29 | Выполнен Этап 10.2: `SwaggerRequestBody` хранит content types, top-level schema fields и schema extraction flag; registry извлекает inline/`$ref`/composed object properties; linter проверяет `body.<field>` и выдаёт `SWAGGER_BINDING_BODY_FIELD_NOT_FOUND` / `SWAGGER_BINDING_BODY_SCHEMA_UNSUPPORTED`; bindings приведены к schema-aware expressions. | Done | `poetry run pytest tests/core/test_swagger_registry.py tests/core/test_swagger_linter.py`; `poetry run python scripts/lint_swagger_bindings.py --json --strict --output /tmp/swagger-10-2.json`; `make swagger-lint`; `poetry run mypy avito`; `poetry run ruff check avito tests/core docs/site/assets/_gen_reference.py`; `make check` |
| 2026-04-29 | Выполнен Этап 10.3: contract tests усилены до полного request coverage по 204 discovered bindings и полного error coverage по 639 numeric Swagger error responses; `SwaggerFakeTransport` получил generated success invocation для auth/domain bindings, controlled success payload registry и дополнительные SDK argument builders; исправлены выявленные Swagger request drift в query/header параметрах. | Done | `poetry run pytest tests/contracts/test_swagger_contracts.py`; full verification по 10.4 |
| 2026-04-29 | Выполнен Этап 10.4: пройден полный verification set после усиления contract tests; strict binding report подтверждает 204/204 bound, 0 unbound, 0 duplicate, 0 ambiguous, 0 validation errors. | Done | `poetry run pytest tests/core/test_swagger.py tests/core/test_swagger_discovery.py tests/core/test_swagger_linter.py tests/core/test_swagger_report.py`; `poetry run pytest tests/core/test_swagger_registry.py tests/contracts/test_swagger_contracts.py`; `make swagger-lint`; `poetry run mypy avito`; `poetry run ruff check avito tests/core tests/contracts/test_swagger_contracts.py`; `make docs-strict`; `make check` |
