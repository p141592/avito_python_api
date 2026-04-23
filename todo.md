# Документация avito-py на MkDocs Material

## Context

SDK `avito-py` покрывает 204 операции Avito API через 11 публичных доменных пакетов (`accounts`, `ads`, `autoteka`, `cpa`, `jobs`, `messenger`, `orders`, `promotion`, `ratings`, `realty`, `tariffs`) и 58 фабричных методов на `AvitoClient`. Число публичных доменов **не хардкодится** — вычисляется как уникальные значения колонки `пакет_sdk` в `docs/avito/inventory.md`, исключая `auth`, `core` и `testing`.

Сейчас у пользователя есть `README.md` с quickstart и доменными how-to snippet'ами (как требует STYLEGUIDE § Documentation Structure), русские docstring'и в публичном API и `CHANGELOG.md` в корне. Docstring'и не считать готовыми к строгому reference-гейту: перед включением `pydocstyle`/`interrogate` нужен отдельный проход по публичным контрактам, потому что часть docstring'ов сейчас короткая и не покрывает Returns/Raises/идемпотентность по STYLEGUIDE. **Каркас сайта уже создан** (PR 1 в основном реализован) — см. раздел «Текущее состояние».

STYLEGUIDE § Documentation Structure делает обязательными все четыре режима Diátaxis (tutorials / how-to / reference / explanations); usability_scorecard § 15 выделяет на документацию 7% итогового Score и фиксирует шесть подкритериев с измеримыми процедурами.

Цель — **стабилизировать существующий каркас** и достроить сайт, **не подменяя README** (доменные how-to snippets в README остаются — это нормативное требование STYLEGUIDE.md:678), а дополняя его режимами, которые в README невозможно компактно уместить: полный reference, длинные how-to с диаграммами, explanations и deploy-версионирование.

**Измеримые цели**:

- новичок (P1) доходит от `pip install` до `get_self()` за ≤15 минут (scorecard 1.6);
- опытный разработчик (P2) находит нужный метод без чтения исходников (scorecard 2.*);
- сопровождающий (P3) видит совместимость и deprecation без заглядывания в git-лог (scorecard 18.*);
- scorecard §15 закрыт по всем подпунктам 15.1–15.6 отдельно; агрегат вроде «6% из 7%» не заменяет провал отдельного подпункта;
- P2 может написать consumer-side test поверх SDK через документированный `avito.testing` без приватных полей и без реального HTTP (scorecard 16.1–16.2);
- Diátaxis-матрица 4×N заполнена; каждый публичный домен имеет минимум одну how-to на сайте (в дополнение к snippet'у в README).
- `docs-quality-report` покрывает не только scorecard §15, но и supporting-gates для §16.1–16.4 и §18.1–18.5, потому что production-ready docs здесь завязана на public testing contract и deprecation/CHANGELOG contract, а не только на markdown-страницы.

Язык — только русский. Визуализация — сбалансированная (Mermaid, admonitions, tabbed code, без кастомной темы). Версионирование — через `mike`.

## Текущее состояние (уже реализовано)

PR 1 в основном сделан:

- `mkdocs.yml` существует, настроен на `docs_dir: docs/site`.
- Группа `docs` в `pyproject.toml` содержит `mkdocs-material`, `mkdocs-awesome-pages-plugin`, `mkdocs-include-markdown-plugin`, `mike`.
- `.github/workflows/docs.yml` собирает сайт и деплоит через `mike`.
- Цели `docs-serve` / `docs-build` в `Makefile`.
- `[tool.poetry.urls].Documentation` указан в метаданных Poetry.
- Структура `docs/site/` с плейсхолдерами четырёх Diátaxis-разделов.
- `docs/site/index.md` — hero + три карточки + Diátaxis-карта.
- `docs/site/tutorials/getting-started.md` — первый рабочий tutorial.
- `docs/site/tutorials/first-promotion.md` — плейсхолдер.
- `docs/site/changelog.md` — include корневого `CHANGELOG.md`.

**Что сломано в текущем состоянии** (надо починить в PR 1):

1. `mkdocs build --strict` падает с 8 предупреждениями (strict-mode превращает warning → error):
   - Nav-ссылки вида `tutorials/` в `mkdocs.yml` не разрешаются до того, как плагин awesome-pages обработает nav; решение — удалить `nav` из `mkdocs.yml` и завести `docs/site/.pages` с порядком разделов и русскими именами вкладок.
   - `docs/site/index.md` содержит ссылку `../avito/inventory.md` — файл вне `docs_dir`; решить добавлением `docs/site/reference/coverage.md` и ссылкой на неё.
   - Несколько ссылок из `tutorials/getting-started.md` ведут на страницы, которые ещё не созданы (`how-to/auth-and-config.md`, `reference/client.md`); добавить плейсхолдеры.
2. `avito.testing.__init__` экспортирует только `FakeTransport` и `FakeResponse`, но `fake_transport.py` объявляет в `__all__` также `JsonValue`, `RecordedRequest`, `json_response`, `route_sequence` — нужные в how-to/reference примерах; синхронизировать публичный export.

## Зафиксированные решения

### Навигация

- Material-фичи: `navigation.tabs`, `navigation.sections`, `navigation.indexes`, `navigation.top`, `toc.follow`.
- `nav` удаляется из `mkdocs.yml`; nav управляется файлами `.pages` (awesome-pages plugin).
- Корневой `docs/site/.pages`:
  ```yaml
  nav:
    - Главная: index.md
    - Tutorials: tutorials
    - How-to: how-to
    - Reference: reference
    - Explanations: explanations
    - Changelog: changelog.md
  ```

### Код-блоки и аннотации

`content.code.annotate` **остаётся включённым глобально** — это фича рендеринга, не синтаксис Python. Проблема не в ней, а в аннотационном синтаксисе `# (N)!` внутри Python-блоков: mktestdocs передаёт блок в Python как есть, и `# (1)!` — невалидный Python-комментарий в Material-смысле (хотя технически парсится, маркер-символ может путать инструменты). Поэтому:

- **Правило**: в `tutorials/*.md` и `how-to/*.md` Python-блоки никогда не содержат аннотационных маркеров `# (N)!`. Это plain fenced code без Material-специфичного синтаксиса.
- `pymdownx.tabbed` тоже не используется в tutorials/how-to.
- В `explanations/` и `reference/` аннотации и вкладки разрешены — mktestdocs там не применяется.

### Исполняемость примеров (mktestdocs harness)

`mktestdocs` через `pytest tests/docs/`. Финальная политика: **все fenced code-блоки с меткой `python` или `pycon` в `README.md`, `tutorials/*.md` и `how-to/*.md` исполняются**. Bash, env, mermaid — не исполняются (нет метки `python`).

Правила классификации примеров:

- если блок показывает SDK-вызов и помечен как `python`/`pycon`, он обязан выполняться через docs-harness без сети;
- если блок иллюстративный и не должен исполняться, он не имеет метки `python`/`pycon` (`text`, `console`, `bash` и т.п.) и не считается copy-paste примером;
- в `reference/` и `explanations/` Python-блоки либо подключаются к тому же collector'у, либо заменяются на non-executable fence; скрытых непроверяемых SDK-примеров быть не должно;
- реальный HTTP допускается только в ручной TTFC-процедуре с настоящими ключами, а не в CI.

**Проблема изоляции**: `tutorials/getting-started.md:47` вызывает `AvitoClient.from_env().account().get_self()` — это реальный HTTP-запрос. В CI без API-секретов он упадёт. Базовое решение для PR 3 — `tests/docs/conftest.py` с pytest-фикстурой, которая:
1. Monkeypatches `AvitoClient.from_env()` → возвращает lightweight docs-test facade, повторяющий только публичные методы, используемые в README/tutorials/how-to (`account()`, `ad()`, и т.д.).
2. Facade внутри использует настоящие доменные объекты SDK, созданные поверх `FakeTransport.build()`, чтобы проверялись реальные публичные вызовы доменов без сетевого доступа.
3. FakeTransport скриптован `route_sequence` на типичные ответы (get_self, get_items, и т.д.), покрывающие все README/tutorials/how-to.
4. Env-переменные `AVITO_CLIENT_ID`/`AVITO_CLIENT_SECRET` устанавливаются в фикстуре как заглушки.

Ограничение harness: monkeypatch только `AvitoClient.from_env()` покрывает tutorial-путь, но не покрывает Python-блоки, где конструируется `AvitoClient(client_id=..., client_secret=...)` или `AvitoClient(AvitoSettings(...))` и затем выполняется SDK-вызов. Зафиксированный контракт:

- в executable examples сетевые SDK-вызовы идут через `AvitoClient.from_env()`;
- остальные способы инициализации (`AvitoClient(client_id=...)`, `AvitoClient(AvitoSettings(...))`) можно показывать, но без вызова методов, которые идут в transport;
- consumer-testing примеры используют `FakeTransport.as_client()` после добавления публичного testing API в PR 3;
- если документации нужен executable пример с прямым `AvitoClient(...)` и последующим SDK-вызовом, сначала расширяется docs-harness публичным тестовым API; monkeypatch приватных полей запрещён.

Не использовать хрупкий вариант «создать настоящий `AvitoClient`, потом заменить internals»: у `AvitoClient` нет публичного параметра `transport`, а STYLEGUIDE требует иммутабельности клиента после создания. Если в будущем понадобится полноценный `AvitoClient` с fake transport для docs-тестов, это отдельное публичное/тестовое API-решение, а не monkeypatch приватных полей.

Это позволяет README/tutorials/how-to показывать реальный API (`from_env()`) для P1-аудитории, и при этом тестировать код без сетевого доступа. Скрипты, которые явно импортируют `FakeTransport` (how-to `testing-with-fake-transport.md`), работают напрямую без monkeypatch.

**Дизайнерское правило**: каждый новый Python-блок в README/tutorials/how-to обязан работать с harness conftest без сетевых запросов. Если блок требует API-секрет или настоящий transport, это дефект документации, не test-skip.

### Страница «Покрытие API» (coverage.md)

`docs/site/reference/coverage.md` — статическая страница внутри `docs_dir`. Она **не ссылается относительными ссылками на `docs/avito/`** (они вне docs_dir и сломают strict-mode). Вместо этого ссылки на Swagger-схемы идут через GitHub blob URL вида `https://github.com/<owner>/<repo>/blob/main/docs/avito/api/<filename>.json`. Все файлы в `docs/avito/api/` имеют расширение **`.json`**, не `.yaml`.

**Важно**: `mkdocs.yml:4` сейчас содержит `repo_url: https://github.com/p141592/avito`, при этом `site_url`, badge coverage и локальный каталог проекта указывают на `avito_python_api`. До создания `coverage.md` нужно выбрать один canonical repo URL и синхронно обновить `mkdocs.yml`, Poetry metadata и badges. Если URL окажется неверным, blob-ссылки из coverage.md будут 404. Правило: blob-ссылки в coverage.md хардкодятся с верифицированным URL репозитория и обновляются при смене repo_url в mkdocs.yml; генерировать их динамически из конфига mkdocs не нужно (coverage.md меняется редко).

### Синхронизация specs ↔ inventory

`docs/avito/api/*.json` остаётся **единственным authoritative source of truth** по API-контракту; `docs/avito/inventory.md` — это производный индекс для SDK/discovery/doc-generation, а не замена Swagger/OpenAPI-спекам. Поэтому финальный DoD не может опираться только на `inventory-coverage-report.json`.

Зафиксированный контракт:

- `scripts/check_spec_inventory_sync.py --output spec-inventory-report.json` сверяет все операции из Swagger/OpenAPI-документов с таблицей `inventory.md`;
- отчёт проверяет как минимум `method + path + документ + раздел`, а не только общее количество строк;
- наличие операции в spec и отсутствие в inventory — дефект inventory;
- наличие операции в inventory без соответствующей spec-записи — дефект inventory или устаревшая запись;
- `coverage.md` может ссылаться на inventory как на удобный индекс, но CI-гейт по полноте строится отдельно через `check_spec_inventory_sync.py`.

### Deprecated-политика (docs и runtime — разные работы)

- *Сайт*: `_gen_reference.py` рендерит `!!! warning "Устаревшая операция"` из inventory. Если inventory содержит явное поле `replacement` (см. «Расширение inventory» ниже), генератор добавляет ссылку. Если нет — warning рендерится без replacement; эвристического вывода нет.
- *Runtime*: каждый публичный SDK-символ с `deprecated: да` **обязан** эмитировать `DeprecationWarning` при первом вызове с указанием replacement и целевой версии удаления (STYLEGUIDE § Deprecation Policy). Отсутствие `replacement` в inventory — недостаток inventory, а не повод обходить runtime-требование.
- *Gap-отчёт*: `scripts/check_inventory_coverage.py` (отдельный скрипт — не `_gen_reference.py`) пишет `inventory-coverage-report.json`. Включает `deprecated_without_replacement` для операций без заполненного поля `replacement`.

Runtime deprecation warnings — это изменение поведения публичного SDK, а не документационная задача. Его нельзя считать частью автогенерации reference. Реализация runtime warnings, тест `tests/contracts/test_deprecation_warnings.py` и запись в `CHANGELOG.md` идут отдельным SDK-contract блоком в PR 2.5/PR 3 до финального DoD.

### Расширение inventory (prerequisite финального DoD)

`docs/avito/inventory.md` сейчас не содержит колонок `deprecated_since`, `replacement` и `removal_version`. Без них финальный DoD (`deprecated_without_replacement` пуст и deprecation-период ≥2 minor) **недостижим** — это не дефект плана сайта, это gap в source of truth. В scope PR 2 входит:

1. Добавить колонки `deprecated_since`, `replacement` и `removal_version` в таблицу операций `docs/avito/inventory.md`.
2. Заполнить значения для всех записей с `deprecated: да`.
3. Обновить `scripts/parse_inventory.py` для разбора новых колонок (`InventoryRow.deprecated_since: str | None`, `InventoryRow.replacement: str | None`, `InventoryRow.removal_version: str | None`).
4. Добавить sanity-check inventory: описание с `(deprecated)` не может иметь `deprecated: нет`; `deprecated: да` не может быть без `deprecated_since`, `replacement`, `removal_version`; `removal_version` должен быть не раньше чем через два minor-релиза после `deprecated_since`.

До заполнения этих полей финальный DoD не применяется; промежуточные PR мержатся с непустым отчётом.

### Инструмент проверки ссылок (lychee)

`lychee` — не Python-зависимость. Для `make docs-check` требует отдельной установки:

- macOS: `brew install lychee`
- Linux/CI: `cargo binstall lychee` или GitHub Action [`lycheeverse/lychee-action`](https://github.com/lycheeverse/lychee-action)

Установка документируется в `CONTRIBUTING.md`. Если lychee не найден — `make docs-check` падает с понятным сообщением (не silent skip). В CI lychee запускается через GitHub Action, не через Makefile.

Конфигурация: `--exclude "avito\.ru"`, `--retry-wait-time 5`, `--max-retries 3`, `--timeout 30`.

Для локальной работы без lychee доступна цель `make docs-strict` (только `mkdocs build --strict` + Python-gates).

### Прочие решения

- **Автогенерация reference**: `mkdocstrings[python]` + `mkdocs-gen-files` + `mkdocs-literate-nav`. Генерируемые файлы (`reference/domains/*.md`, `reference/operations.md`, `reference/SUMMARY.md`) **не коммитятся** — создаются через `mkdocs_gen_files.open()` как виртуальные.
- **Версионирование**: фиксируем конкретную схему `mike`. На `push` в `main` деплоится docs-version `main` с alias `latest` через `mike deploy --push --update-aliases main latest`, затем `mike set-default --push latest`. На `push` тега `vX.Y.Z` деплоится docs-version `X.Y.Z` с alias `stable` через `mike deploy --push --update-aliases X.Y.Z stable`. Root redirect всегда ведёт на alias `latest`; `stable` — это последний релизный docs-snapshot, а не default alias.
- **mkdocstrings-зависимость**: `mkdocstrings = { version = ">=0.27", extras = ["python"] }`.
- **Inventory parser**: `scripts/parse_inventory.py` — reusable, возвращает `list[InventoryRow]` (frozen dataclass). Используется в `_gen_reference.py`, `check_readme_domain_coverage.py`, `check_inventory_coverage.py`, `check_docs_examples.py`, `check_spec_inventory_sync.py`.
- **Разделение ответственности**: `_gen_reference.py` только читает inventory и рендерит страницы. `scripts/check_inventory_coverage.py --output inventory-coverage-report.json` — владелец contract-отчёта.
- **Reference public surface**: generated reference ориентируется на фактическую публичную поверхность: `avito.__all__`, `avito.<domain>.__all__`, `avito.testing.__all__` и явные страницы для top-level contract (`AvitoClient`, `AvitoSettings`, `AuthSettings`, `PaginatedList`, exceptions). Отдельный скрипт `scripts/check_reference_public_surface.py --output reference-public-report.json` проверяет две вещи: все публичные экспорты попали в reference ровно один раз; internal/private символы вне экспортируемой поверхности не попали в `SUMMARY.md` и discovery-индекс.
- **CI fetch-depth**: `fetch-depth: 0` добавляется в `ci.yml` в PR 3 (нужен для `interrogate` diff-gate против `origin/main`).
- **poetry.lock**: каждый PR, добавляющий зависимости в `pyproject.toml`, коммитит обновлённый `poetry.lock`. Для Poetry 2.x используется `poetry lock` — опции `--no-update` больше нет, а сохранение уже зафиксированных версий является поведением по умолчанию.
- **Контракт README**: `scripts/check_readme_domain_coverage.py` читает домены из inventory через `parse_inventory.py` (не хардкоженный список), выходит с ненулевым кодом при пропущенных; включён в `make docs-strict` и `make docs-check`.
- **pydocstyle**: отдельная цель `make qa-docs`, не в `make lint`.
- **interrogate**: PR 2 — report-only; PR 3 — gate только на изменённые публичные модули.
- **Docstring readiness**: перед `pydocstyle`/`interrogate` привести публичные docstring'и к STYLEGUIDE: возвращаемая SDK-модель, nullable/empty behavior, per-operation overrides, идемпотентность, типовые исключения. Для этого нужен отдельный `scripts/check_public_docstrings.py --output docstring-contract-report.json`: в PR 2 report-only, в PR 3/финальном DoD — strict gate для публичных символов, попадающих в generated reference. До этого `interrogate` может быть только report-only, а reference не считается финально полным.
- **README example sync**: README и tutorial/how-to snippets обязаны отражать реальные публичные сигнатуры текущего SDK. Если public method ушёл с `request=` DTO на flattened keyword-only параметры, старый пример не может жить как “иллюстративный”. Это отдельный docs-contract, проверяемый mktestdocs и review-чек-листом.

## Структура `docs/site/`

```
docs/site/
  .pages                              # корневой nav для awesome-pages
  index.md                            # hero + три роли-входа (P1/P2/P3) + Diátaxis-карта
  tutorials/
    .pages
    index.md
    getting-started.md                # pip install → get_self() — показывает from_env(); тест через harness conftest
    first-promotion.md                # dry_run=True → dry_run=False
  how-to/
    .pages
    index.md
    auth-and-config.md                # placeholder PR 1; содержимое в PR 3
    (остальные рецепты — PR 3)
  reference/
    .pages
    index.md
    coverage.md                       # PR 1: «Покрытие API» со ссылками на GitHub blob URLs; заменяет битую ../avito/inventory.md
    client.md                         # placeholder PR 1; полный reference — PR 2
    operations.md                     # PR 2: генерируемая карта operation → SDK method
    config.md                         # PR 2
    domains/                          # генерируется _gen_reference.py (не коммитится)
    models.md                         # PR 2
    exceptions.md                     # PR 2
    pagination.md                     # PR 2
    testing.md                        # PR 2
  explanations/
    .pages
    index.md
    (статьи — PR 3)
  changelog.md                        # include из корневого CHANGELOG.md
  assets/
    _gen_reference.py
    overrides/
```

## Генерация reference

`docs/site/assets/_gen_reference.py`:

1. Импортирует `scripts/parse_inventory.py` для получения `list[InventoryRow]`.
2. Обходит `avito/` исключая internals: `core/transport.py`, `core/retries.py`, `auth/provider.py`, `_env.py`, `__main__.py`.
3. Для каждого публичного пакета создаёт виртуальную страницу `reference/domains/<pkg>.md` с шапкой (назначение пакета из inventory) и директивой `::: avito.<pkg>`. Источник публичной поверхности для пакетной страницы — `__all__` экспортируемого пакета, а не простое сканирование всего дерева `avito/<pkg>/`.
4. Создаёт виртуальную `reference/operations.md`: таблица `описание → HTTP method/path → пакет_sdk → доменный_объект → публичный_метод_sdk → deprecated/replacement`. Это основной discovery-индекс для P2.
5. Пишет виртуальный `reference/SUMMARY.md` для `literate-nav`.
6. Для операций с `deprecated: да` вставляет `!!! warning "Устаревшая операция"`. Ссылка на replacement добавляется только если поле `replacement` явно присутствует в `InventoryRow`. Эвристического вывода нет.
7. **Не пишет** в `inventory-coverage-report.json` — это ответственность `scripts/check_inventory_coverage.py`.

Важно: `scripts/check_inventory_coverage.py` не должен сводиться к простому `hasattr`. Он проверяет связку `пакет_sdk + доменный_объект + публичный_метод_sdk`, special-case `AvitoClient.auth()`, legacy-домены и то, что публичный символ попадает в reference-индекс. Наличие метода без документируемого публичного пути считается gap.

Все файлы создаются через `mkdocs_gen_files.open()` — **не на диск**, не в git.

## Опции `mkdocstrings`

```yaml
handlers:
  python:
    options:
      docstring_style: google
      docstring_section_style: table
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      show_source: false
      filters: ["!^_"]
      members_order: source
      heading_level: 2
```

## Разделение на этапы

### PR 1 — Стабилизация существующего каркаса

**Задача**: `mkdocs build --strict` проходит без предупреждений. Deploy проверяется после merge/push в main, потому что PR не публикует GitHub Pages.

Конкретные изменения:

- `mkdocs.yml`: удалить секцию `nav`.
- `docs/site/.pages`: создать (см. раздел «Навигация»).
- `docs/site/index.md`: ссылка `../avito/inventory.md` → `reference/coverage.md`.
- `docs/site/reference/coverage.md`: страница «Покрытие API» с таблицей 23 Swagger-документов и GitHub blob URL-ами.
- `mkdocs.yml`, Poetry metadata, badges: синхронизировать canonical repo URL (`avito` vs `avito_python_api`) до добавления blob-ссылок.
- `docs/site/reference/client.md`: placeholder.
- `docs/site/how-to/auth-and-config.md`: placeholder.
- `docs/site/how-to/.pages`: добавить `auth-and-config.md`.
- `docs/site/reference/.pages`: добавить `coverage.md`, `client.md`.
- `avito/testing/__init__.py`: синхронизировать публичный testing-export с `avito.testing.fake_transport.__all__`: `FakeTransport`, `FakeResponse`, `JsonValue`, `RecordedRequest`, `json_response`, `route_sequence`. Если `JsonValue` не должен быть публичным символом, сначала убрать его из обоих `__all__` и reference.

**Критерий готовности PR 1**: `poetry install --with docs && poetry run mkdocs build --strict` проходит без предупреждений; после merge/push сайт деплоится на GitHub Pages с alias `latest`; TTFC-проверка tutorial проходит вручную.

### PR 2 — Reference, inventory parser, расширение inventory

**Prerequisite**: `scripts/parse_inventory.py` — reusable модуль разбора inventory. Возвращает `list[InventoryRow]` (frozen dataclass с полями `deprecated_since: str | None`, `replacement: str | None`, `removal_version: str | None`).

Конкретные изменения:

- `docs/avito/inventory.md`: добавить колонки `deprecated_since`, `replacement` и `removal_version` в таблицу операций; заполнить для всех `deprecated: да`.
- `scripts/parse_inventory.py`: реализовать с поддержкой новых колонок.
- `scripts/check_inventory_coverage.py --output <path>`: реализовать; пишет `inventory-coverage-report.json`. Проверяет: каждой inventory-операции соответствует публичный SDK-символ; каждая `deprecated: да` запись имеет `deprecated_since`, `replacement` и `removal_version`; deprecation-период не меньше двух minor-релизов; описание и колонка `deprecated` не противоречат друг другу. В PR 2 работает report-only и не блокирует merge; hard `exit 1` на непустой gap-report включается в PR 3 / финальном DoD.
- `scripts/check_spec_inventory_sync.py --output <path>`: реализовать; пишет `spec-inventory-report.json`. Проверяет: каждая операция из `docs/avito/api/*.json` присутствует в inventory; в inventory нет операций, отсутствующих в spec; совпадают `документ + метод + путь + раздел`. В PR 2 работает report-only и публикуется как CI artifact.
- `scripts/check_readme_domain_coverage.py`: реализовать; домены из inventory.
- `scripts/check_reference_public_surface.py --output <path>`: реализовать; пишет `reference-public-report.json`. Проверяет: все экспорты из `avito.__all__`, `avito.<domain>.__all__`, `avito.testing.__all__` попадают в reference; лишние internal/private символы не попадают в generated nav/discovery pages. В PR 2 работает report-only и публикуется как CI artifact.
- Docstring readiness audit: сформировать report-only список публичных классов/методов, где docstring не покрывает требования STYLEGUIDE. Реализация — `scripts/check_public_docstrings.py --output <path>` с проверкой обязательных contract-aspects, а не только наличия docstring. Не блокирует PR 2, но блокирует перевод `interrogate` в gate.
- `pyproject.toml`, группа `docs` — добавить и обновить `poetry.lock`:
  ```toml
  mkdocstrings = { version = ">=0.27", extras = ["python"] }
  mkdocs-gen-files = ">=0.5"
  mkdocs-literate-nav = ">=0.6"
  ```
- `mkdocs.yml`: подключить `gen-files`, `literate-nav`, `mkdocstrings[python]`.
- `docs/site/assets/_gen_reference.py`: реализовать (виртуальные файлы).
- `docs/site/reference/`: создать `config.md`, `models.md`, `exceptions.md`, `pagination.md`, `testing.md`; `operations.md` генерируется виртуально из inventory.
- `Makefile`:
  ```makefile
  docs-strict:
      poetry run mkdocs build --strict
      poetry run python scripts/check_readme_domain_coverage.py

  docs-check: docs-strict
      lychee --exclude "avito\.ru" --retry-wait-time 5 --max-retries 3 --timeout 30 site/
  ```
- `interrogate` — report-only: CI публикует артефакт `interrogate-report.txt`. Baseline коммитится в `.interrogate-baseline`:
  ```json
  {"modules": {"avito/accounts/client.py": 92.5, ...}, "generated_at": "<iso8601>", "interrogate_version": "<x.y.z>"}
  ```

**Критерий готовности PR 2**: все пункты STYLEGUIDE § What Constitutes the Public SDK Contract имеют reference-страницу или явно отмеченный docstring gap; deprecated-бейджи рендерятся; `reference/operations.md` строится из inventory; `make docs-strict` проходит; `inventory-coverage-report.json`, `spec-inventory-report.json`, `reference-public-report.json` и `docstring-contract-report.json` публикуются как CI-артефакты; колонки `deprecated_since`/`replacement`/`removal_version` заполнены для всех `deprecated: да` записей. Непустые SDK coverage/spec-sync/reference-public/docstring gaps допустимы только как report-only артефакты PR 2 и должны быть закрыты к финальному DoD.

### PR 2.5 — Runtime deprecation contract

**Задача**: синхронизировать runtime-поведение SDK с deprecated-данными inventory. Это публичное SDK-изменение, поэтому оно отделено от генерации сайта.

Конкретные изменения:

- Добавить runtime `DeprecationWarning` для каждого публичного SDK-символа с `deprecated: да`, при первом вызове, с replacement и целевой версией удаления.
- Добавить/обновить docstring line у deprecated-символов: replacement и target removal version.
- Добавить `tests/contracts/test_deprecation_warnings.py`, который строит cases из inventory, но проверяет поведение через реальные публичные вызовы/минимальные fake-transport сценарии, а не только наличие атрибута.
- Добавить запись в `CHANGELOG.md` в секцию `Deprecated`; проверить, что CHANGELOG релиза содержит стандартные секции `Added`/`Changed`/`Deprecated`/`Removed`/`Fixed` (пустые секции допустимы только если политика changelog это явно разрешает).

**Критерий готовности PR 2.5**: `pytest tests/contracts/test_deprecation_warnings.py` зелёный; runtime warnings не дублируются сверх первого вызова; `make test typecheck lint` зелёные.

### PR 3 — How-to, explanations и quality gates

Конкретные изменения:

- `docs/site/how-to/*` — 14 рецептов с фиксированными файлами:
  `auth-and-config.md`, `chat-image-upload.md`, `promotion-dry-run.md`, `pagination.md`,
  `order-labels.md`, `job-applications.md`, `autoteka-report.md`, `realty-booking.md`,
  `cpa-calltracking.md`, `ratings-and-tariffs.md`, `per-operation-overrides.md`,
  `idempotency.md`, `testing-with-fake-transport.md`, `diagnostics-and-logging.md`.
- `docs/site/explanations/*` — 8 концептуальных статей с Mermaid:
  `architecture.md`, `auth-flow.md`, `transport-and-retries.md`, `error-model.md`,
  `pagination-semantics.md`, `dry-run-and-idempotency.md`, `testing-strategy.md`,
  `api-coverage-and-deprecations.md`.
- До массового написания how-to: обновить `README.md` и уже существующие tutorial-snippet'ы под реальные публичные сигнатуры текущего SDK. Устаревшие примеры с `request=` DTO там, где сигнатура уже flattened, переписываются, а не помечаются как “illustrative”.
- Перед `testing-with-fake-transport.md`: добавить публичный consumer-testing API. Выбранный контракт: `FakeTransport.as_client(*, user_id: int | None = None, retry_policy: RetryPolicy | None = None) -> AvitoClient`. Он создаёт полностью инициализированный `AvitoClient` поверх fake transport без post-init monkeypatch приватных полей и без публичного параметра `transport` в `AvitoClient.__init__`. `FakeTransport.build()` не используется в пользовательской документации; если он остаётся, он помечается как low-level/internal testing helper или проходит deprecation policy.
- Перед массовым написанием рецептов: реализовать mktestdocs harness на `getting-started.md` и одном how-to, прогнать `pytest tests/docs/`, затем масштабировать на остальные страницы.
- `tests/docs/conftest.py`: mktestdocs harness — monkeypatch `AvitoClient.from_env()` → lightweight docs-test facade поверх настоящих доменных объектов и `FakeTransport.build()`; заглушки env-переменных. Если how-to выполняют сетевые вызовы через прямой `AvitoClient(...)`, сначала принять отдельное публичное тестовое API для fake transport или переписать пример так, чтобы сетевой вызов выполнялся через `from_env()`.
- `tests/docs/test_docs_harness_surface.py`: проверяет, что docs-test facade не изобретает собственный API: имена фабрик/методов и callable-сигнатуры, используемые harness, совпадают с реальными публичными сигнатурами `AvitoClient` и соответствующих доменных объектов.
- `tests/docs/test_markdown_examples.py`: pytest-тест, который вызывает mktestdocs для `README.md`, `docs/site/tutorials/*.md` и `docs/site/how-to/*.md`; одного `conftest.py` недостаточно для запуска markdown-примеров.
- `tests/docs/test_no_placeholders.py`: падает, если production docs содержат `Раздел в разработке`, `placeholder`, `плейсхолдер`, `TODO`, `TBD`, `coming soon`.
- `scripts/check_docs_examples.py`: проверяет, что SDK-примеры в `reference/` и `explanations/` либо исполняются тем же collector'ом, либо не помечены как `python`/`pycon`.
- `pyproject.toml`, группа `docs` — добавить и обновить `poetry.lock`:
  ```toml
  mktestdocs = ">=0.2"
  interrogate = ">=1.7"
  pydocstyle = { version = ">=6.3", extras = ["toml"] }
  ```
- `mktestdocs` через `pytest tests/docs/`: все `python`/`pycon` блоки в README/tutorials/how-to. Включается в `make docs-strict`.
- `pydocstyle` с профилем Google — `make qa-docs`, **не** `make lint`.
- `interrogate` gate — diff против `origin/main`; per-module vs baseline. `ci.yml`: `fetch-depth: 0`.
- `CONTRIBUTING.md`: инструкция по установке lychee (`brew install lychee` / `cargo binstall lychee`); review-чек-лист README domain coverage.
- `.github/pull_request_template.md`: чек-лист coverage.
- `.github/workflows/docs.yml`: шаг `lycheeverse/lychee-action` (не вызов `make docs-check`); на `push` в `main` выполняются `mike deploy --push --update-aliases main latest` и `mike set-default --push latest`; на `push` тега `v*` выполняется `mike deploy --push --update-aliases <version> stable`, где `<version>` берётся из тега без `v`.
- `.github/workflows/ci.yml`: добавить `make docs-strict` в пайплайн; `fetch-depth: 0`.
- `Makefile`: в PR 3 расширить `docs-strict`, добавив `poetry run pytest tests/docs/`. В PR 2 snippet `docs-strict` ещё не включает mktestdocs.
- `docs-quality-report.md` или CI artifact `docs-quality-report.json`: фиксирует Diátaxis-матрицу, прохождение 15.1–15.6, TTFC-замер, README/domain coverage, markdown examples, lychee, inventory coverage, spec↔inventory sync, reference public surface, docstring readiness, а также supporting-gates для scorecard §16 и §18.

**Критерий готовности PR 3**: Diátaxis-матрица 4×N; каждый публичный домен (из inventory, кроме auth/core/testing) имеет ≥1 how-to; README/tutorials/how-to синхронизированы с реальными публичными сигнатурами SDK; все `python`/`pycon` блоки в README/tutorials/how-to исполняются через mktestdocs с harness conftest; docs-harness surface проверен отдельным тестом; SDK-примеры в reference/explanations либо исполняются, либо не помечены как executable; `make docs-strict`, `make qa-docs` и CI lychee-step проходят; `mike list` показывает как минимум `main [latest]` и текущий релиз `[stable]`; scorecard §15.1–15.6 закрыт по каждому подпункту, а `docs-quality-report` показывает supporting-gates для §16 и §18.

## Риски и их нейтрализация

| Риск | Нейтрализация |
|---|---|
| mktestdocs падает на `AvitoClient.from_env()` в CI | `tests/docs/conftest.py` monkeypatches from_env → docs-test facade поверх FakeTransport; реальных API-вызовов нет |
| mktestdocs пропускает прямой `AvitoClient(...)` и уходит в сеть | Использовать зафиксированный контракт: executable network calls только через `from_env()`, consumer-testing через `FakeTransport.as_client()`, прямой `AvitoClient(...)` без transport-вызова |
| README содержит SDK-snippet'ы, которые не покрыты docs-harness | Включить `README.md` в `tests/docs/test_markdown_examples.py`; переписать или переклассифицировать каждый non-executable блок |
| Annotation-маркеры `# (N)!` ломают Python-блоки | Правило: в tutorials/how-to нет аннотационного синтаксиса; `content.code.annotate` остаётся глобально включённым (это не источник проблемы) |
| `coverage.md` ссылается на файлы вне `docs_dir` | Только GitHub blob URLs; нет относительных ссылок на `docs/avito/` |
| Inventory расходится со Swagger/OpenAPI-спеками | `check_spec_inventory_sync.py` сравнивает `docs/avito/api/*.json` с `inventory.md`; report-only в PR 2, strict в финальном DoD |
| lychee не установлен локально | `make docs-strict` без lychee; `make docs-check` документирует зависимость; в CI — GitHub Action |
| Финальный DoD по deprecated недостижим без inventory | В scope PR 2: добавить колонки `deprecated_since`/`replacement`/`removal_version`; финальный DoD применяется только после их заполнения |
| Inventory содержит противоречивые deprecated-данные | `check_inventory_coverage.py` проверяет `description` vs `deprecated`, обязательные `deprecated_since`/`replacement`/`removal_version` и deprecation-период |
| Runtime deprecated warnings смешиваются с docs-задачей | Выделить PR 2.5 SDK-contract: warnings, docstrings, tests, CHANGELOG |
| `_gen_reference.py` становится владельцем contract-логики | `check_inventory_coverage.py` владеет отчётом; генератор только рендерит |
| `check_inventory_coverage.py` превращается в `hasattr`-проверку | Проверять связку из inventory, special-case auth/legacy и попадание символа в reference-индекс |
| Generated reference случайно протекает internal/private surface | `check_reference_public_surface.py` сверяет reference с `__all__`-экспортами и top-level contract |
| `poetry.lock` устаревает | Каждый PR с новыми deps коммитит обновлённый lock (`poetry lock` для Poetry 2.x) |
| interrogate diff требует git history | `fetch-depth: 0` в ci.yml (PR 3) |
| lychee шумит на нестабильных хостах | `--exclude "avito\.ru"`, retry 3, timeout 30с |
| `repo_url` расходится с GitHub Pages/coverage badge | В PR 1 выбрать canonical repo и синхронизировать `mkdocs.yml`, Poetry metadata, badges и blob-ссылки |
| В production docs остаются плейсхолдеры | `tests/docs/test_no_placeholders.py` и финальный `rg`-gate на `Раздел в разработке|placeholder|плейсхолдер|TODO|TBD|coming soon` |
| README/snippet'ы отстают от реальных public signatures | Обязательная синхронизация примеров в PR 3 + mktestdocs + review-чек-лист |
| Docs-harness начинает жить отдельно от реального API | `tests/docs/test_docs_harness_surface.py` сверяет facade с `AvitoClient` и доменными public methods |

## Реиспользуемые артефакты

- `avito/testing/__init__.py` (после PR 1: `FakeTransport`, `FakeResponse`, `JsonValue`, `RecordedRequest`, `json_response`, `route_sequence`; после PR 3: `FakeTransport.as_client()`) — harness conftest, how-to, reference.
- `avito/core/exceptions.py` — reference `exceptions.md`, explanation `error-model.md`.
- `avito/core/pagination.py:PaginatedList` — reference `pagination.md`, explanation `pagination-semantics.md`.
- `avito/core/serialization.py:SerializableModel` — reference `models.md`.
- `docs/avito/inventory.md` — парсится через `parse_inventory.py`; источник доменов, deprecated-статусов, `deprecated_since`, `replacement`, `removal_version`.
- Доменные `client.py` с публичными docstring'ами — автопарсятся `mkdocstrings`; до финального DoD они проходят docstring readiness audit по STYLEGUIDE.
- `CHANGELOG.md` — включается через `mkdocs-include-markdown-plugin`.

## Definition of Done (итоговая)

- Все PR 1, PR 2, PR 2.5 и PR 3 смержены.
- `mkdocs build --strict` — без предупреждений.
- CI lychee-step — ноль битых ссылок.
- Все `python`/`pycon` блоки в README/tutorials/how-to исполняются через mktestdocs с harness conftest в `pytest tests/docs/`.
- SDK-примеры в reference/explanations либо исполняются тем же collector'ом, либо не помечены как executable Python.
- `interrogate` baseline зафиксирован; gate проходит для изменённых публичных модулей.
- `make qa-docs` зелёный после закрытия docstring readiness gaps.
- Deprecated-статусы в reference совпадают с inventory; runtime `DeprecationWarning` реализован для deprecated SDK-символов; `test_deprecation_warnings` зелёный; `deprecated_since`, `replacement` и `removal_version` заполнены для всех `deprecated: да` записей; deprecation-период не меньше двух minor-релизов.
- `inventory-coverage-report.json` пуст.
- `spec-inventory-report.json` пуст.
- `reference-public-report.json` пуст.
- `docs-quality-report` опубликован как CI artifact и показывает 15.1–15.6 без пропусков, а также supporting-gates для scorecard §16 и §18.
- Docstring readiness gaps закрыты для публичных контрактов, попадающих в generated reference.
- Diátaxis-матрица 4×N; каждый публичный домен (кроме auth/core/testing) имеет ≥1 how-to; `make docs-strict` проходит полностью.
- Reference `operations.md` даёт карту всех inventory operations к публичным SDK-методам.
- Reference `testing.md` и how-to `testing-with-fake-transport.md` покрывают все аспекты public testing contract: scripting responses, call inspection, transport-level errors, `Retry-After`, `as_client()` consumer test.
- Каждый пункт STYLEGUIDE § What Constitutes the Public SDK Contract покрыт reference-страницей.
- README/tutorials/how-to snippet'ы соответствуют актуальным публичным сигнатурам SDK; устаревших примеров с pre-refactor `request=` DTO в flattened-methods не осталось.
- В production docs нет плейсхолдеров: `Раздел в разработке`, `placeholder`, `плейсхолдер`, `TODO`, `TBD`, `coming soon`.
- `mike list` показывает `main [latest]` и как минимум один релизный docs-version с alias `stable`; root redirect ведёт на `latest`.

## Verification

1. `poetry install --with docs` — зависимости встают, lock актуален.
2. `make docs-serve` — локальный сайт, четыре Diátaxis-вкладки.
3. `make docs-strict` — после PR 2: `mkdocs build --strict` + `check_readme_domain_coverage.py`; после PR 3 дополнительно mktestdocs через `pytest tests/docs/` и placeholder-gate.
4. `make docs-check` — дополнительно lychee (требует `brew install lychee`).
5. `make qa-docs` — `pydocstyle` с профилем Google.
6. `poetry run pytest tests/docs/` — исполняет README/tutorials/how-to snippets и проверяет отсутствие плейсхолдеров.
7. TTFC-процедура: чистый venv, `pip install avito-py`, tutorial, засечь время до реального `get_self()` с настоящими ключами.
8. `pytest tests/contracts/test_deprecation_warnings.py` — для каждого SDK-символа с `deprecated: да`.
9. `python scripts/check_inventory_coverage.py --strict --output inventory-coverage-report.json` — exit 0.
10. `python scripts/check_spec_inventory_sync.py --strict --output spec-inventory-report.json` — exit 0.
11. `python scripts/check_reference_public_surface.py --strict --output reference-public-report.json` — exit 0.
12. `python scripts/check_public_docstrings.py --strict --output docstring-contract-report.json` — exit 0 после закрытия gaps.
13. `rg -n "Раздел в разработке|placeholder|плейсхолдер|TODO|TBD|coming soon" docs/site README.md` — пустой вывод для production docs.
14. CI: PR с битой ссылкой → lychee-step падает; PR с пониженным coverage → interrogate падает.
15. Push в `main` → `mike deploy --push --update-aliases main latest` + `mike set-default --push latest`; push тега `v*` → `mike deploy --push --update-aliases <version> stable`; `mike list` показывает оба alias.
