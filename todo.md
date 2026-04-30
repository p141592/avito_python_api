# Action plan: полный переход на domain architecture v2

## Назначение документа

Этот документ описывает конкретный порядок работ, который должен привести SDK к 100% соответствию `docs/site/explanations/domain-architecture-v2.md` и `STYLEGUIDE.md`.

Финальное состояние:

- все API-домены используют v2 layout;
- все публичные API-методы явно описаны в `domain.py`;
- каждый публичный API-метод имеет ровно один `@swagger_operation(...)`;
- каждый публичный API-метод исполняется через ровно один `OperationSpec`;
- response parsing живёт в `ResponseModel.from_payload()`;
- request/query serialization живёт в request/query dataclass через `to_payload()` / `to_params()`;
- API-домены не содержат legacy `client.py`, `mappers.py`, standalone `enums.py`;
- transport и core не знают о доменных mapper-функциях;
- архитектурные инварианты проверяются автоматически.

Корневой `avito/client.py` остаётся публичным фасадом SDK и не считается legacy domain `client.py`.

## Жёсткие правила миграции

1. Обратная совместимость с domain-level `client.py`, `mappers.py`, standalone `enums.py` не сохраняется.
2. Не добавлять новые legacy adapter-и, deprecated aliases или compatibility exports.
3. Не переносить HTTP-вызовы в модели, mapper-и или transport helpers.
4. Не переносить Swagger contract data в `@swagger_operation(...)`: binding остаётся только адресацией SDK method -> Swagger operation.
5. Не использовать `dict` или `Any` как public return annotation.
6. Не использовать `setattr`, `globals()` или runtime patching для публичных методов.
7. После перевода домена legacy-файлы домена удаляются в том же change set.
8. После каждого домена quality gate должен становиться не хуже: запрещено добавлять новые legacy imports, mapper-based вызовы или unbound public methods.

## Phase 0. Baseline inventory

Цель: получить измеримый baseline до рефакторинга и не потерять API-поверхность.

### 0.1. Зафиксировать список API-доменов

API-домены для перевода:

- `accounts`
- `ads`
- `autoteka`
- `cpa`
- `jobs`
- `messenger`
- `orders`
- `promotion`
- `ratings`
- `realty`
- `tariffs`

Не считать API-доменами:

- `auth`
- `core`
- `summary`
- `testing`
- корневой `avito/client.py`

### 0.2. Снять метрики текущего состояния

Добавить временный или постоянный скрипт inventory report, который выводит:

- domain-level legacy files: `avito/<domain>/client.py`, `mappers.py`, `enums.py`;
- imports из `avito.<domain>.client`, `avito.<domain>.mappers`, `avito.<domain>.enums`;
- использования `request_public_model`;
- использования `mapper=`;
- количество public methods в `avito/<domain>/domain.py`;
- количество discovered Swagger bindings по доменам;
- количество Swagger operations по доменам;
- домены с binary, multipart, pagination, idempotency, empty response.

Минимальные команды baseline:

```bash
find avito -mindepth 2 -maxdepth 2 \( -name client.py -o -name mappers.py -o -name enums.py \) | sort
rg "request_public_model|mapper=|from avito\..*\.(client|mappers|enums)|import avito\..*\.(client|mappers|enums)" avito tests docs
poetry run python scripts/lint_swagger_bindings.py --json --strict --output swagger-bindings-report.json
```

### 0.3. Создать progress table

Phase 0 baseline снят командой:

```bash
poetry run python scripts/inventory_architecture.py --json --output architecture-inventory-report.json
poetry run python scripts/lint_swagger_bindings.py --json --strict --output swagger-bindings-report.json
```

Общий baseline:

- API-доменов: 11;
- API-domain legacy files: 33;
- legacy imports: 70;
- `request_public_model` / `mapper=` hits: 321;
- public methods в `avito/<domain>/domain.py`: 201;
- Swagger operations всего: 204;
- Swagger operations в API-доменах Phase 0: 200;
- discovered Swagger bindings в API-доменах Phase 0: 200.

Поддерживать таблицу до завершения миграции.

| Domain | Legacy files | Public methods | Swagger bindings | Swagger ops | Edge cases | Status |
|---|---:|---:|---:|---:|---|---|
| tariffs | 0 | 1 | 1 | 1 | - | done |
| accounts | 0 | 8 | 8 | 8 | empty_response | done |
| ratings | 0 | 4 | 4 | 4 | pagination | done |
| realty | 0 | 7 | 7 | 7 | empty_response | done |
| cpa | 0 | 14 | 14 | 14 | empty_response | done |
| messenger | 0 | 18 | 18 | 18 | empty_response, multipart, pagination | done |
| jobs | 0 | 26 | 25 | 25 | empty_response, pagination | done |
| autoteka | 0 | 26 | 26 | 26 | pagination | done |
| promotion | 0 | 24 | 24 | 24 | empty_response | done |
| ads | 0 | 28 | 28 | 28 | empty_response, pagination | done |
| orders | 0 | 45 | 45 | 45 | binary, pagination | done |

## Phase 1. Implement v2 core MVP

Цель: создать минимальный core, на котором можно перевести первые домены без временных adapter-ов.

Статус: выполнено. Добавлены `ApiModel`, `RequestModel`, `api_field`, `JsonReader`,
`OperationSpec`, `OperationExecutor`, `EmptyResponse`, `DomainObject._execute()`;
`_resolve_user_id` больше не импортирует `avito.accounts.client`.

Проверено:

```bash
poetry run pytest tests/core/
poetry run mypy avito/core avito/testing
poetry run ruff check avito/core tests/core
```

### 1.1. Добавить `avito/core/models.py`

Реализовать:

- `ApiModel(SerializableModel)`;
- `RequestModel`;
- общий serializer для request/query dataclass;
- `to_payload()`;
- `to_params()`;
- исключение `None`-полей, если это нужно контракту API;
- поддержку вложенных request-моделей, list, dict, enum, date/datetime.

Тесты:

- dataclass -> payload с API field names;
- dataclass -> params;
- вложенные dataclass-и;
- enum serialization;
- пропуск `None`;
- отсутствие `raw_payload` в public serialization.

### 1.2. Добавить `avito/core/fields.py`

Реализовать:

- `api_field("apiName")`;
- metadata для request/query serializer;
- поддержку default/default_factory, если используется dataclasses.

Тесты:

- Python field name отличается от API field name;
- metadata не ломает frozen/slots dataclass.

### 1.3. Добавить `avito/core/payload.py`

Реализовать `JsonReader`:

- `expect_mapping(payload)`;
- `expect_list(payload)`;
- `required_str`, `optional_str`;
- `required_int`, `optional_int`;
- `required_float`, `optional_float`;
- `required_bool`, `optional_bool`;
- `required_datetime`, `optional_datetime`;
- `enum`;
- `mapping`;
- `list`;
- fallback keys;
- Russian-only `ResponseMappingError` messages.

Тесты:

- wrong payload type;
- missing required field;
- fallback key order;
- bool не принимается как int;
- unknown enum fallback;
- datetime parsing.

### 1.4. Добавить `avito/core/operations.py`

Реализовать MVP:

- `OperationSpec`;
- `OperationExecutor`;
- path rendering;
- `RequestContext` creation from operation name;
- path params;
- query params;
- JSON body;
- custom headers;
- idempotency key;
- response kinds: `json`, `empty`, `binary`;
- response parsing through `response_model.from_payload()`;
- typed empty result model или explicit sentinel для `204 No Content`.

`OperationSpec` MVP fields:

- `name`;
- `method`;
- `path`;
- `query_model`;
- `request_model`;
- `response_model`;
- `response_kind`;
- `content_type`;
- `requires_auth`;
- `retry_policy` или `retry_mode`;

Тесты:

- path rendering encodes path params;
- query model вызывает `to_params()`;
- request model вызывает `to_payload()`;
- response model вызывает `from_payload()`;
- empty response не пытается читать JSON;
- binary response использует transport binary path;
- idempotency key передаётся в transport;
- headers передаются в transport.

### 1.5. Подключить executor к `DomainObject`

Добавить в `DomainObject` protected helper:

```python
def _execute(...): ...
```

Helper должен:

- принимать `OperationSpec`;
- принимать path/query/request/header/idempotency arguments;
- делегировать в `OperationExecutor`;
- не знать о конкретных доменах Avito.

### 1.6. Убрать legacy dependency из `_resolve_user_id`

Сейчас `_resolve_user_id` не должен зависеть от `avito.accounts.client`.

Сделать:

- заменить legacy import на v2-compatible resolver;
- после перевода `accounts` использовать account domain operation;
- до перевода `accounts` допускается узкий internal resolver без mapper compatibility только как временная часть Phase 1/2;
- покрыть сценарии: explicit `user_id`, configured `user_id`, fallback через profile, profile without `user_id`.

Definition of Done Phase 1:

```bash
poetry run pytest tests/core/
poetry run mypy avito/core avito/testing
poetry run ruff check avito/core tests/core
```

## Phase 2. Add architecture-lint

Цель: автоматически запретить возврат к legacy architecture.

Статус: выполнено. Добавлен `scripts/lint_architecture.py`, Makefile target
`architecture-lint`, focused tests `tests/core/test_architecture_lint.py`.
Migration allowlist уменьшен после перевода `tariffs`, `accounts`, `ratings`.

### 2.1. Добавить `scripts/lint_architecture.py`

Линтер должен использовать AST там, где regex ненадёжен.

Проверки файловой структуры:

- запрещены `avito/<api-domain>/client.py`;
- запрещены `avito/<api-domain>/mappers.py`;
- запрещены `avito/<api-domain>/enums.py`;
- запрещены underscore-prefixed варианты тех же файлов:
  `_client.py`, `_mappers.py`, `_mapping.py`, `_enums.py` —
  чтобы переименование не давало обхода checks (Phase 2 follow-up);
- запрещены imports из таких underscore-prefixed модулей;
- не запрещать `avito/client.py`;
- не запрещать `avito/core/enums.py`;
- не запрещать `avito/auth/enums.py`, если auth остаётся не API-доменом.

Regex/token checks:

- `request_public_model`;
- `mapper=`;
- imports из `avito.<api-domain>.client`;
- imports из `avito.<api-domain>.mappers`;
- imports из `avito.<api-domain>.enums`.

AST checks:

- public domain method без `@swagger_operation(...)`;
- public API method без `_execute(...)` или другого approved `OperationExecutor` call;
- public return annotation `dict`;
- public return annotation `Any`;
- calls to `setattr(...)`;
- calls to `globals(...)`;
- response model class без `from_payload()`;
- request/query model без `to_payload()` или `to_params()`, если она используется в `OperationSpec`.

### 2.2. Добавить Makefile target

```make
architecture-lint:
	poetry run python scripts/lint_architecture.py
```

Временно разрешить allowlist только для ещё не переведённых доменов, но allowlist должен уменьшаться после каждого домена.

### 2.3. Подключить к quality gate

После перевода первых эталонных доменов добавить:

```make
check: swagger-update test typecheck lint swagger-lint architecture-lint build
```

Definition of Done Phase 2:

```bash
make architecture-lint
poetry run pytest tests/core/test_architecture_lint.py
```

## Phase 3. Convert reference domains

Цель: получить рабочий шаблон перевода домена и доказать, что core покрывает реальные операции.

## Method migration checklist

Для каждого public API method:

1. Найти Swagger operation в `docs/avito/api/*.json`.
2. Проверить текущий `@swagger_operation(...)`.
3. Создать `OperationSpec` с тем же method/path.
4. Перенести path params в явные arguments executor-а.
5. Перенести query params в query dataclass.
6. Перенести JSON body в request dataclass.
7. Перенести response mapping в `ResponseModel.from_payload()`.
8. Перенести enum-ы рядом с моделями.
9. Заменить legacy client call на `self._execute(...)`.
10. Удалить legacy mapper function для метода.
11. Добавить тест request/query serialization.
12. Добавить тест response parsing.
13. Добавить тест domain method -> operation execution.
14. Проверить совпадение method/path в `@swagger_operation(...)` и `OperationSpec`.

### 3.1. Convert `tariffs`

Цель: минимальный эталон JSON GET.

Статус: выполнено.

Actions:

- создать `avito/tariffs/operations.py`;
- перенести HTTP contract из `TariffsClient.get_tariff_info`;
- перенести `TariffLevel` из `enums.py` в `models.py`;
- сделать `TariffContractInfo(ApiModel)`;
- сделать `TariffInfo(ApiModel)`;
- перенести `map_tariff_info` в `TariffInfo.from_payload()`;
- заменить `TariffsClient(self.transport).get_tariff_info()` на `self._execute(...)`;
- удалить `avito/tariffs/client.py`;
- удалить `avito/tariffs/mappers.py`;
- удалить `avito/tariffs/enums.py`;
- обновить exports в `avito/tariffs/__init__.py`;
- обновить тесты и docs imports.

Verification:

```bash
poetry run pytest tests/domains/tariffs/
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

### 3.2. Convert `accounts`

Цель: снять core dependency на legacy account client и закрыть user/account patterns.

Статус: выполнено.

Actions:

- создать `avito/accounts/operations.py`;
- перенести account/profile/balance/employee/phone operations;
- перенести enum-ы в `models.py`;
- перенести mapper logic в `from_payload()`;
- перевести request/query dataclass-и на `RequestModel`;
- переписать `accounts/domain.py` на `OperationSpec`;
- заменить `_resolve_user_id` fallback на v2 account operation;
- удалить `accounts/client.py`, `accounts/mappers.py`, `accounts/enums.py`;
- обновить tests for `_resolve_user_id`.

Verification:

```bash
poetry run pytest tests/domains/accounts/ tests/core/test_domain.py
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

### 3.3. Convert `ratings`

Цель: эталон write/idempotency/list/delete операций.

Статус: выполнено.

Actions:

- создать `avito/ratings/operations.py`;
- перенести GET/POST/DELETE operations;
- перенести enum-ы в `models.py`;
- перенести mapper logic в `from_payload()`;
- перевести request/query dataclass-и на `RequestModel`;
- переписать `ratings/domain.py` на `OperationSpec`;
- покрыть idempotency key;
- покрыть validation;
- удалить `ratings/client.py`, `ratings/mappers.py`, `ratings/enums.py`;
- обновить docs imports.

Verification:

```bash
poetry run pytest tests/domains/ratings/
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

### 3.4. Freeze reference pattern

После `tariffs`, `accounts`, `ratings`:

Статус: выполнено. Эталонный паттерн зафиксирован в
`docs/site/explanations/domain-architecture-v2.md`, `STYLEGUIDE.md` и
`docs/site/explanations/swagger-binding-subsystem.md`.

- обновить `docs/site/explanations/domain-architecture-v2.md` фактическими сигнатурами core API;
- обновить `STYLEGUIDE.md`: temporary compatibility больше не описывать как поддерживаемый режим;
- обновить `docs/site/explanations/swagger-binding-subsystem.md`, если добавлена проверка `OperationSpec`;
- добавить короткий domain conversion recipe в docs или dev notes;
- убрать переведённые домены из architecture-lint allowlist.

Verification:

```bash
make docs-strict
make check
```

## Phase 4. Convert medium domains by edge case

Цель: расширить покрытие executor-а через реальные edge cases.

### 4.1. Convert `realty`

Focus:

- query/body/path combinations;
- date/range request models;
- nested request serialization.

Actions:

- создать `realty/operations.py`;
- перенести enum-ы в `models.py`;
- перенести mapper logic в `from_payload()`;
- удалить legacy files;
- покрыть date/range serialization tests.

### 4.2. Convert `cpa`

Focus:

- binary/audio edge cases;
- complaints;
- call tracking;
- body-only requests.

Actions:

- создать `cpa/operations.py`;
- добавить/доработать binary response support в executor, если MVP недостаточен;
- перенести mapper logic в `from_payload()`;
- удалить legacy files;
- покрыть binary/audio response tests.

### 4.3. Convert `messenger`

Focus:

- messages;
- uploads;
- webhooks;
- multipart.

Actions:

- создать `messenger/operations.py` или `messenger/operations/`;
- добавить/доработать multipart request support;
- перенести upload request models;
- перенести webhook models;
- удалить legacy files;
- покрыть multipart tests.

### 4.4. Convert `jobs`

Focus:

- справочники;
- lists;
- nested models.

Actions:

- создать `jobs/operations.py`;
- перенести nested parsing в `from_payload()`;
- удалить legacy files;
- покрыть list/nested model tests.

Verification after each domain:

```bash
poetry run pytest tests/domains/<domain>/
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

## Phase 5. Convert complex domains

Цель: перевести самые объёмные домены, дробя models/operations по подсекциям там, где монолит становится трудно поддерживать.

### 5.1. Convert `autoteka`

Статус: выполнено.

Focus:

- nested parsing;
- report/scoring/monitoring models;
- response variants.

Target layout:

```text
avito/autoteka/
  __init__.py
  domain.py
  operations.py        # or operations/
  models.py            # or models/
```

### 5.2. Convert `promotion`

Статус: выполнено.

Focus:

- service dictionaries;
- order/status variants;
- campaign/stat/budget models;
- action result responses.

Consider split:

```text
avito/promotion/
  operations/
    __init__.py
    services.py
    orders.py
    bids.py
    campaigns.py
  models/
    __init__.py
    services.py
    orders.py
    bids.py
    campaigns.py
```

### 5.3. Convert `ads`

Статус: выполнено.

Focus:

- autoload;
- upload;
- reports;
- stats;
- services;
- item-level actions.

Consider split:

```text
avito/ads/
  operations/
    __init__.py
    items.py
    autoload.py
    reports.py
    stats.py
    services.py
  models/
    __init__.py
    items.py
    autoload.py
    reports.py
    stats.py
    services.py
```

### 5.4. Convert `orders`

Статус: выполнено. Удалены `_client.py`, `_mapping.py`, `_enums.py`;
публичные методы выполняются через `orders/operations.py`, enum-ы и parsing перенесены
в `orders/models.py`, `architecture-lint` проходит без migration allowlist.

Focus:

- labels;
- delivery;
- sandbox;
- stock;
- binary labels;
- largest operation surface.

Target split:

```text
avito/orders/
  __init__.py
  domain.py
  operations/
    __init__.py
    orders.py
    labels.py
    delivery.py
    sandbox.py
    stock.py
  models/
    __init__.py
    orders.py
    labels.py
    delivery.py
    sandbox.py
    stock.py
```

Verification after each domain:

```bash
poetry run pytest tests/domains/<domain>/
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

## Phase 6. Remove legacy core and transport surface

Цель: после перевода всех доменов удалить инфраструктуру, которая существовала только для legacy architecture.

Статус: выполнено. Удалены `avito/core/mapping.py` и
`Transport.request_public_model(...)`; `architecture-lint` больше не содержит
allowlist для legacy core, inventory показывает `legacy_usage_count: 0`.

Actions:

- удалить `avito/core/mapping.py`;
- удалить `Transport.request_public_model(..., mapper=...)`;
- удалить mapper-related imports из transport/core;
- удалить legacy mapper helpers;
- удалить tests legacy clients/mappers;
- удалить compatibility exports из all domain `__init__.py`;
- обновить `avito/core/__init__.py` exports;
- проверить, что transport не импортирует доменные модели;
- проверить, что core не содержит domain-specific enum, fallback keys или бизнес-валидацию;
- убрать все architecture-lint allowlist entries.

Verification:

```bash
rg "request_public_model|mapper=" avito tests docs
rg "from avito\..*\.(client|mappers|enums)|import avito\..*\.(client|mappers|enums)" avito tests docs
find avito -mindepth 2 -maxdepth 2 \( -name client.py -o -name mappers.py -o -name enums.py \) | sort
make check
```

Expected:

- `rg` commands return no API-domain legacy hits;
- `find` returns no files for API domains;
- `avito/client.py`, `avito/core/enums.py`, `avito/auth/enums.py` are handled according to their non-domain role.

## Phase 7. Swagger and architecture enforcement

Цель: сделать v2 не только реализованной, но и постоянно проверяемой.

Статус: выполнено. `lint_swagger_bindings --strict` проверяет полноту 204/204
Swagger bindings, duplicate/missing/unbound состояния, соответствие
`@swagger_operation(...)` реальному `OperationSpec`, отсутствие лишних
API-domain `OperationSpec` без публичного binding, а также совпадение
HTTP method/path между Swagger operation и исполняемым `OperationSpec`.

Actions:

- расширить `scripts/lint_swagger_bindings.py` или добавить отдельную проверку, что each public API method has matching `OperationSpec`;
- проверить совпадение method/path между `@swagger_operation(...)` и `OperationSpec`;
- проверить отсутствие `OperationSpec` без public Swagger binding, кроме явно internal operations;
- проверить discovered bindings count against Swagger operations count;
- убедиться, что `make swagger-lint` падает на duplicate/missing/unbound methods.

Swagger Definition of Done:

- обнаружено ровно 204 bindings для 204 Swagger operations;
- нет duplicate bindings;
- нет missing bindings;
- нет unbound public API methods для Avito operations;
- нет лишних public `OperationSpec` без Swagger binding;
- `operation_id`, `method`, `path`, `spec` валидируются автоматически;
- method/path в binding и `OperationSpec` совпадают;
- каждый discovered SDK method соответствует ровно одной Swagger operation;
- каждая Swagger operation соответствует ровно одному discovered SDK method.

Verification:

```bash
make swagger-lint
poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py
make architecture-lint
```

## Phase 8. Documentation and reference

Цель: документация должна описывать фактическую v2 implementation, а не migration path.

Статус: выполнено. Обновлены architecture explanations, v2 domain architecture,
Swagger binding subsystem, testing/transport explanations и `STYLEGUIDE.md`;
`make docs-strict` проходит.

Actions:

- обновить `docs/site/explanations/domain-architecture-v2.md`;
- обновить `STYLEGUIDE.md`;
- обновить `docs/site/explanations/swagger-binding-subsystem.md`;
- удалить упоминания поддерживаемых legacy clients/mappers/enums;
- перегенерировать reference docs;
- обновить examples/how-to;
- проверить, что public method docstrings reference-ready;
- проверить, что generated reference не требует ручных исключений.

Docs Definition of Done:

- `domain-architecture-v2.md` описывает фактически implemented API;
- `STYLEGUIDE.md` требует обязательный v2 для всех API-доменов;
- reference docs сгенерированы из актуальной package surface;
- examples/how-to не ссылаются на удалённые clients/mappers/enums;
- docs не описывают compatibility/migration path как поддерживаемый режим;
- `make docs-strict` проходит.

Verification:

```bash
make docs-strict
```

## Domain Definition of Done

Домен считается переведённым только когда выполнены все пункты:

- удалены `avito/<domain>/client.py`, `avito/<domain>/mappers.py`, `avito/<domain>/enums.py`;
- `domain.py` не импортирует legacy clients/mappers/enums;
- `__init__.py` не экспортирует legacy clients/mappers/enums;
- все enum-ы перенесены в `models.py` или `models/`;
- все response-модели наследуют `ApiModel`;
- все response-модели реализуют `from_payload()`;
- все request/query модели наследуют `RequestModel` или явно реализуют тот же contract;
- все HTTP details находятся только в `operations.py` или `operations/`;
- все public API methods имеют reference-ready docstring;
- все public API methods имеют ровно один `@swagger_operation(...)`;
- все public API methods исполняются через `OperationSpec`;
- public methods возвращают only typed SDK models;
- нет public return `dict`;
- нет public return `Any`;
- нет raw payload в public SDK contract;
- tests покрывают happy path;
- tests покрывают validation;
- tests покрывают request/query serialization;
- tests покрывают response parsing;
- tests покрывают binary/multipart/pagination/idempotency, если применимо;
- `make architecture-lint` не содержит allowlist entry для домена.

Minimum verification after each domain:

```bash
poetry run pytest tests/domains/<domain>/
make swagger-lint
make architecture-lint
poetry run mypy avito
poetry run ruff check .
```

## Core Definition of Done

v2 core готов, когда:

- есть `ApiModel`;
- есть `RequestModel`;
- есть `JsonReader`;
- есть `api_field`;
- есть `OperationSpec`;
- есть `OperationExecutor`;
- `DomainObject._execute()` delegates to `OperationExecutor`;
- executor поддерживает JSON body;
- executor поддерживает query params;
- executor поддерживает path params;
- executor поддерживает headers;
- executor поддерживает idempotency key;
- executor поддерживает `json`, `empty`, `binary`, `multipart` modes;
- executor поддерживает pagination strategy или documented pagination adapter;
- path rendering покрыт тестами;
- request/query serialization покрыта тестами;
- response parsing через `from_payload()` покрыт тестами;
- transport не знает о доменных моделях;
- transport не знает о mapper-функциях;
- core не импортирует API-domain `client.py`, `mappers.py`, `enums.py`.

## Architecture-Lint Definition of Done

`architecture-lint` готов, когда он автоматически проверяет:

- отсутствие API-domain `client.py`;
- отсутствие API-domain `mappers.py`;
- отсутствие API-domain `enums.py`;
- отсутствие API-domain `_client.py`, `_mappers.py`, `_mapping.py`, `_enums.py`;
- отсутствие `mapper=`;
- отсутствие `request_public_model`;
- отсутствие legacy imports;
- наличие `from_payload()` у public response models;
- наличие `@swagger_operation(...)` у public API methods;
- наличие `OperationSpec` у public API methods;
- совпадение method/path между Swagger binding и `OperationSpec`;
- отсутствие `dict` и `Any` в public return annotations;
- отсутствие runtime method injection;
- отсутствие allowlist для полностью переведённых доменов.

## Final Acceptance

Переход завершён только когда проходят:

```bash
make check
make docs-strict
make swagger-lint
make architecture-lint
```

И дополнительные проверки для API-domain legacy surface возвращают пустой результат:

```bash
rg "request_public_model|mapper=" avito tests docs
rg "from avito\..*\.(client|mappers|enums)|import avito\..*\.(client|mappers|enums)" avito tests docs
find avito -mindepth 2 -maxdepth 2 \( -name client.py -o -name mappers.py -o -name enums.py \) | sort
```

Дополнительно:

- все 204 Swagger operations покрыты;
- все public methods доступны через `AvitoClient` factories;
- все public methods типизированы;
- все public models сериализуются через `to_dict()` и `model_dump()`;
- full reference generation проходит без ручных исключений;
- `architecture-lint` не содержит migration allowlist для API-доменов.
