# Swagger Schema Contract Coverage

## Контекст для восстановления

Задача: добавить в SDK строгую проверку полного соответствия локальным Swagger/OpenAPI спецификациям Авито. Нельзя замалчивать пробелы покрытия, использовать allowlist/skip для непокрытых контрактов или сохранять обратную совместимость ценой расхождения со Swagger.

Целевой инвариант:

- каждая Swagger operation имеет ровно один SDK binding;
- каждый binding исполняет ровно один `OperationSpec`;
- каждый Swagger JSON `requestBody` имеет явный `OperationSpec.request_model`;
- каждый Swagger JSON success response имеет явный `OperationSpec.response_model`;
- каждый Swagger JSON error response имеет явный `OperationSpec.error_models[status]` или общий typed error model;
- все JSON request/success/error payloads проверяются по field key и JSON type;
- unsupported Swagger schema shape является падающим тестом, а не пропуском.

Текущий важный статус: инфраструктурный слой уже добавлен. `SwaggerRegistry` строит normalized schema tree, `OperationSpec` получил `error_models`, добавлен общий `ApiErrorPayload`, добавлен `avito/testing/swagger_schema.py`, а контрактные тесты теперь вскрывают реальные payload mismatches. Полнота моделей и parsing schemas уже проходят, но строгие schema payload tests сейчас красные и являются backlog исправлений.

Проверки, которые уже проходили после инфраструктурного шага:

```bash
poetry run python scripts/lint_swagger_bindings.py --strict
poetry run mypy avito
poetry run ruff check avito tests/contracts/test_swagger_contracts.py
poetry run pytest tests/domains/accounts/test_accounts.py tests/core/test_swagger_registry.py tests/contracts/test_swagger_contracts.py::test_swagger_operation_specs_cover_all_declared_json_bodies
```

Команды для получения текущего backlog:

```bash
poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short
poetry run pytest tests/contracts/test_swagger_contracts.py -k "success_response_models_accept or error_responses_preserve" --tb=short
```

Последний известный baseline:

- `85` request-body mismatches;
- `61` success/error response mismatches.

## Action Plan

### 1. Зафиксировать красный baseline

Сохранить текущий список падений как рабочий backlog:

```bash
poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short
poetry run pytest tests/contracts/test_swagger_contracts.py -k "success_response_models_accept or error_responses_preserve" --tb=short
```

Цель: закрывать домены пачками и видеть прогресс, а не спорить с тестами по одному.

### 2. Сначала закрыть request-body mismatches

Request fixes обычно локальные: public args, `method_args`, request dataclass, `to_payload()`.

Порядок доменов:

1. `accounts`
2. `ads`
3. `cpa`
4. `autoteka`
5. `jobs`
6. `messenger`
7. `promotion`
8. `ratings`
9. `realty`
10. `orders`
11. `delivery`

### 3. Цикл исправления каждой failing request operation

Для каждой операции:

1. Открыть Swagger schema операции в `docs/avito/api/*.json`.
2. Сравнить с фактическим `request.json_body` из `SwaggerFakeTransport`.
3. Если поле required в Swagger, сделать его required в public method или гарантированно выводимым из состояния домена.
4. Поправить `to_payload()` на точные Swagger keys.
5. Поправить типы публичных аргументов и request dataclass.
6. Добавить/исправить `@swagger_operation(method_args=...)`, чтобы generated contract call был валидным.
7. Обновить доменные тесты и docs snippets, если public signature изменилась.

### 4. Первый batch: `ads` requests

Закрыть:

- `PUT /core/v1/accounts/{user_id}/items/{item_id}/vas`: `vas_id`, не `codes`;
- `PUT /core/v2/items/{item_id}/vas`: `slugs`, не `codes`;
- `PUT /core/v2/accounts/{user_id}/items/{item_id}/vas_packages`: `package_id`;
- stats endpoints: required `dateFrom/dateTo`, а для v2 также `grouping`, `limit`, `metrics`, `offset`;
- spendings: required `dateFrom/dateTo/grouping/spendingTypes`.

### 5. Второй batch: `cpa` requests

Закрыть:

- complaints: Swagger требует `message`, SDK сейчас использует `reason`;
- `callsByTime`, `chatsByTime`, `phonesInfoFromChats`: добавить required `limit/offset/dateTimeFrom`;
- `balanceInfo`: Swagger описывает body type `string`; SDK сейчас отправляет `{}`.

### 6. Третий batch: `autoteka` requests

Закрыть:

- `vehicleId` и `itemId` как `string`, не `integer`;
- monitoring bucket add/remove: точные Swagger keys вместо `vehicles`;
- `valuation/by-specification`: required wrapper `specification`;
- `get-leads`: required `subscriptionId`;
- `catalogs/resolve`: required `fieldsValueIds`.

### 7. Средние домены

После первых трех batches перейти к:

- `jobs`: ids как strings, webhook/vacancy required fields;
- `messenger`: blacklist/message/image payload keys;
- special offers: required nested fields;
- `promotion`: cancel/apply/order payload shape;
- `ratings`: answer request shape;
- `realty`: prices/intervals/base/booking wrappers.

### 8. Крупные домены в конце

`orders` и `delivery` оставить после стабилизации подхода:

- там много nested objects;
- больше шансов, что public API сейчас намеренно упрощен, но целевой контракт требует приводить SDK к Swagger;
- фиксировать по operation groups: labels, tracking, parcel, sandbox tariffs, announcements.

### 9. После request-body green перейти к success responses

Для каждого failing success response:

1. Сгенерированный Swagger payload считать source of truth.
2. `from_payload()` должен его принять.
3. Если модель ожидает другой wrapper (`items`, `result`, `success.result`) - добавить корректный Swagger path.
4. Если публичная модель слишком бедная, расширить dataclass typed fields.
5. Если response реально array, `from_payload()` должен читать array, а не только object.

### 10. Потом error responses

Цель:

- generated error payload валиден по Swagger;
- transport поднимает правильный exception;
- `exception.payload == swagger_payload`;
- `message/error_code/details` извлекаются без ломки схемы.

Если schema error payload нестандартная, исправлять общий parser `_extract_message/_extract_error_code/_extract_error_details`, но не терять raw `payload`.

### 11. Усилить lint после стабилизации

Перенести часть runtime contract правил в `swagger_linter`:

- JSON requestBody требует `request_model`;
- JSON success response требует `response_model`;
- JSON error response требует `error_models`;
- schema must parse.

### 12. Включить строгие schema tests в gate

Когда все green:

- добавить новые тесты в `make swagger-coverage`;
- затем убедиться, что `make check` проходит.

### 13. Финальная проверка

Минимум:

```bash
poetry run pytest tests/contracts/test_swagger_contracts.py
poetry run pytest tests/domains/
poetry run python scripts/lint_swagger_bindings.py --strict
poetry run mypy avito
poetry run ruff check .
```

Финально:

```bash
make check
```

## Changelog / Статус выполнения

### 2026-05-01

- Этап 1 выполнен: красный baseline зафиксирован в `swagger_contract_backlog.md`.
- Подтверждено текущими прогонами:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `85 failed, 119 passed`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k "success_response_models_accept or error_responses_preserve" --tb=short` - `61 failed, 782 passed`.
- Добавлена инфраструктура strict Swagger schema contracts.
- `SwaggerRegistry` расширен normalized JSON schema tree для request/response/error bodies.
- `OperationSpec` расширен `error_models`.
- Добавлен общий typed wrapper `ApiErrorPayload`.
- Добавлен `avito/testing/swagger_schema.py` с generator/validator по key/type.
- Добавлены контрактные тесты на:
  - полноту моделей для всех JSON bodies;
  - соответствие actual request body Swagger schema;
  - прием Swagger-shaped success payload через SDK response models;
  - сохранение Swagger-shaped error payload в SDK exceptions.
- Закрыты начальные missing model gaps:
  - 3 missing `request_model`;
  - 7 missing `response_model`;
  - JSON error responses покрыты общим typed error model.
- Исправлен `accounts.get_operations_history()`:
  - `date_from` и `date_to` стали required;
  - payload теперь отправляет `dateTimeFrom/dateTimeTo` по Swagger;
  - обновлены domain test и docs snippet.
- Проверено:
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass;
  - `poetry run mypy avito` - pass;
  - `poetry run ruff check avito tests/contracts/test_swagger_contracts.py` - pass;
  - targeted registry/model-coverage/accounts tests - pass.
- Оставшийся backlog:
  - `85` request-body mismatches;
  - `61` success/error response mismatches.
- Рекомендуемый следующий шаг: начать с `ads` request batch.

### 2026-05-01 / Этап 2 partial

- Начато закрытие request-body mismatches.
- Закрыт `accounts` request mismatch:
  - `POST /listItemsByEmployeeIdV1` теперь отправляет `employeeId/categoryId/lastItemId` по Swagger;
  - `category_id` стал обязательным публичным аргументом.
- Закрыт `ads` request batch:
  - legacy VAS v1 отправляет `vas_id`;
  - VAS v2 отправляет `slugs`;
  - VAS package отправляет `package_id`;
  - stats/calls/spendings request models отправляют обязательные Swagger поля периода, grouping/limit/metrics/offset/spendingTypes.
- Обновлены доменные тесты, model/client contract tests, README/how-to snippets и `CHANGELOG.md` для измененных публичных сигнатур.
- Проверено:
  - `poetry run pytest tests/domains/accounts/test_accounts.py tests/domains/ads/test_ads.py tests/domains/promotion/test_promotion.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py` - pass;
  - `poetry run ruff check ...` по измененным файлам - pass;
  - `poetry run mypy ...` по измененным source-файлам - pass;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `77 failed, 127 passed`.
- Request-body backlog уменьшен с `85` до `77`.
- Закрыт `cpa` request batch:
  - complaints отправляют `message`;
  - `balanceInfo` отправляет JSON string `"{}"` по Swagger;
  - `callsByTime`, `chatsByTime`, `phonesInfoFromChats` отправляют обязательные `dateTimeFrom`, `limit`, `offset`/`limit`.
- Request-body backlog дополнительно уменьшен до `69 failed, 135 passed`.
- Следующий практичный шаг: закрыть маленькие request groups (`autoload`, `stock`, `trx-promo`, `autostrategy`) или перейти к `autoteka` по исходному порядку плана.

### 2026-05-01 / Этап 3

- Закрыт `autoteka` request batch:
  - monitoring bucket add/remove отправляют `data`;
  - `vehicleId` и external `itemId` генерируются как JSON strings;
  - `valuation/by-specification` отправляет required wrapper `specification`;
  - `get-leads` требует `subscriptionId`;
  - `catalogs/resolve` отправляет `fieldsValueIds`.
- Обновлены доменные/model tests и `CHANGELOG.md` для измененной публичной сигнатуры `get_leads(subscription_id=...)`.
- Проверено:
  - `poetry run pytest tests/domains/autoteka/test_autoteka.py tests/contracts/test_model_contracts.py` - pass;
  - `poetry run ruff check avito/autoteka avito/testing/swagger_fake_transport.py tests/domains/autoteka/test_autoteka.py tests/contracts/test_model_contracts.py` - pass;
  - `poetry run mypy avito/autoteka avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `59 failed, 145 passed`.
- Request-body backlog уменьшен с `69` до `59`.
- Следующий практичный шаг: закрыть маленькие request groups (`autoload`, `stock`, `trx-promo`, `autostrategy`) или перейти к `jobs`.

### 2026-05-02 / Этап 4

- Закрыты маленькие request groups:
  - `autoload`: v2 profile save отправляет `autoload_enabled`, `report_email`, `schedule`, `feeds_data`; legacy v1 profile save отправляет `autoload_enabled`, `report_email`, `schedule`, `upload_url`;
  - `stock`: info request отправляет `item_ids` и опциональный `strong_consistency`;
  - `trx-promo`: cancel request отправляет `itemIDs`;
  - `autostrategy`: update/stop bindings генерируют `campaignId` и `version`.
- Обновлен `SwaggerFakeTransport` для генерации валидных значений сложных body bindings этого batch.
- Проверено:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `53 failed, 151 passed`;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass;
  - `poetry run pytest tests/domains/ads/test_ads.py tests/domains/orders/test_orders.py tests/domains/promotion/test_promotion.py tests/contracts/test_model_contracts.py` - pass;
  - `poetry run ruff check avito/ads avito/orders avito/promotion avito/testing/swagger_fake_transport.py tests/domains/ads/test_ads.py tests/domains/orders/test_orders.py tests/domains/promotion/test_promotion.py tests/contracts/test_model_contracts.py` - pass;
  - `poetry run mypy avito/ads avito/orders avito/promotion avito/testing/swagger_fake_transport.py` - pass.
- Request-body backlog уменьшен с `59` до `53`.
- Следующий практичный шаг: перейти к `jobs` request batch.
