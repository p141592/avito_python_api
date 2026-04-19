# Changelog

Все заметные изменения SDK фиксируются в этом файле.

Формат записей:

- `Добавлено` — новые публичные методы, модели и доменные блоки.
- `Изменено` — совместимые изменения поведения и документации.
- `Исправлено` — багфиксы, корректировки mapping и transport.
- `Удалено` — убранные или больше не поддерживаемые части API.

## [Unreleased]

### Добавлено

- Политика релизного процесса в `docs/release.md`.
- Проверки качества `pytest`, `mypy`, `ruff` и `poetry build` в `README.md`.
- Безопасный debug hook `AvitoClient.debug_info()` для диагностики transport-конфигурации.
- GitHub Actions workflows `CI` и `Release` с обязательной валидацией проекта на Python `3.14`.
- Автоматическая публикация релиза по тегу `v*` с проверкой соответствия версии из `pyproject.toml`.
- Единый quality gate `make check` для тестов, типизации, линтинга и сборки.

### Изменено

- `README.md` приведён к объектному API SDK и дополнен сценарными примерами по доменам.
- `autoteka` очищена от неканоничных public methods: `resolve_catalog()`, `list_reports()`, `delete_bucket()` и `remove_bucket()` заменили старые составные имена без compatibility alias-ов.
- `pyproject.toml` дополнен strict-конфигурацией `mypy`, правилами `ruff` и современным build backend `poetry-core`.
- `Makefile` разделён на `fmt`, `lint`, `typecheck`, `test`, `build` и `check`, чтобы release не зависел от автоформатирования.
- `AGENTS.md` синхронизирован с реальной структурой SDK, наличием тестов и Python `3.14` quality gate.
- `realty` больше не использует generic `RealtyRequest`: публичные методы принимают `RealtyBookingsUpdateRequest`, `RealtyPricesUpdateRequest`, `RealtyIntervalsRequest` и `RealtyBaseParamsUpdateRequest`.
- `jobs` больше не использует generic `JobsRequest` / `JobsQuery`: публичный surface переведен на отдельные typed request/query-модели для applications, vacancies, resumes и webhooks.
- `autoteka` больше не использует generic `AutotekaRequest` / `AutotekaQuery`: публичный surface переведен на отдельные typed request/query-модели для preview, report, monitoring, scoring и valuation сценариев.
- `messenger.ChatMedia.upload_images()` больше не принимает `dict[str, object]`; вместо него используется typed request через `UploadImageFile` / `UploadImagesRequest`.
- `promotion.autostrategy` больше не использует generic payload-wrapper’ы: `CreateAutostrategyBudgetRequest`, `CreateAutostrategyCampaignRequest`, `UpdateAutostrategyCampaignRequest` и `ListAutostrategyCampaignsRequest` теперь содержат typed поля по documented contract.
- `promotion` и `ads` write-клиенты больше не раскрывают `Mapping[str, object]` в публичных сигнатурах helper/client-слоя; preview и apply используют одинаковый typed request contract.
- Автостратегия приведена к documented shape ответов: бюджет теперь возвращает `calc_id`, список кампаний включает `total_count`, `CampaignDetailsResult` хранит `campaign` / `forecast` / `items`, а `AutostrategyStat` содержит ежедневные значения и `totals`.
- Публичный surface очищен от неканоничных имен: `autoload_legacy()` -> `autoload_archive()`, `cpa_legacy()` -> `cpa_archive()`, `apply_vas_v2()` -> `apply_vas_direct()`, version-suffixed методы ratings/realty/orders заменены на каноничные имена без `_v1` / `_v2`.
