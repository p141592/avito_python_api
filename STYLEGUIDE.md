# STYLEGUIDE

## Цель

Этот документ задает единый стиль разработки Python SDK для Avito API.
Цель библиотеки:

- дать понятный и прозрачный публичный API;
- скрыть технические детали авторизации, ретраев и обогащения данных;
- возвращать строго типизированные объекты собственных классов;
- сохранить чистую пакетную архитектуру по разделам Avito API;
- обеспечить предсказуемое поведение при нестабильном соединении.

Документ нормативный. Новые модули и рефакторинг существующего кода должны соответствовать этим правилам.

## Базовые принципы

- Код должен быть читаемым раньше, чем компактным.
- Публичный API библиотеки должен быть простым, внутренние детали должны быть инкапсулированы.
- Каждый слой отвечает только за свою задачу: transport, auth, API clients, domain models, mapping, errors.
- Внешний код не должен работать с сырыми `dict[str, Any]`, если можно вернуть типизированный объект.
- Исключения должны быть явными и доменными, без `assert False` для управления потоком.
- Любое сетевое взаимодействие считается потенциально нестабильным.
- Публичные контракты SDK фиксируются явно и меняются только осознанно.

## Целевая архитектура пакетов

Разделы Avito API оформляются пакетами. Рекомендуемая структура:

```text
avito/
  __init__.py
  client.py
  config.py
  auth/
    __init__.py
    models.py
    provider.py
    settings.py
  core/
    __init__.py
    transport.py
    retries.py
    exceptions.py
    types.py
    pagination.py
  accounts/
    __init__.py
    client.py
    models.py
    mappers.py
  ads/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  promotion/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  messenger/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
  orders/
    __init__.py
    client.py
    models.py
    enums.py
    mappers.py
```

Правила:

- `core/` содержит только общую инфраструктуру, без логики конкретного API-раздела.
- Каждый раздел API живет в отдельном пакете: `ads`, `messenger`, `orders`, `autoload` и т.д.
- В каждом разделе допускаются только модули, относящиеся к этому разделу.
- `avito/client.py` и `avito/__init__.py` содержат только высокоуровневую точку входа и публичные экспорты.

## Публичный API библиотеки

Публичный API должен быть объектным и очевидным:

```python
client = AvitoClient(settings)
profile = client.account().get_self()
listing = client.ad(item_id=42, user_id=123).get()
stats = client.ad_stats(user_id=123).get_item_stats(item_ids=[42])
```

Правила:

- Методы должны отражать действие предметной области, а не детали HTTP.
- Нельзя выносить в публичный API детали `headers`, `token refresh`, `raw request payload`, если в этом нет явной необходимости.
- Публичные методы возвращают доменные модели, коллекции доменных моделей или типизированные result-объекты.
- Сырые ответы API допустимы только во внутренних слоях или в явно обозначенных low-level методах.

### Что считается публичным контрактом SDK

Нормативно в публичный контракт входят:

- пакет `avito` и его экспорты `AvitoClient`, `AvitoSettings`, `AuthSettings`;
- фабрики ресурсов у `AvitoClient`, например `account()`, `ad()`, `ad_stats()`, `promotion_order()`;
- публичные модели из `avito.<domain>.models`;
- typed exceptions из `avito.core.exceptions`;
- lazy pagination контракт `PaginatedList`;
- стабильная сериализация публичных моделей через `to_dict()` и `model_dump()`;
- безопасный diagnostic contract метода `debug_info()`.

Нормативно не входят в публичный контракт:

- transport request/response shapes;
- внутренние mapper-объекты;
- `raw_payload`, служебные dataclass-ы transport-слоя и внутренние DTO;
- shape исходного JSON-ответа Avito API.

Внутренние изменения допустимы, пока публичные сигнатуры, возвращаемые модели, сериализация и типы ошибок остаются стабильными.

## Классы и ответственность

Обязательное разделение:

- `AvitoClient` — корневой фасад SDK.
- `SectionClient` классы — клиенты конкретных API-разделов.
- `Transport` — выполнение HTTP-запросов.
- `AuthProvider` — получение и обновление токена.
- `Mapper` — преобразование JSON в доменные модели.
- `Settings`/`Config` — конфигурация SDK.

Правила:

- Один класс — одна явная зона ответственности.
- Классы не должны одновременно заниматься HTTP, авторизацией, логированием и преобразованием моделей.
- Запрещены "god object" классы с логикой всех API-разделов сразу.

## Dataclass и модели

Основной формат моделей SDK — `dataclass`.

Правила:

- Доменные сущности и объекты ответов описываются через `@dataclass(slots=True, frozen=True)` по умолчанию.
- Если модель должна быть изменяемой, это должно быть осознанным исключением и явно документироваться.
- Для списков использовать конкретные контейнеры: `list[Message]`, а не просто `list`.
- Для необязательных полей использовать `T | None`, а не неявные значения.
- Вложенные структуры тоже должны иметь собственные типизированные dataclass-модели.
- Не использовать `dict` как substitute для модели предметной области.
- Все публичные read/write методы возвращают только нормализованные модели SDK, а не transport-layer объекты.
- Для стабильных публичных моделей должны быть явно определены обязательные и nullable-поля.
- Каждая публичная модель должна предоставлять единообразную сериализацию через `to_dict()` и `model_dump()`.
- Сериализация публичных моделей должна быть JSON-compatible и рекурсивной для вложенных SDK-моделей.
- В публичных моделях запрещены transport/internal implementation fields.

Пример:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class Message:
    id: str
    chat_id: str
    text: str | None
    created_at: datetime
```

## Pydantic и валидация

Для этого проекта `dataclass` — стандарт представления доменных объектов. `pydantic` не должен быть базовым строительным блоком всей модели SDK.

Допустимое использование `pydantic`:

- чтение конфигурации из environment;
- валидация сложного внешнего payload на границе системы, если это действительно упрощает код;
- прототипирование до появления финальной dataclass-модели.

Недопустимое использование:

- смешивать `pydantic.BaseModel` и `dataclass` без четкого слоя ответственности;
- возвращать `BaseModel` как основной публичный формат SDK, если доменная dataclass уже существует.

## Типизация и mypy

Строгая типизация обязательна.

Правила:

- Все функции, методы, атрибуты классов и возвращаемые значения должны быть аннотированы.
- `Any` запрещен, кроме узких boundary-layer мест с локальным объяснением.
- Использовать `mypy` в строгом режиме или максимально близком к нему.
- Использовать `Protocol`, `TypeAlias`, `TypedDict` для границ, где dataclass еще не применим.
- JSON от внешнего API сначала трактуется как boundary-тип, затем маппится в dataclass.
- Не возвращать объединения слишком широких типов вроде `dict | list | str | None`.

Минимальный целевой профиль `mypy`:

```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
disallow_any_generics = true
no_implicit_optional = true
```

## HTTP и transport layer

Весь HTTP должен проходить через единый transport layer.

Правила:

- Прямые вызовы `httpx.get()`/`httpx.post()` внутри section clients запрещены.
- Использовать `httpx.Client` или `httpx.AsyncClient` как внутреннюю зависимость transport-слоя.
- Таймауты задаются явно.
- Заголовки авторизации подставляются transport/auth слоем, а не бизнес-методами.
- Формирование URL, обработка ошибок, retry и логирование концентрируются в transport.
- Transport-детали не должны быть частью публичных сигнатур, docstrings и serialization.

Рекомендация:

- Сначала сделать качественный sync SDK.
- Async-версию добавлять отдельным слоем, а не смешивать sync/async в одних и тех же классах.

## Авторизация

Авторизация должна быть полностью абстрагирована от API-методов.

Правила:

- API-методы не должны сами получать токен.
- Должен существовать отдельный `AuthProvider`, отвечающий за кэш токена, refresh и срок жизни.
- При `401 Unauthorized` transport должен инициировать controlled refresh, а не ломать контракт случайным образом.
- Конфигурация авторизации хранится в `Settings`, а не размазывается по коду.

## Работа с нестабильным соединением

Сеть нестабильна по умолчанию. Это нужно считать частью дизайна.

Правила:

- На transport-уровне должны быть retries с ограничением числа попыток.
- Retry применяется только к безопасным сценариям: timeout, connection errors, временные `5xx`, rate limit при понятной политике.
- Политика retry должна быть централизована и конфигурируема.
- Для всех запросов задаются разумные timeout'ы на connect/read/write.
- Ошибки после исчерпания retry не скрываются, а поднимаются как доменные исключения.
- Логирование retry должно быть информативным, но без утечки секретов.

Минимально ожидаемые сущности:

- `RetryPolicy`
- `ApiTimeouts`
- `TransportError`
- `RateLimitError`
- `AuthorizationError`
- `UpstreamApiError`

## Ошибки и исключения

`assert` не используется для обработки ошибок API.

Правила:

- Для ошибок SDK создается иерархия собственных исключений в `core/exceptions.py`.
- Ошибка должна содержать минимум: `operation`, HTTP status, код ошибки Avito при наличии, человекочитаемое сообщение и безопасные metadata.
- Ошибки 4xx и 5xx должны различаться типами.
- Ошибки парсинга и ошибки transport должны различаться.
- Mapping transport/HTTP/API ошибок в публичные ошибки SDK должен быть централизован.
- Секреты, токены и чувствительные headers должны автоматически санитизироваться в сообщении и metadata.
- Неизвестная ошибка upstream не должна протекать наружу как сырой transport exception.

Пример иерархии:

```python
class AvitoError(Exception): ...
class TransportError(AvitoError): ...
class ValidationError(AvitoError): ...
class AuthorizationError(AvitoError): ...
class RateLimitError(AvitoError): ...
class ConflictError(AvitoError): ...
class UnsupportedOperationError(AvitoError): ...
class UpstreamApiError(AvitoError): ...
class ResponseMappingError(AvitoError): ...
```

Нормативный mapping:

- `400` и `422` маппятся в `ValidationError`, если это соответствует контракту операции;
- `401` и `403` маппятся в `AuthorizationError`;
- `409` маппится в `ConflictError`;
- `429` маппится в `RateLimitError`;
- неподдерживаемая операция приводит к `UnsupportedOperationError`;
- остальные неизвестные ошибки upstream маппятся в `UpstreamApiError`.

## Mapping и преобразование данных

JSON от Avito — это внешний контракт, а не внутренняя модель приложения.

Правила:

- Сырые JSON-ответы маппятся в отдельном слое.
- Логика "обогащения" данных выполняется после transport, но до возврата объекта пользователю.
- Обогащение должно быть детерминированным и не ломать исходный контракт метода.
- Если обогащение дорогое или требует дополнительных запросов, оно должно быть явно обозначено в API.
- Централизовать преобразование transport response в публичные модели SDK.
- Один и тот же ресурс должен маппиться в один и тот же публичный тип независимо от вариаций upstream payload внутри допустимого диапазона.
- Публичные docstring и сигнатуры не должны требовать знания upstream JSON shape.

Рекомендация:

- Использовать `mappers.py` внутри раздела API.
- Не смешивать mapping с HTTP-вызовом в одном методе.

## Публичные read-контракты

Read-операции должны быть выровнены по форме результата, nullable-поведению и неймингу полей.

Правила:

- `account().get_self()` возвращает `AccountProfile`;
- `ad().get(...)` возвращает `Listing`;
- `ad().list(...)` возвращает коллекцию или пагинируемый результат из `Listing`;
- `ad_stats().get_item_stats(...)` возвращает коллекцию `ListingStats`;
- `ad_stats().get_calls_stats(...)` возвращает коллекцию `CallStats`;
- `ad_stats().get_account_spendings(...)` возвращает `AccountSpendings` или иную зафиксированную контрактом SDK модель;
- пустой или частично заполненный upstream payload не должен ломать read-контракт, если модель допускает `None` для отсутствующих значений;
- consumer-код не должен знать структуру raw Avito response для использования read-методов.

Для стабильных публичных read/write результатов нормативно закрепляются следующие canonical типы:

- `AccountProfile`
- `Listing`
- `ListingStats`
- `CallStats`
- `AccountSpendings`
- `PromotionService`
- `PromotionOrder`
- `PromotionForecast`
- `PromotionActionResult`

## Promotion write-контракт

Официально поддерживаемые write-операции продвижения должны иметь единый публичный контракт.

Правила:

- write-операции продвижения принимают `dry_run: bool = False`;
- при `dry_run=True` метод обязан валидировать входные данные, собрать официальный request payload, не выполнять write-запрос и вернуть `PromotionActionResult` со статусом `preview` или `validated`;
- при `dry_run=False` метод обязан использовать тот же payload builder, выполнить write-запрос и вернуть тот же тип `PromotionActionResult`;
- невалидные входные параметры должны приводить к `ValidationError` до вызова transport;
- `request_payload` в результате должен соответствовать фактическому payload write-вызова;
- одинаковые входы в `dry_run=True` и `dry_run=False` должны формировать один и тот же payload.

Стабильный контракт `PromotionActionResult`:

- `action`
- `target`
- `status`
- `applied`
- `request_payload`
- `warnings`
- `upstream_reference`
- `details`

Минимум следующие операции должны следовать этому контракту:

- `bbip_promotion().create_order(...)`
- `ad_promotion().apply_vas(...)`
- `ad_promotion().apply_vas_package(...)`
- `ad_promotion().apply_vas_v2(...)`
- `trx_promotion().apply(...)`
- `trx_promotion().delete(...)`
- `target_action_pricing().update_manual(...)`
- `target_action_pricing().update_auto(...)`
- `target_action_pricing().delete(...)`

## Promotion read-контракт

Read-операции promotion surface должны возвращать только стабильные публичные SDK-модели.

Правила:

- `promotion_order().list_services(...)` возвращает коллекцию `PromotionService`;
- `promotion_order().list_orders(...)` возвращает коллекцию `PromotionOrder`;
- `promotion_order().get_order_status(...)` возвращает результат по зафиксированному контракту SDK;
- `bbip_promotion().get_suggests(...)` и `bbip_promotion().get_forecasts(...)` возвращают стабильные SDK-модели, а не transport shape;
- `target_action_pricing().get_bids(...)` и `target_action_pricing().get_promotions_by_item_ids(...)` возвращают стабильные SDK-модели;
- пустой список upstream корректно возвращается как пустая коллекция SDK-моделей;
- частичный upstream payload корректно маппится в nullable-поля публичных моделей.

## Нейминг

Правила:

- Имена пакетов и модулей: lowercase, короткие и предметные.
- Имена классов: `PascalCase`.
- Имена функций и методов: `snake_case`.
- Имена публичных методов должны описывать бизнес-действие: `get_item`, `list_messages`, `create_discount_campaign`.
- Для публичных моделей использовать canonical имена предметной области, а не внутренние transport aliases.
- Избегать абстрактных имен вроде `utils`, `helpers`, `common2`, `manager2`.

## Конфигурация

Правила:

- Конфигурация SDK выделяется в отдельный модуль: `config.py` или `settings.py`.
- `AvitoSettings` и `AuthSettings` являются единственным официальным способом конфигурации SDK.
- Пользователь SDK должен иметь возможность передать конфигурацию явно через объект настроек.
- Переменные окружения читаются в одном месте через `AvitoSettings.from_env()` и `AuthSettings.from_env()`.
- `AvitoClient.from_env()` является официальным factory method для инициализации клиента из environment.
- Resolution process environment и `.env` должен быть детерминированным и одинаковым для всех entry point.
- Значения из process environment имеют приоритет над `.env`.
- Поддерживаемые env-переменные и alias-имена должны быть задокументированы и считаться частью стабильного config contract.
- Отсутствие обязательных полей конфигурации должно валидироваться до первого HTTP-запроса через typed exceptions с понятными сообщениями.
- Сообщения и metadata ошибок конфигурации не должны содержать секретные значения.

Пример:

```python
@dataclass(slots=True, frozen=True)
class AuthSettings:
    client_id: str
    client_secret: str
    refresh_token: str | None = None


@dataclass(slots=True, frozen=True)
class AvitoSettings:
    auth: AuthSettings
    base_url: str = "https://api.avito.ru"
    user_id: int | None = None
    timeout_seconds: float = 10.0
```

Минимально ожидаемые возможности config contract:

- `AvitoSettings.from_env()`;
- `AuthSettings.from_env()`;
- `AvitoClient.from_env()`;
- явная валидация обязательных auth-полей;
- безопасный `debug_info()` contract без утечки `client_secret`, access token, refresh token и `Authorization` header.

## Пагинация

Публичное поведение lazy pagination должно быть зафиксировано как часть SDK contract.

Правила:

- list-методы, использующие lazy pagination, возвращают результат с list-like коллекцией `PaginatedList` в поле `items`;
- первая страница может быть уже загружена в момент получения результата;
- чтение первых `N` элементов не должно загружать все страницы сразу;
- итерация по первым `N` элементам должна выполнять только необходимое число page-запросов;
- полная материализация должна выполняться явным вызовом, например `items.materialize()`;
- пустая коллекция должна работать без лишних запросов;
- ошибка последующей страницы должна пробрасываться в момент чтения этой страницы;
- повторный доступ к уже загруженным элементам не должен инициировать повторный fetch, если кэширование объявлено частью контракта.

Если поверх пагинации нужны дополнительные утилиты, они должны быть частью публичного SDK contract, а не внешними helper-функциями.

## Сериализация

Публичные модели SDK должны безопасно и единообразно сериализоваться без внешних helper-ов.

Правила:

- каждая публичная модель сериализуется стандартным SDK-методом;
- результат сериализации должен быть JSON-compatible;
- вложенные публичные модели должны сериализоваться рекурсивно;
- nullable и optional-поля сериализуются по правилам зафиксированного контракта;
- сериализация не должна раскрывать transport-объекты, служебные ссылки и внутренние mapper-поля.

## Логирование

Правила:

- Логирование должно быть структурным и полезным для диагностики.
- Нельзя логировать `client_secret`, access token, refresh token, полный authorization header и иные секреты.
- На уровне info/debug можно логировать endpoint, attempt number, latency, status code и operation name.
- Пользователь SDK должен иметь возможность отключить или перенаправить логирование.
- Диагностические снимки, например `debug_info()`, должны считаться безопасными по умолчанию.

## Докстринги и комментарии

Правила:

- Публичные классы и методы должны иметь короткие docstring с описанием контракта.
- Docstring публичного метода должен описывать возвращаемую SDK-модель и поведение на nullable/empty cases.
- Комментарии используются только там, где нельзя выразить намерение кодом.
- Комментарии не должны дублировать очевидное.

## Тестируемость

Style guide ориентирован на код, который легко тестировать.

Правила:

- Внешние зависимости передаются через конструктор.
- Нельзя захардкодить сетевые вызовы так, чтобы их нельзя было подменить в тестах.
- Transport, auth provider и section clients должны тестироваться отдельно.
- Mapping должен покрываться unit-тестами на реальных примерах Avito payload.
- Для unit/regression тестирования публичного SDK должен использоваться единый mock/fake transport.
- Для ключевых публичных моделей и результатов операций обязательны contract/snapshot tests.
- Для публичных read/write методов обязательны happy-path тесты через mock transport.
- Для write-методов с `dry_run` обязательны отдельные тесты, подтверждающие отсутствие write-вызова и идентичность payload builder.
- Typed error mapping должен быть покрыт отдельными тестами по статус-кодам и unsupported-сценариям.
- Lazy pagination должна покрываться regression-тестами на частичную итерацию, полную материализацию, пустую коллекцию и ошибку на последующих страницах.
- Сериализация публичных моделей должна покрываться отдельными contract-тестами.

## Импорты и зависимости

Правила:

- Использовать абсолютные импорты внутри пакета.
- Избегать циклических зависимостей между пакетами API-разделов.
- Зависимости должны быть минимально необходимыми.
- Если стандартная библиотека решает задачу без потери качества, сторонняя библиотека не нужна.

## Чего в проекте быть не должно

- Глобального состояния токена без контролируемого владельца.
- Методов, возвращающих неструктурированный JSON в основном API.
- Смешения transport, auth, parsing и domain logic в одном классе.
- Неаннотированных публичных методов.
- Широкого использования `Any`.
- Обработки ошибок через `assert`.
- Скрытых сетевых побочных эффектов в свойствах и dataclass.
- Утечки transport-layer shapes и mapper-деталей в публичные сигнатуры и модели.
- Неявного или недокументированного config resolution через environment.

## Практический вывод для текущего репозитория

При дальнейшем рефакторинге проекта нужно двигаться в сторону следующей модели:

- заменить текущие `BaseModel` доменные сущности на `dataclass`;
- вынести HTTP и retry в `core/transport.py`;
- вынести авторизацию в отдельный пакет `auth/`;
- разбить API по предметным пакетам вместо одной общей клиентской реализации;
- ввести строгую конфигурацию `mypy`;
- заменить сырые словари ответа на собственные типизированные модели;
- закрепить `AvitoSettings` и `AuthSettings` как единственный config contract;
- закрепить стабильные публичные модели, serialization contract и lazy pagination semantics;
- унифицировать promotion read/write surface, включая `dry_run`;
- заменить `assert` на иерархию typed exceptions SDK и централизованный error mapping.

Этот документ является базовым стандартом для всех следующих изменений в проекте.
