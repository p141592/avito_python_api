# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [Unreleased]

### Changed
- Централизовано выполнение схемы `request + map` через `Transport.request_public_model`.
- Убраны прямые обращения доменных клиентов к `request_json` и приватному `Transport._auth_provider`.
- Секционные клиенты переведены на `@dataclass(slots=True, frozen=True)`.
- Иерархия исключений упрощена до frozen dataclass без кастомного `__setattr__`.
- Публичные сигнатуры `accounts`, `ads`, `autoteka`, `cpa`, `jobs`, `messenger`, `orders`, `promotion`, `ratings` и `realty` переведены с `request`-DTO на keyword-only примитивы и коллекции.
- Transport получил поддержку `Idempotency-Key`; публичные write-методы во всех доменах принимают `idempotency_key`, а dry-run/write-контракт promotion покрыт тестами.
- Во всех доменных пакетах добавлены `enums.py`; `accounts`, `ads`, `autoteka`, `jobs`, `messenger`, `orders`, `promotion`, `ratings`, `realty` и `tariffs` переведены на typed enums с fallback на `UNKNOWN` и warning-логом ровно один раз на неизвестное upstream-значение.

## [1.0.2] - 2026-04-21

### Added
- Первый публичный релиз changelog для `avito-py`.

### Changed
- Зафиксирована базовая структура истории изменений для следующих фаз исправления STYLEGUIDE.
