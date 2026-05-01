# TODO: Приведение SDK к STYLEGUIDE.md

## Контекст восстановления

Дата анализа: 2026-05-01.

Репозиторий: `/Users/n.baryshnikov/Projects/avito_python_api`.

Цель: устранить несоответствия `STYLEGUIDE.md` по архитектуре, публичным
сигнатурам, transport/auth boundary, docstrings, error language и enum fallback.

Выбранная стратегия: **breaking cleanup**. Старые публичные формы не сохраняются
через deprecated wrappers.

Исходное состояние проверок:

- `make lint` passed
- `make typecheck` passed
- `make swagger-lint` passed: 204/204 operations bound
- `make test` passed: 986 tests

Основные найденные несоответствия:

- OAuth token flow использует прямой `httpx` вне общего transport-контура.
- `AvitoClient` хранит публично заменяемые `settings`, `auth_provider`,
  `transport`.
- Public domain methods не принимают per-operation `timeout` и `retry` overrides.
- Internal `RequestModel`/query DTO и input DTO протекают в публичные сигнатуры.
- Есть wrapper `Application.list(...)` с двумя путями выполнения.
- Docstrings массово содержат generic fragments вместо reference-ready описаний.
- Часть публичных error messages смешивает русский и английский.
- `CpaCallStatusId` тихо возвращает `None` для неизвестного upstream значения.

## Этап 1. OAuth Through Transport

Перевести OAuth token flow на общий transport-контур:

- убрать прямые `httpx.Client()` и `client.post()` из `avito/auth/provider.py`;
- убрать `token_http_client`, `alternate_http_client`, `autoteka_http_client` из
  `AvitoClient._build_auth_provider`;
- выполнять token operations через unauthenticated `Transport(..., auth_provider=None)`;
- сохранить ошибки OAuth как `AuthenticationError`, без сырых `httpx` исключений
  наружу.

Проверка этапа:

- `rg -n "httpx.Client\\(|client\\.post\\(" avito/auth/provider.py avito/client.py`
  не показывает прямой OAuth HTTP-код;
- тест подтверждает, что token request получает SDK `User-Agent`, timeout и
  centralized error mapping;
- `poetry run pytest tests/core/test_authentication.py tests/core/test_transport.py`.

## Этап 2. Immutable AvitoClient

Сделать `AvitoClient` practically immutable:

- заменить публичное хранение на `_settings`, `_auth_provider`, `_transport`;
- добавить read-only properties `settings`, `auth_provider`, `transport`;
- запретить замену этих атрибутов после init;
- оставить изменяемым только `_closed`.

Проверка этапа:

- тесты проверяют, что `client.settings = ...`, `client.transport = ...`,
  `client.auth_provider = ...` невозможны;
- context manager и `close()` продолжают работать;
- `poetry run pytest tests/contracts/test_client_contracts.py tests/core/test_configuration.py`.

## Этап 3. Per-Operation Overrides

Добавить во все public API domain methods:

- `timeout: ApiTimeouts | None = None`;
- `retry: Literal["default", "enabled", "disabled"] | None = None`.

Прокинуть через:

- `DomainObject._execute(...)`;
- `OperationExecutor.execute(...)`;
- `RequestContext`.

Effective retry:

- `None` / `"default"` использует `OperationSpec.retry_mode`;
- `"enabled"` форсирует retry;
- `"disabled"` запрещает retry.

Проверка этапа:

- AST/grep-скан подтверждает наличие `timeout` и `retry` в public domain methods;
- тест подтверждает, что timeout попадает в `RequestContext`;
- тест подтверждает retry override precedence;
- `poetry run pytest tests/core/test_operations.py tests/core/test_transport.py`.

## Этап 4. Remove Internal DTO From Public Signatures

Заменить public signatures:

- `Review.list(*, offset=None, page=None, limit=None, timeout=None, retry=None)`;
- `AutotekaMonitoring.get_monitoring_reg_actions(*, limit=None, timeout=None, retry=None)`;
- `Vacancy.list(*, query: str | None = None, ...)`;
- `Vacancy.get(*, vacancy_id: int | str | None = None, query: str | None = None, ...)`;
- `Application.get_ids(*, updated_at_from: str, ...)`;
- удалить `Application.list(...)`;
- `Resume.list(*, query: str | None = None, ...)`.

Internal query dataclasses остаются только внутри реализации.

Проверка этапа:

- AST-скан не находит `Request`, `Query`, `Params` типы в public domain signatures;
- `Application.list` отсутствует;
- payload/query params совпадают со старым поведением;
- `poetry run pytest tests/domains/jobs/test_jobs.py tests/domains/ratings/test_ratings.py tests/domains/autoteka/test_autoteka.py`.

## Этап 5. Public Input Models Instead Of TypedDict/Internal RequestModel

Заменить публичные input DTO:

- `BbipItemInput`;
- `TrxItemInput`;
- `BidItemInput`;
- `ApplicationViewedItem` как public input.

Новая форма:

- frozen public dataclasses, не наследующие `RequestModel`;
- internal request dataclasses строятся внутри domain methods.

Проверка этапа:

- `rg -n "TypedDict|RequestModel" avito/*/domain.py` не показывает public input usage;
- dry-run и real payload promotion methods совпадают;
- tests покрывают BBIP, TrxPromo, CPA auction, application viewed update;
- `poetry run pytest tests/domains/promotion/test_promotion.py tests/domains/jobs/test_jobs.py`.

## Этап 6. Reference-Ready Docstrings

Заменить generic docstring fragments:

- "Выполняет публичную операцию ...";
- "Пустой результат возвращается как пустая коллекция или `None` согласно аннотации метода."

Каждый public method должен описывать:

- бизнес-действие;
- аргументы;
- return model;
- pagination/dry-run/idempotency/override behavior;
- common SDK exceptions.

Проверка этапа:

- `rg -n "Выполняет публичную операцию|Пустой результат возвращается" avito/*/domain.py`
  возвращает пусто;
- добавить тест/сканер против этих шаблонов;
- `poetry run pytest tests/contracts/`.

## Этап 7. Error Language Consistency

Заменить mixed-language public error fragments:

- `OAuth transport`;
- `OAuth endpoint`;
- `JSON files`;
- `Binding ambiguous`;
- аналогичные совпадения.

Проверка этапа:

- `rg -n "OAuth transport|OAuth endpoint|JSON files|Binding ambiguous" avito tests docs`
  возвращает пусто или только допустимые технические docs references;
- error tests продолжают проходить;
- `poetry run pytest tests/core/test_authentication.py tests/core/test_swagger_registry.py`.

## Этап 8. CPA Enum Fallback

Исправить `CpaCallStatusId`:

- добавить `UNKNOWN` или typed fallback;
- unknown upstream value не должен тихо превращаться в `None`;
- warning должен логироваться once per process.

Проверка этапа:

- тест unknown `statusId`;
- тест warning-once behavior;
- `poetry run pytest tests/domains/cpa/test_cpa.py`.

## Этап 9. Docs And Release Notes

Обновить:

- `CHANGELOG.md` с breaking changes;
- reference docs;
- how-to snippets со старыми query/request/input forms.

Проверка этапа:

- `rg` не находит старые snippets: `Application.list`, `query=ReviewsQuery`,
  `query=ApplicationIdsQuery`, старые TypedDict inputs;
- `make docs-strict`, если docs pipeline меняет reference output.

## Code To Remove After Completion

Удалить:

- `Application.list(...)` из `avito/jobs/domain.py`;
- public usage `ReviewsQuery`, `MonitoringEventsQuery`, `VacanciesQuery`,
  `ApplicationIdsQuery`, `ResumeSearchQuery` в domain signatures;
- `BbipItemInput`, `_TrxItemInputRequired`, `TrxItemInput`, `BidItemInput`, если
  больше не используются;
- `ApplicationViewedItem` как public `RequestModel`, после ввода public replacement;
- bare `httpx.Client()` fallback и direct `client.post(...)` в token flow;
- token HTTP clients из `AvitoClient._build_auth_provider`;
- generic docstring fragments;
- mixed-language public error fragments;
- tests/docs, завязанные на старые публичные формы.

Финальная проверка удаления:

- `rg -n "Application\\.list|def list\\(.*Application|ReviewsQuery|MonitoringEventsQuery|VacanciesQuery|ApplicationIdsQuery|ResumeSearchQuery" avito docs tests`;
- `rg -n "BbipItemInput|TrxItemInput|BidItemInput|ApplicationViewedItem" avito docs tests`;
- `rg -n "httpx.Client\\(|client\\.post\\(" avito/auth/provider.py avito/client.py`.

## Final Gate

Перед завершением:

- `make lint`;
- `make typecheck`;
- `make swagger-lint`;
- `poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py`;
- `poetry run pytest tests/domains/`;
- `make test`;
- `make check`;
- `make docs-strict`, если менялись docs/reference.

## Assumptions

- Breaking cleanup подтвержден: обратную совместимость через deprecated wrappers
  не сохраняем.
- Swagger binding invariant остается обязательным: 204 operations, exactly one
  discovered binding per operation.
- Internal request/query dataclasses могут остаться, но не в public domain signatures.
- Public input dataclasses допустимы, если явно задокументированы и не наследуют
  `RequestModel`.

## Changeslog выполнения

| Дата | Этап | Статус | Файлы | Проверка | Примечание |
|---|---|---|---|---|---|
| 2026-05-01 | План сохранен | done | `todo.md` | `sed -n '1,40p' todo.md`; `tail -n 20 todo.md` | Создан файл с контекстом восстановления, планом, проверками этапов и changeslog |
|  | OAuth through Transport | pending |  |  |  |
|  | Immutable AvitoClient | pending |  |  |  |
|  | Per-operation overrides | pending |  |  |  |
|  | Public signatures cleanup | pending |  |  |  |
|  | Public input models cleanup | pending |  |  |  |
|  | Docstrings cleanup | pending |  |  |  |
|  | Error language cleanup | pending |  |  |  |
|  | CPA enum fallback | pending |  |  |  |
|  | Docs and final gate | pending |  |  |  |
