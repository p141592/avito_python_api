# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added
- Нет изменений.

### Deprecated
- Архивные CPA-методы `CpaArchive.get_call`, `CpaArchive.get_balance_info`, `CpaArchive.get_call_by_id` и режим `CpaChat.list(version=1)` теперь эмитируют `DeprecationWarning` при первом вызове; используйте `call_tracking_call().download`, `cpa_lead().get_balance_info`, `call_tracking_call().get` и `cpa_chat().list(version=2)`.
- Архивные методы автозагрузки `AutoloadArchive.get_profile`, `AutoloadArchive.save_profile`, `AutoloadArchive.get_last_completed_report`, `AutoloadArchive.get_report` теперь эмитируют `DeprecationWarning` при первом вызове; используйте `autoload_profile().get`, `autoload_profile().save`, `autoload_report().get_last_completed` и `autoload_report().get`.

### Changed
- Централизовано выполнение схемы `request + map` через `Transport.request_public_model`.
- Убраны прямые обращения доменных клиентов к `request_json` и приватному `Transport._auth_provider`.
- Секционные клиенты переведены на `@dataclass(slots=True, frozen=True)`.
- Иерархия исключений упрощена до frozen dataclass без кастомного `__setattr__`.
- Публичные сигнатуры `accounts`, `ads`, `autoteka`, `cpa`, `jobs`, `messenger`, `orders`, `promotion`, `ratings` и `realty` переведены с `request`-DTO на keyword-only примитивы и коллекции.
- Transport получил поддержку `Idempotency-Key`; публичные write-методы во всех доменах принимают `idempotency_key`, а dry-run/write-контракт promotion покрыт тестами.
- Во всех доменных пакетах добавлены `enums.py`; `accounts`, `ads`, `autoteka`, `jobs`, `messenger`, `orders`, `promotion`, `ratings`, `realty` и `tariffs` переведены на typed enums с fallback на `UNKNOWN` и warning-логом ровно один раз на неизвестное upstream-значение.

### Removed
- **BREAKING:** удалены классы исключений `NotFoundError`, `ClientError`, `ServerError` из `avito.core.exceptions`. HTTP 404 и 5xx теперь маппятся на `UpstreamApiError`. Пользователям, ловившим эти типы, перейти на `UpstreamApiError` или `AvitoError` и проверять `status_code`.
- Удалены legacy-модули `avito/auth/mappers.py` и `avito/auth/enums.py` (внутренние, без публичных импортов).
- Удалены инфраструктурные мета-тесты (`tests/docs/`, `tests/test_inventory_architecture.py`, `tests/test_download_avito_api_specs.py`, `tests/core/test_architecture_lint.py`, `tests/core/test_swagger_{linter,discovery,factory_map,report}.py`); архитектурные инварианты остаются под `make swagger-lint` и `make architecture-lint`.
- Удалены архитектурные тесты `tests/contracts/test_public_surface.py` и `tests/core/test_swagger.py` — публичная поверхность и метаданные `@swagger_operation` верифицируются `mypy strict` + `make swagger-lint` + `tests/contracts/test_swagger_contracts.py`.

### Fixed
- Нет изменений.

## [1.0.2] - 2026-04-21

### Added
- Первый публичный релиз changelog для `avito-py`.

### Changed
- Зафиксирована базовая структура истории изменений для следующих фаз исправления STYLEGUIDE.
