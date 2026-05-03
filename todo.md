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

### 2026-05-02 / Этап 5

- Закрыт `jobs` request batch:
  - `applications/apply_actions` и `applications/get_by_ids` отправляют строковые ids;
  - `applications/webhook` требует и отправляет `secret`;
  - v2 vacancy create/update отправляют обязательный `billing_type`;
  - v1 vacancy create отправляет обязательные `name`, `description`, `billing_type`, `business_area`, `employment`, `schedule`, `experience`;
  - v1 vacancy update отправляет обязательный `billing_type`;
  - vacancy statuses отправляют UUID string ids.
- Разделены request-модели v1/v2 вакансий, обновлены domain tests, how-to snippet и `CHANGELOG.md` для измененных публичных сигнатур.
- Проверено:
  - `poetry run pytest tests/domains/jobs/test_jobs.py` - pass;
  - `poetry run pytest tests/domains/jobs/test_jobs.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py` - pass;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `45 failed, 159 passed`;
  - `poetry run mypy avito/jobs avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run ruff check avito/jobs avito/testing/swagger_fake_transport.py tests/domains/jobs/test_jobs.py` - pass;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass.
- Request-body backlog уменьшен с `53` до `45`.
- Следующий практичный шаг: перейти к `messenger` request batch.

### 2026-05-02 / Этап 6

- Закрыт `messenger` request batch:
  - blacklist отправляет Swagger wrapper `users[].user_id`;
  - text messages отправляют `message.text` и `type`;
  - image messages отправляют `image_id`.
- `SwaggerRegistry` теперь не включает в normalized `required` поля, отсутствующие в `properties`; это убирает неконсистентный Swagger `required: ["url"]` в `sendMessageRequestBody`, где `url` не описан как свойство и не имеет JSON type.
- Обновлены domain tests и `CHANGELOG.md`.
- Проверено:
  - `poetry run pytest tests/domains/messenger/test_messenger.py tests/core/test_swagger_registry.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py` - pass;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `40 failed, 164 passed`;
  - `poetry run mypy avito/core/swagger_registry.py avito/messenger avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run ruff check avito/core/swagger_registry.py avito/messenger avito/testing/swagger_fake_transport.py tests/domains/messenger/test_messenger.py` - pass;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass.
- Request-body backlog уменьшен с `45` до `40`.
- Следующий практичный шаг: перейти к `special-offers` request batch.

### 2026-05-02 / Этап 7

- Закрыт `special-offers` request batch:
  - `multiCreate` отправляет только Swagger поле `itemIds`;
  - `multiConfirm` отправляет `dispatches[]` и опциональный `expiresAt`;
  - `stats` требует и отправляет `dateTimeFrom/dateTimeTo`.
- Обновлены публичные сигнатуры, request models, domain tests и `CHANGELOG.md`.
- В `SwaggerFakeTransport` убраны точечные scalar fallbacks: `itemIds`/`itemIDs`, `dateTime*`, `campaignId`, `fieldsValueIds`, `specification` и jobs `schedule` теперь подбираются через общий alias lookup и scoped body-field aliases.
- Проверено:
  - `poetry run pytest tests/domains/messenger/test_messenger.py` - pass;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `37 failed, 167 passed`;
  - `poetry run mypy avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run ruff check avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass.
- Request-body backlog уменьшен с `40` до `37`.
- Следующий практичный шаг: перейти к `promotion`, `ratings` или `realty` request batch.

### План / Этап 8: убрать корневую причину hardcode в Swagger contract harness

- Контекст после этапов 5-7:
  - `jobs`, `messenger` и `special-offers` request batches закрыты;
  - request-body backlog сейчас `37 failed, 167 passed`;
  - в `SwaggerFakeTransport` уже убраны несколько точечных scalar fallbacks, но это временное улучшение, а не полное архитектурное решение.
- Проблема:
  - `method_args` сейчас описывает только связь SDK-аргумента с top-level Swagger body field;
  - этого недостаточно для nested/object/array mappings: `users[].user_id`, `dispatches[].dispatchId`, `schedule.id`, `fieldsValueIds[]`;
  - из-за этого `SwaggerFakeTransport` вынужден угадывать тестовые аргументы и накапливает hardcode.
- Исправление:
  - вынести нормализацию Swagger field names в общий модуль и использовать ее в registry/linter/fake transport из одного источника;
  - расширить binding expressions до JSON-path уровня: `body.itemIds`, `body.dispatches[].dispatchId`, `body.users[].user_id`, `body.fieldsValueIds[]`;
  - научить `swagger_linter` валидировать весь path по `SwaggerSchema`, включая array/object leaf nodes;
  - перевести существующие грубые bindings (`users`, `dispatches`, `schedule`, `fieldsValueIds`, `specification`) на точные paths;
  - упростить `SwaggerFakeTransport`, чтобы он генерировал значения по parsed path + schema/annotation, а не через локальные `if field_name == ...`.
- Минимальная проверка этапа:
  - `poetry run python scripts/lint_swagger_bindings.py --strict`;
  - `poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short`;
  - `poetry run mypy avito/core avito/testing`;
  - `poetry run ruff check avito/core avito/testing tests/core tests/contracts`.
- После этого вернуться к оставшемуся request-body backlog: `promotion`, `ratings`, `realty`, затем крупные `orders/delivery` группы.

### 2026-05-02 / Этап 8

- Убрана корневая причина части hardcode в Swagger contract harness:
  - добавлен общий `avito.core.swagger_names.swagger_field_aliases()`;
  - добавлен parser/validator restricted body paths в `avito.core.swagger_schema_paths`;
  - `swagger_linter` теперь валидирует `body.field`, `body.array[]`, `body.array[].field`, `body.object.field` по normalized `SwaggerSchema`;
  - `SwaggerFakeTransport` использует parsed body path и schema leaf для генерации аргументов, вместо scoped aliases для `users`, `dispatches`, `fieldsValueIds`, `specification`, `schedule`;
  - сохранена поддержка literal Swagger property с brackets, например `body.uploadfile[]`.
- Переведены грубые bindings на точные body paths:
  - `users[].user_id`;
  - `dispatches[].dispatchId`, `dispatches[].recipientsCount`, `dispatches[].offerSlug`;
  - `fieldsValueIds[].valueId`;
  - `specification.brand.valueId`;
  - `schedule.id` и `schedule[].rate`.
- Проверено:
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass;
  - `poetry run pytest tests/core/test_swagger_schema_paths.py tests/core/test_swagger_registry.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py` - pass;
  - `poetry run pytest tests/core/test_swagger_schema_paths.py tests/core/test_swagger_registry.py tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `25 failed, 179 passed`;
  - `poetry run mypy avito/core avito/testing` - pass;
  - `poetry run ruff check avito/core avito/testing tests/core tests/contracts` - pass.
- Request-body backlog уменьшен с `37` до `25`.
- Следующий практичный шаг: закрыть `promotion`, `ratings`, `realty`, затем крупные `orders/delivery` groups.

### 2026-05-02 / Этап 8 завершен полностью

- Доведен до конца отказ от domain-specific body fixture hardcode в `SwaggerFakeTransport`:
  - удалены ручные ветки создания delivery/realty/promotion request DTO по именам классов и полей;
  - добавлен общий schema-aware dataclass/list/scalar generator по type hints публичного SDK метода;
  - генератор заполняет dataclass fields через Swagger property aliases и required/properties текущей schema, чтобы не добавлять лишние JSON поля;
  - enum/string/list/datetime/scalar значения теперь выводятся общим путем, а не через локальные branches для конкретного домена;
  - сохранены только отдельные генераторы для auth request objects, upload files и query objects, потому что они не являются JSON body DTO hardcode.
- Проверено:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `204 passed, 1707 deselected`;
  - `poetry run pytest tests/core/test_swagger_schema_paths.py tests/core/test_swagger_registry.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py` - `32 passed`;
  - `poetry run mypy avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run ruff check avito/testing/swagger_fake_transport.py` - pass.

### 2026-05-02 / Этап 2 завершен

- Полностью закрыт request-body backlog strict Swagger schema contracts.
- Закрыты оставшиеся request groups:
  - `promotion`: `orders/get` и `orders/status` приведены к Swagger payload shape;
  - `ratings`: ответы на отзывы отправляют `message`;
  - `realty`: bookings/prices/intervals/base payloads приведены к Swagger keys;
  - `orders`: markings, confirmation code, CNC details, courier range и labels приведены к Swagger request schemas;
  - `delivery`: production announcement/parcel/changeParcel payloads и sandbox tariffs/announcements/createParcel payloads приведены к Swagger request schemas.
- Разделены request-модели для похожих delivery endpoints, где Swagger требует разные JSON contracts:
  - production create/cancel announcement;
  - sandbox create/track announcement;
  - production create parcel и sandbox v2 create parcel.
- Обновлены доменные тесты под Swagger-shaped request payloads.
- Проверено:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `204 passed, 1707 deselected`;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass, `bound: 204, unbound: 0, duplicate: 0, ambiguous: 0, validation errors: 0`;
  - `poetry run pytest tests/domains/promotion/test_promotion.py tests/domains/ratings/test_ratings.py tests/domains/realty/test_realty.py tests/domains/orders/test_orders.py tests/contracts/test_model_contracts.py tests/contracts/test_client_contracts.py --tb=short` - `32 passed`;
  - `poetry run mypy avito/promotion avito/ratings avito/realty avito/orders avito/testing/swagger_fake_transport.py` - pass;
  - `poetry run ruff check avito/promotion avito/ratings avito/realty avito/orders avito/testing/swagger_fake_transport.py tests/domains/promotion/test_promotion.py tests/domains/ratings/test_ratings.py tests/domains/realty/test_realty.py tests/domains/orders/test_orders.py` - pass.
- Следующий практичный шаг: перейти к этапу 9, success response mismatches.

### 2026-05-03 / Этап 9 завершен

- Полностью закрыт success-response backlog strict Swagger schema contracts.
- Исправлены `from_payload()`/response mappers для Swagger-shaped success payloads:
  - `accounts`: `operations_history`, `listCompanyPhonesV1`, `getEmployeesV1`;
  - `ads`: `vas/prices` array response;
  - `jobs`: `vacancies/statuses` array response;
  - `messenger`: `chats/{chat_id}/messages` array response;
  - `promotion`: `items/services/dict` array response;
  - `auth/autoteka`: OAuth token `expires_in` принимает Swagger number.
- Обновлен устаревший contract harness smoke-test для `listItemsByEmployeeIdV1` под текущий Swagger-shaped request body.
- Проверено:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k success_response_models_accept --tb=short` - `204 passed, 1707 deselected`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short` - `204 passed, 1707 deselected`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k error_responses_preserve --tb=short` - `639 passed, 1272 deselected`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py --tb=short` - `1911 passed`;
  - `poetry run mypy avito/accounts avito/ads avito/jobs avito/messenger avito/promotion avito/auth` - pass;
  - `poetry run ruff check avito/accounts/models.py avito/ads/models.py avito/jobs/models.py avito/messenger/models.py avito/promotion/models.py avito/auth/provider.py tests/contracts/test_swagger_contracts.py` - pass.
- Следующий практичный шаг: этап 10 уже зеленый по текущему contract slice; перейти к этапу 11/12 и зафиксировать strict schema tests в lint/gate.

### 2026-05-03 / Этап 10 завершен

- Error-response contracts подтверждены текущими строгими Swagger schema tests.
- Подтверждено:
  - generated error payload валиден по Swagger schema;
  - `SwaggerFakeTransport` мапит каждый заявленный error status в SDK exception;
  - `exception.payload == swagger_payload`;
  - общий `ApiErrorPayload` сохраняет upstream payload без потерь.
- Кодовых изменений не потребовалось: общий error parser и typed error wrapper уже соответствуют целевому контракту.
- Проверено:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py -k "error_responses_preserve or maps_every_declared_error_status or error_contract_coverage" --tb=short` - `1279 passed, 632 deselected`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py --tb=short` - `1911 passed`;
  - `poetry run pytest tests/core/test_transport.py tests/core/test_operations.py --tb=short` - `41 passed`.
- Следующий практичный шаг: этап 11 - перенести runtime contract правила в `swagger_linter`, затем этап 12 - закрепить strict schema tests в gate.

### 2026-05-03 / Этап 11 завершен

- Runtime contract правила из `tests/contracts/test_swagger_contracts.py::test_swagger_operation_specs_cover_all_declared_json_bodies` перенесены в strict `swagger_linter`.
- В strict режиме `scripts/lint_swagger_bindings.py --strict` теперь дополнительно проверяет:
  - JSON `requestBody` со Swagger schema требует `OperationSpec.request_model`;
  - JSON success response требует `OperationSpec.response_model`, если `response_kind == "json"`;
  - JSON error response требует `OperationSpec.error_models[status]`;
  - JSON request/success/error schema должна быть разобрана registry.
- Добавлен unit-test `tests/core/test_swagger_linter.py` на новые linter-коды missing request/response/error model.
- Проверено:
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass, `bound: 204, unbound: 0, duplicate: 0, ambiguous: 0, validation errors: 0`;
  - `poetry run pytest tests/contracts/test_swagger_contracts.py --tb=short` - `1911 passed`;
  - `poetry run pytest tests/core/test_swagger_linter.py tests/core/test_swagger_registry.py tests/core/test_swagger_schema_paths.py tests/contracts/test_swagger_contracts.py::test_swagger_operation_specs_cover_all_declared_json_bodies --tb=short` - `16 passed`;
  - `poetry run mypy avito/core` - pass;
  - `poetry run ruff check avito/core tests/core/test_swagger_linter.py` - pass.
- Следующий практичный шаг: этап 12 - убедиться, что strict schema tests закреплены в `make swagger-coverage`/gate, затем прогнать `make check`.

### 2026-05-03 / Этап 12 завершен

- Strict schema tests закреплены в gate:
  - `make swagger-coverage` запускает `swagger-lint`, `tests/core/test_swagger_registry.py` и полный `tests/contracts/test_swagger_contracts.py`;
  - `make check` запускает полный `pytest`, поэтому strict Swagger schema contracts входят в общий gate.
- Проверено:
  - `make swagger-coverage` - pass, `1921 passed`;
  - `make check` - pass:
    - `poetry run pytest` - `2051 passed`;
    - `poetry run mypy avito` - pass;
    - `poetry run ruff check .` - pass;
    - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass, `bound: 204, unbound: 0, duplicate: 0, ambiguous: 0, validation errors: 0`;
    - `poetry run python scripts/lint_architecture.py` - pass, `errors=0`;
    - `poetry build` - pass, built sdist and wheel.
- Следующий практичный шаг: этап 13 - финальная проверка/резюме состояния проекта.

### 2026-05-03 / Этап 13 завершен

- Финальная проверка strict Swagger schema contract coverage завершена.
- Минимальные проверки из плана выполнены:
  - `poetry run pytest tests/contracts/test_swagger_contracts.py --tb=short` - `1911 passed`;
  - `poetry run pytest tests/domains/ --tb=short` - `37 passed`;
  - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass, `bound: 204, unbound: 0, duplicate: 0, ambiguous: 0, validation errors: 0`;
  - `poetry run mypy avito` - pass, `84 source files`;
  - `poetry run ruff check .` - pass.
- Финальный gate выполнен:
  - `make check` - pass:
    - `poetry run pytest` - `2051 passed`;
    - `poetry run mypy avito` - pass;
    - `poetry run ruff check .` - pass;
    - `poetry run python scripts/lint_swagger_bindings.py --strict` - pass;
    - `poetry run python scripts/lint_architecture.py` - pass, `errors=0`;
    - `poetry build` - pass, built sdist and wheel.
- Целевой инвариант strict Swagger schema contracts достигнут для текущих 23 Swagger specs / 204 operations.
