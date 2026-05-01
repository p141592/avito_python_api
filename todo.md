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
| 2026-05-01 | OAuth through Transport | done | `avito/auth/provider.py`, `avito/client.py`, `tests/core/test_authentication.py` | `rg -n "httpx\\.Client\\(|client\\.post\\(" avito/auth/provider.py avito/client.py`; `poetry run pytest tests/core/test_authentication.py tests/core/test_transport.py`; `poetry run ruff check avito/auth/provider.py avito/client.py tests/core/test_authentication.py`; `poetry run mypy avito/auth/provider.py avito/client.py` | OAuth token flow идет через unauthenticated `Transport`; token clients получают SDK settings для base URL, timeout и User-Agent |
| 2026-05-01 | Immutable AvitoClient | done | `avito/client.py`, `tests/contracts/test_client_contracts.py` | `poetry run pytest tests/contracts/test_client_contracts.py tests/core/test_configuration.py`; `poetry run ruff check avito/client.py tests/contracts/test_client_contracts.py`; `poetry run mypy avito/client.py` | `settings`, `auth_provider`, `transport` переведены на read-only properties; тесты используют `_from_transport` вместо мутации клиента |
| 2026-05-01 | Per-operation overrides | done | `avito/core/types.py`, `avito/core/operations.py`, `avito/core/domain.py`, `avito/core/transport.py`, `avito/*/domain.py`, `tests/core/test_operations.py`, `tests/core/test_transport.py` | `poetry run pytest tests/core/test_operations.py tests/core/test_transport.py`; `poetry run mypy avito`; `poetry run ruff check avito tests/core/test_operations.py tests/core/test_transport.py`; `make swagger-lint` | `timeout` и `retry` добавлены в Swagger-bound public methods; executor прокидывает `ApiTimeouts` в `RequestContext`; `retry=\"disabled\"` запрещает retry даже для retryable HTTP methods |
| 2026-05-01 | Public signatures cleanup | done | `avito/ratings/domain.py`, `avito/autoteka/domain.py`, `avito/jobs/domain.py`, `tests/domains/ratings/test_ratings.py`, `tests/domains/autoteka/test_autoteka.py`, `tests/domains/jobs/test_jobs.py`, `docs/site/how-to/ratings-and-tariffs.md`, `docs/site/how-to/job-applications.md` | `poetry run pytest tests/domains/jobs/test_jobs.py tests/domains/ratings/test_ratings.py tests/domains/autoteka/test_autoteka.py`; `poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py`; `poetry run mypy avito`; `poetry run ruff check avito tests/domains/jobs/test_jobs.py tests/domains/ratings/test_ratings.py tests/domains/autoteka/test_autoteka.py`; `make swagger-lint`; `make docs-strict` | Internal query DTO убраны из public domain signatures; `Application.list(...)` удален; docs snippets переведены на `get_ids`, `get_by_ids`, primitive query params |
| 2026-05-01 | Public input models cleanup | done | `avito/promotion/models.py`, `avito/promotion/domain.py`, `avito/promotion/__init__.py`, `avito/jobs/models.py`, `avito/jobs/domain.py`, `avito/testing/swagger_fake_transport.py`, `tests/domains/promotion/test_promotion.py`, `tests/contracts/test_model_contracts.py` | `poetry run pytest tests/domains/promotion/test_promotion.py tests/domains/jobs/test_jobs.py`; `poetry run pytest tests/core/test_swagger*.py tests/contracts/test_swagger_contracts.py`; `poetry run ruff check avito/promotion/models.py avito/promotion/domain.py avito/promotion/__init__.py avito/jobs/models.py avito/jobs/domain.py avito/testing/swagger_fake_transport.py tests/domains/promotion/test_promotion.py tests/domains/jobs/test_jobs.py tests/contracts/test_model_contracts.py`; `poetry run mypy avito/promotion/models.py avito/promotion/domain.py avito/jobs/models.py avito/jobs/domain.py`; `make swagger-lint`; `rg -n "class ApplicationViewedItem\\(RequestModel\\)|class (BbipItemInput|_TrxItemInputRequired|TrxItemInput|BidItemInput)|TypedDict" avito docs tests` | `BbipItemInput`, `_TrxItemInputRequired`, `TrxItemInput`, `BidItemInput` удалены; public promotion signatures принимают `BbipItem`, `TrxItem`, `CpaAuctionBidInput`; `ApplicationViewedItem` больше не наследует `RequestModel`, внутренний payload строится через request dataclasses |
| 2026-05-01 | Docstrings cleanup | done | `avito/accounts/domain.py`, `avito/ads/domain.py`, `avito/autoteka/domain.py`, `avito/cpa/domain.py`, `avito/jobs/domain.py`, `avito/messenger/domain.py`, `avito/orders/domain.py`, `avito/promotion/domain.py`, `avito/ratings/domain.py`, `avito/realty/domain.py`, `tests/contracts/test_docstring_contracts.py` | `rg -n "Выполняет публичную операцию|Пустой результат возвращается" avito/*/domain.py`; `poetry run pytest tests/contracts/`; `poetry run ruff check avito/accounts/domain.py avito/ads/domain.py avito/autoteka/domain.py avito/cpa/domain.py avito/jobs/domain.py avito/messenger/domain.py avito/orders/domain.py avito/promotion/domain.py avito/ratings/domain.py avito/realty/domain.py tests/contracts/test_docstring_contracts.py` | Generic docstring fragments заменены на reference-ready описания с аргументами, return model, pagination/idempotency/timeout/retry behavior и common SDK exceptions; добавлен contract-test против регресса |
| 2026-05-01 | Error language cleanup | done | `avito/auth/provider.py`, `avito/core/swagger_registry.py`, `avito/testing/swagger_fake_transport.py` | `rg -n "OAuth transport|OAuth endpoint|JSON files|Binding ambiguous" avito tests docs`; `poetry run pytest tests/core/test_authentication.py tests/core/test_swagger_registry.py`; `poetry run ruff check avito/auth/provider.py avito/core/swagger_registry.py avito/testing/swagger_fake_transport.py` | Mixed-language public error fragments заменены на русские формулировки |
| 2026-05-01 | CPA enum fallback | done | `avito/core/enums.py`, `avito/cpa/models.py`, `tests/domains/cpa/test_cpa.py` | `poetry run pytest tests/domains/cpa/test_cpa.py`; `poetry run ruff check avito/core/enums.py avito/cpa/models.py tests/domains/cpa/test_cpa.py`; `poetry run mypy avito/core/enums.py avito/cpa/models.py` | `CpaCallStatusId.UNKNOWN` добавлен; unknown `statusId` мапится в typed fallback и логирует warning once per process |
| 2026-05-01 | Docs and final gate | done | `README.md`, `CHANGELOG.md`, `avito/jobs/__init__.py`, `avito/autoteka/__init__.py`, `todo.md` | `rg -n "Application\\.list|query=ReviewsQuery|query=ApplicationIdsQuery|query=ResumeSearchQuery|BbipItemInput|TrxItemInput|BidItemInput|ReviewsQuery\\(|ApplicationIdsQuery\\(|ResumeSearchQuery\\(" README.md docs/site`; `rg -n "ApplicationIdsQuery|ResumeSearchQuery|VacanciesQuery|MonitoringEventsQuery" avito/*/__init__.py README.md docs/site`; `make docs-strict`; `poetry run pytest tests/core/test_swagger_registry.py tests/contracts/test_swagger_contracts.py`; `poetry run pytest tests/domains/`; `make check` | README snippets и release notes обновлены; internal query DTO убраны из generated reference surface; full gate passed |
