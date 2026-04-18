# TODO

## Цель

Полностью реализовать SDK для всех методов, описанных в `docs/*.json`, с архитектурой, строго соответствующей `STYLEGUIDE.md`:

- публичный API только через объектный фасад `AvitoClient`;
- один публичный клиент без дерева section clients в пользовательском API;
- отдельные слои `auth`, `core`, `domain objects`, `mappers`, `errors`;
- публичные ответы только как `@dataclass(slots=True, frozen=True)`;
- единый transport на `httpx.Client`;
- централизованные retries, timeouts, обработка `401`, `4xx`, `5xx`, rate limit;
- отсутствие `assert` и сырых `dict[str, Any]` в публичном API.
- пользовательская документация репозитория и docstring публичных сущностей должны быть на русском языке.

Целевая форма пользовательского API:

```python
avito = AvitoClient(...)
ad = avito.ad(item_id).get()
avito.account(user_id).get_balance()
avito.chat(chat_id, user_id=user_id).send_message(...)
```

Доменные объекты создаются через один клиент и инкапсулируют операции своей предметной области. В публичном API не должно быть сценариев вида `client.ads.get(...)`, `client.orders.list(...)` или `client.messenger.send(...)`.

## Полный охват документации

Нужно покрыть все разделы из `docs/`:

- `auth`: Авторизация, а также отдельный токен в `Автотека`.
- `accounts`: Информация о пользователе, Иерархия аккаунтов.
- `ads`: Объявления, Автозагрузка.
- `messenger`: Мессенджер, Рассылка скидок и спецпредложений.
- `promotion`: Продвижение, TrxPromo, CPA-аукцион, Настройка цены целевого действия, Автостратегия.
- `orders`: Управление заказами, Доставка, Управление остатками.
- `jobs`: Авито.Работа.
- `cpa`: CPA Авито, CallTracking.
- `autoteka`: все операции по превью, отчетам, скорингу, мониторингу, тизерам, оценке.
- `realty`: Краткосрочная аренда, Аналитика по недвижимости.
- `ratings`: Рейтинги и отзывы.
- `tariffs`: Тарифы.

Deprecated-методы из swagger не пропускать: реализовать как отдельные legacy-методы с явной пометкой в docstring и тестах.

## Явная матрица покрытия docs -> SDK

Ниже зафиксировано соответствие каждого документа и его endpoint-групп будущим пакетам SDK. Это обязательная часть плана, а не задача "на потом".

| Документ | Операции | Пакет SDK | Доменный объект | Этап |
| --- | ---: | --- | --- | ---: |
| `docs/Авторизация.json` | 3 | `auth` | `AvitoClient.auth()` и внутренние token flow-объекты | 3 |
| `docs/Информацияопользователе.json` | 3 | `accounts` | `Account` | 4 |
| `docs/ИерархияАккаунтов.json` | 5 | `accounts` | `AccountHierarchy` | 4 |
| `docs/Объявления.json` | 11 | `ads` | `Ad`, `AdStats`, `AdPromotion` | 4 |
| `docs/Автозагрузка.json` | 17 | `ads` | `AutoloadProfile`, `AutoloadReport`, `AutoloadLegacy` | 4 |
| `docs/Мессенджер.json` | 13 | `messenger` | `Chat`, `ChatMessage`, `ChatWebhook`, `ChatMedia` | 5 |
| `docs/Рассылкаскидокиспецпредложенийвмессенджере.json` | 5 | `messenger` | `SpecialOfferCampaign` | 5 |
| `docs/Продвижение.json` | 7 | `promotion` | `PromotionOrder`, `BbipPromotion` | 6 |
| `docs/TrxPromo.json` | 3 | `promotion` | `TrxPromotion` | 6 |
| `docs/CPA-аукцион.json` | 2 | `promotion` | `CpaAuction` | 6 |
| `docs/Настройкаценыцелевогодействия.json` | 5 | `promotion` | `TargetActionPricing` | 6 |
| `docs/Автостратегия.json` | 7 | `promotion` | `AutostrategyCampaign` | 6 |
| `docs/Управлениезаказами.json` | 12 | `orders` | `Order`, `OrderLabel` | 7 |
| `docs/Доставка.json` | 31 | `orders` | `DeliveryOrder`, `SandboxDelivery`, `DeliveryTask` | 7 |
| `docs/Управлениеостатками.json` | 2 | `orders` | `Stock` | 7 |
| `docs/АвитоРабота.json` | 25 | `jobs` | `Vacancy`, `Application`, `Resume`, `JobWebhook`, `JobDictionary` | 8 |
| `docs/CPAАвито.json` | 11 | `cpa` | `CpaLead`, `CpaChat`, `CpaCall`, `CpaLegacy` | 9 |
| `docs/CallTracking[КТ].json` | 3 | `cpa` | `CallTrackingCall` | 9 |
| `docs/Автотека.json` | 27 | `autoteka` | `AutotekaVehicle`, `AutotekaReport`, `AutotekaMonitoring`, `AutotekaScoring`, `AutotekaValuation` | 10 |
| `docs/Краткосрочнаяаренда.json` | 5 | `realty` | `RealtyListing`, `RealtyBooking`, `RealtyPricing` | 11 |
| `docs/Аналитикапонедвижимости.json` | 2 | `realty` | `RealtyAnalyticsReport` | 11 |
| `docs/Рейтингииотзывы.json` | 4 | `ratings` | `Review`, `ReviewAnswer`, `RatingProfile` | 11 |
| `docs/Тарифы.json` | 1 | `tariffs` | `Tariff` | 11 |

Правила полноты:

- Для каждого endpoint из таблицы в `docs/inventory.md` должны быть зафиксированы:
  - HTTP method;
  - path;
  - swagger summary;
  - target package;
  - target domain object;
  - публичный метод SDK;
  - признак `legacy/deprecated`;
  - тип request/response модели;
  - тесты, покрывающие endpoint.
- Этап считается закрытым только если все endpoints из соответствующих строк таблицы получили конкретные методы SDK и тесты.
- Любой endpoint из `docs/*.json`, который не попал в таблицу или в inventory, считается пропуском плана.

## Проверка соответствия swagger

Покрытие `docs/*.json` должно не только существовать в inventory, но и регулярно проверяться на консистентность.

- Для каждого swagger-документа нужно зафиксировать число операций и их соответствие inventory.
- Для каждого endpoint нужно проверять совпадение:
  - HTTP method;
  - path;
  - deprecated-статуса;
  - основных request/response схем на уровне, достаточном для выявления расхождений SDK с документацией.
- Любое расхождение между swagger и `docs/inventory.md` считается дефектом плана и должно исправляться до расширения SDK.
- Если swagger содержит неоднозначность или явную ошибку, это должно быть отдельно отмечено в inventory с пояснением принятой нормализации.
- Для inventory и матрицы покрытия нужна отдельная проверка в тестах или validation script, которую можно запускать перед релизом.

## Целевая структура пакетов

```text
avito/
  __init__.py
  client.py
  config.py
  auth/
  core/
  accounts/
  ads/
  messenger/
  promotion/
  orders/
  jobs/
  cpa/
  autoteka/
  realty/
  ratings/
  tariffs/
```

В каждом доменном пакете:

- `domain.py` с доменными объектами и их операциями;
- `models.py` с dataclass-моделями;
- `enums.py` для строковых констант API;
- `mappers.py` для JSON -> dataclass;
- при необходимости `requests.py` или `filters.py` для typed request-моделей.

## Общие правила реализации

- Все JSON-ответы сначала описывать как boundary-типы (`TypedDict`), затем маппить в dataclass.
- Для списков, пагинации, batch-операций и task-based API делать отдельные result-модели.
- Для бинарных ответов выделить типизированные low-level сущности:
  - аудиозаписи звонков;
  - PDF этикеток;
  - загрузка изображений и файлов.
- Для webhook-операций сделать отдельные request/result модели и контрактные тесты сериализации.
- Для sandbox-методов `delivery` сохранить отдельный `SandboxDeliveryClient`, не смешивая с production API.
- Для `x-gateway`, rate-limiter и нестандартных заголовков добавить расширяемую конфигурацию transport, но скрыть детали от публичного API.
- Сохранять обратную совместимость с текущим кодом не требуется: при конфликте старой структуры с новой архитектурой приоритет всегда у новой архитектуры из `STYLEGUIDE.md`.
- Каждый публичный и внутренний класс должен иметь короткий обязательный docstring с описанием ответственности и контракта.
- Пользовательская документация репозитория, `docs/*.md`, README и docstring публичных сущностей ведутся на русском языке.
- Аномалии в swagger нормализовать в inventory:
  - дубли `/token` с невидимыми символами;
  - deprecated-версии;
  - неоднородные path/query/body схемы;
  - операции, возвращающие task id для последующего polling.

## Этап 1. Инвентаризация swagger и каркас SDK

Что сделать:

- Создать `docs/inventory.md` с перечнем всех операций: section, HTTP method, path, swagger summary, статус `deprecated`, пакет SDK, domain object, публичный метод SDK, тип request, тип response, тип теста.
- Зафиксировать единый mapping `docs/*.json -> package/module`.
- Удалить текущую смесь логики из `avito/client/client.py` и заменить на один минимальный клиент, совместимый с новой архитектурой.
- Создать пакеты `auth`, `core` и доменные пакеты-заготовки.
- Ввести единый стиль именования фабрик и методов доменных объектов:
  - `avito.account(...)`, `avito.ad(...)`, `avito.chat(...)`, `avito.order(...)`, `avito.tariff(...)`;
  - `get_*`, `list_*`, `create_*`, `update_*`, `delete_*`, `apply_*`, `download_*`, `get_*_by_*`.

Тесты:

- Smoke-тест импорта `AvitoClient`.
- Тест структуры единого клиента: `avito.account(...)`, `avito.ad(...)`, `avito.chat(...)`, `avito.order(...)` и другие доменные фабрики доступны как методы одного клиента.
- Тест проверки соответствия `docs/inventory.md` исходным swagger-документам.

Критерии готовности:

- В репозитории есть полный inventory по всем swagger-операциям.
- Inventory доказывает соответствие `каждый endpoint -> конкретный метод SDK -> конкретный тест`.
- Новая пакетная структура создана.
- Старый god-object больше не является точкой дальнейшей разработки, а новый единый клиент является единственной публичной точкой входа.

## Этап 2. Core: config, exceptions, transport, retries, pagination

Что сделать:

- Вынести настройки в `config.py` и `auth/settings.py` на `pydantic-settings`.
- Реализовать:
  - `ApiTimeouts`;
  - `RetryPolicy`;
  - `Transport`;
  - `RequestContext`;
  - `Paginator` или page/result abstractions;
  - иерархию исключений из `STYLEGUIDE.md`.
- Добавить нормализацию URL и кодирование path/query параметров.
- Реализовать базовую обработку:
  - `401 -> controlled token refresh`;
  - `429 -> RateLimitError` или retry по политике;
  - `5xx -> retry + ServerError`;
  - mapping errors -> `ResponseMappingError`.
- Поддержать JSON, multipart upload, binary download.

Тесты:

- Unit-тесты таймаутов, retry-решений и классификации ошибок.
- Тест refresh токена после `401` с повтором запроса.
- Тест, что неидемпотентные запросы не ретраятся без явного разрешения.
- Тест бинарного ответа и multipart upload.
- Тест пагинации и сборки типизированного page result.

Критерии готовности:

- Ни один доменный объект не делает прямой вызов `httpx` или `requests`.
- Все сетевые ошибки поднимаются как доменные исключения.
- Transport покрыт regression-тестами на основные ветки поведения.

## Этап 3. Auth provider и аутентификация

Что сделать:

- Реализовать `AuthProvider` с кешем access token и временем жизни.
- Поддержать:
  - client credentials;
  - refresh token flow;
  - отдельный auth flow для `Автотека`, если он отличается по контракту.
- Нормализовать дубли `/token` из swagger в один публичный API с legacy-alias при необходимости.
- Добавить low-level модели токенов и auth errors.

Тесты:

- Успешное получение access token.
- Успешный refresh token.
- Ошибка авторизации маппится в `AuthenticationError`.
- Дублирующиеся swagger-path не ломают публичный интерфейс.

Критерии готовности:

- Ни один API-метод не получает токен самостоятельно.
- Обновление токена происходит централизованно и прозрачно для доменных объектов.

## Этап 4. Базовые account- и ads-разделы

Покрыть разделы:

- `Информация о пользователе`
- `Иерархия Аккаунтов`
- `Объявления`
- `Автозагрузка`

Что сделать:

- Реализовать доменные объекты `Account`, `AccountHierarchy`, `Ad`, `AdStats`, `AdPromotion`, `AutoloadProfile`, `AutoloadReport`.
- В `accounts` покрыть:
  - `self`;
  - `balance`;
  - `operations_history`;
  - статус пользователя в ИА;
  - сотрудников;
  - телефоны компании;
  - связь объявлений и сотрудников;
  - список объявлений сотрудника.
- В `ads` покрыть:
  - получение одного объявления и списка объявлений;
  - статистику по объявлениям и расходам;
  - call stats;
  - обновление цены;
  - применение VAS и VAS packages;
  - цены на услуги продвижения;
  - все отчеты и profile API автозагрузки;
  - `ad_ids`, `avito_ids`, tree/fields, upload by URL.
- Для deprecated операций автозагрузки сделать `legacy`-объект или `legacy`-методы с явным именованием.

Тесты:

- Mapping-тесты на все основные модели объявлений, статистики, spendings и autoload reports.
- Тесты query/body/path параметров для фильтров и batch-операций.
- Тесты deprecated wrappers, что они помечены и вызывают правильный endpoint.
- Тесты upload/profile/report flows автозагрузки.

Критерии готовности:

- Пользователь может пройти сценарий `avito.account(user_id).get_self()`, `avito.ad(item_id).get()`, `avito.ad(item_id).get_stats(...)`, `avito.autoload_report(report_id).get()`.
- Все ответы этого блока возвращают dataclass-модели, а не `dict`.

## Этап 5. Messenger и messaging-adjacent API

Покрыть разделы:

- `Мессенджер`
- `Рассылка скидок и спецпредложений в мессенджере`

Что сделать:

- Реализовать `MessengerClient` и вложенный `SpecialOffersClient`.
- Покрыть:
  - список чатов;
  - чат по ID;
  - сообщения V3;
  - отправку текста;
  - отправку изображения;
  - удаление сообщения;
  - отметку чата как прочитанного;
  - voice files;
  - upload images;
  - blacklist;
  - webhook subscribe/unsubscribe/list;
  - available offers, draft create, confirm, stats, tariff info.
- Отдельно спроектировать модели для webhook subscription и media upload results.

Тесты:

- Контрактные тесты сериализации webhook payload и subscribe/unsubscribe flows.
- Тесты multipart/image upload.
- Mapping-тесты чатов, сообщений и голосовых файлов.
- Интеграционные мок-тесты цепочки `upload image -> send image message`.
- Тесты offer campaign flow: `available -> multiCreate -> multiConfirm`.

Критерии готовности:

- Пользователь может пройти end-to-end сценарий переписки и рассылки без обращения к raw HTTP.
- Все webhook-методы имеют стабильные typed request/result модели.

## Этап 6. Promotion stack

Покрыть разделы:

- `Продвижение`
- `TrxPromo`
- `CPA-аукцион`
- `Настройка цены целевого действия`
- `Автостратегия`

Что сделать:

- Реализовать `PromotionClient` и при необходимости вложенные клиенты:
  - `BbipClient`;
  - `TrxPromoClient`;
  - `CpaAuctionClient`;
  - `TargetActionPriceClient`;
  - `AutostrategyClient`.
- Покрыть:
  - словари услуг, список услуг, заявки, статусы заявок;
  - прогнозы, budget suggests, подключение услуг;
  - apply/cancel/commissions для TrxPromo;
  - get/save bids для аукциона;
  - get bids, promotions by item ids, remove, set auto/manual;
  - budget calculation, create/edit/info/stop/list/stat кампаний.
- Выделить общие модели бюджетов, ставок, кампаний и заявок.

Тесты:

- Mapping-тесты бюджетов, ставок, кампаний и статусов заявок.
- Тесты на идемпотентность и корректный HTTP method (`PUT` против `POST`) для подключения услуг.
- Тесты batch-операций по нескольким объявлениям.
- Тесты legacy/deprecated, если в ответах есть старые формы.

Критерии готовности:

- Все promotion API доступны из одного доменного блока без дублирования transport-логики.
- Публичный API отражает предметные действия, а не названия raw endpoints.

## Этап 7. Orders, delivery, stock management

Покрыть разделы:

- `Управление заказами`
- `Доставка`
- `Управление остатками`

Что сделать:

- Реализовать `OrdersClient`, `DeliveryClient`, `SandboxDeliveryClient`, `StockClient`.
- В `orders` покрыть:
  - получение заказов;
  - transitions;
  - confirmation code;
  - cnc details;
  - courier ranges;
  - tracking number;
  - return order;
  - markings;
  - labels tasks;
  - labels PDF download.
- В `delivery` покрыть production и sandbox сценарии:
  - announcement create/cancel/track;
  - parcel create/cancel/change/info;
  - tariff/terminals/areas/sorting centers;
  - prohibit acceptance;
  - custom schedule;
  - tasks polling;
  - change result callbacks.
- В `stock` покрыть info и update stocks.

Тесты:

- Тесты бинарной загрузки PDF-этикеток.
- Тесты polling long-running tasks по `task_id`.
- Тесты sandbox/prod route separation.
- Mapping-тесты заказов, маркировок, диапазонов доставки, посылок, тарифов и остатков.
- Тесты optimistic retry only for safe polling requests.

Критерии готовности:

- Production и sandbox API доставки не смешаны в одном наборе методов.
- Пользователь может получить PDF-этикетку и обработать lifecycle заказа через typed API.

## Этап 8. Jobs API

Покрыть раздел:

- `Авито.Работа`

Что сделать:

- Реализовать `JobsClient` с подразделами:
  - `VacanciesClient`;
  - `ApplicationsClient`;
  - `ResumesClient`;
  - `WebhookClient`;
  - `DictionariesClient`.
- Покрыть обе версии вакансий и резюме:
  - publish/edit/archive/prolongate;
  - v2 create/update/statuses/batch/get/list/auto_renewal;
  - applications ids/by_ids/states/apply_actions/set_is_viewed;
  - webhook CRUD/list;
  - resumes search/get/get contacts;
  - vacancy dictionaries.
- Развести `v1` и `v2` модели там, где контракт реально отличается.

Тесты:

- Mapping-тесты вакансий, резюме, откликов, словарей и статусов публикации.
- Тесты batch vacancy flows.
- Тесты webhook CRUD.
- Тесты, что `v1` и `v2` не смешивают несовместимые поля.

Критерии готовности:

- Полный lifecycle вакансии и отклика покрыт публичным API.
- Версионные различия инкапсулированы в моделях и клиентах, а не размазаны по условным `dict`.

## Этап 9. CPA и CallTracking

Покрыть разделы:

- `CPA Авито`
- `CallTracking[КТ]`

Что сделать:

- Реализовать `CpaClient` и `CallTrackingClient`.
- Покрыть:
  - chat by action id;
  - chats by time `v1` deprecated и `v2`;
  - call by id `v1` deprecated и `v2`;
  - calls by time;
  - complaints;
  - phones info from chats;
  - balance info `v2` deprecated и `v3`;
  - calltracking get call, get calls, get record.
- Для аудиофайлов и записей звонков ввести typed binary result.

Тесты:

- Mapping-тесты звонков, чатов, балансов и complaint responses.
- Тесты legacy wrappers на deprecated endpoints.
- Тесты бинарной выдачи аудиозаписи звонка.
- Тесты временных фильтров и batch phone info requests.

Критерии готовности:

- Все CPA и call tracking методы доступны из отдельных логически чистых клиентов.
- Deprecated API поддержаны без загрязнения основного современного интерфейса.

## Этап 10. Autoteka

Покрыть раздел:

- `Автотека`

Что сделать:

- Реализовать `AutotekaClient` с подразделами:
  - `CatalogClient`;
  - `PreviewClient`;
  - `ReportClient`;
  - `ScoringClient`;
  - `SpecificationsClient`;
  - `MonitoringClient`;
  - `TeaserClient`;
  - `ValuationClient`;
  - `PackageClient`.
- Покрыть:
  - resolve catalogs;
  - active package;
  - all preview creation variants;
  - previews by id;
  - reports, reports by vehicle id, report list, report by id;
  - sync reports by regnumber/vin;
  - scoring create/get;
  - specification create/get;
  - monitoring add/remove/delete/get events;
  - teasers create/get;
  - valuation;
  - leads/signal events.
- Отдельно оформить auth-требования, если токен автотеки живет отдельно.

Тесты:

- Mapping-тесты всех крупных сущностей: preview, report, scoring, specification, teaser, package balance, monitoring event.
- Тесты нескольких альтернативных request-моделей для одного бизнес-действия.
- Тесты polling/report retrieval после create.
- Тесты auth boundary для отдельного токена автотеки.

Критерии готовности:

- Сложный большой API разбит на малые доменные объекты и mappers.
- Пользователь может последовательно пройти сценарий `preview -> report -> scoring/specification`.

## Этап 11. Realty, ratings, tariffs

Покрыть разделы:

- `Краткосрочная аренда`
- `Аналитика по недвижимости`
- `Рейтинги и отзывы`
- `Тарифы`

Что сделать:

- Реализовать `RealtyClient`, `RatingsClient`, `TariffsClient`.
- В `realty` покрыть:
  - bookings get/fill;
  - prices update for periods;
  - intervals fill;
  - base params set;
  - market price correspondence;
  - analytics report create.
- В `ratings` покрыть rating info, reviews pagination, create/delete answer.
- В `tariffs` покрыть transport tariff info.

Тесты:

- Mapping-тесты броней, периодов, аналитических отчетов, отзывов, рейтинга, tariff info.
- Тест пагинации отзывов.
- Тесты mutation-сценариев answer create/delete и booking update.
- Тесты path params для itemId/price/report create.

Критерии готовности:

- Все remaining sections из `docs/` реализованы.
- Нет разделов swagger без соответствующего доменного объекта.

## Этап 12. Сквозная стабилизация, документация и релизный gate

Что сделать:

- Добавить `pytest`, `respx` или аналог для HTTP mocking, `mypy`, `ruff`.
- Зафиксировать `mypy` в strict-режиме или профиле, эквивалентном требованиям `STYLEGUIDE.md`.
- Довести покрытие unit + contract tests до уровня, достаточного для безопасного рефакторинга.
- Добавить обязательные примеры использования публичных методов:
  - короткие примеры в docstring или рядом с методом там, где это уместно;
  - сценарные примеры в `README.md` по всем основным доменам;
  - не менее одного end-to-end примера на каждый крупный пакет SDK.
- Добавить changelog-политику и release checklist.
- Подготовить минимальные low-level debugging hooks, не нарушающие публичный API.
- Запустить финальную ревизию имен методов и моделей, чтобы в API не осталось HTTP-терминов без необходимости.

Тесты:

- `poetry run pytest`
- `poetry run mypy avito`
- `poetry run ruff check .`
- `poetry build`
- Проверка, что конфиг `mypy` соответствует минимальному strict-профилю из `STYLEGUIDE.md`: `strict = true`, `warn_unused_ignores = true`, `warn_redundant_casts = true`, `warn_return_any = true`, `disallow_any_generics = true`, `no_implicit_optional = true`.

Критерии готовности:

- Все этапы выше закрыты.
- Все swagger-разделы имеют реализованные доменные объекты, модели, мапперы и тесты.
- `mypy` работает в strict-режиме или эквивалентном профиле, соответствующем `STYLEGUIDE.md`.
- Сборка пакета проходит стабильно.
- Все классы задокументированы обязательными docstring.
- README показывает объектный API, соответствующий `STYLEGUIDE.md`, и содержит примеры использования ключевых методов.

## Матрица покрытия по пакетам

- `auth`: Авторизация, Autoteka token.
- `accounts`: Информация о пользователе, Иерархия аккаунтов.
- `ads`: Объявления, Автозагрузка.
- `messenger`: Мессенджер, Special offers.
- `promotion`: Продвижение, TrxPromo, CPA-аукцион, Целевое действие, Автостратегия.
- `orders`: Управление заказами, Доставка, Управление остатками.
- `jobs`: Авито.Работа.
- `cpa`: CPA Авито, CallTracking.
- `autoteka`: Автотека.
- `realty`: Краткосрочная аренда, Аналитика по недвижимости.
- `ratings`: Рейтинги и отзывы.
- `tariffs`: Тарифы.

## Определение готовности проекта

Проект считается завершенным только если одновременно выполнено все ниже:

- каждый endpoint из `docs/*.json` сопоставлен публичному или legacy-методу SDK;
- это соответствие зафиксировано в `docs/inventory.md` и проверяемо по тестам;
- ни один публичный метод не возвращает сырой JSON;
- transport/auth/errors/retries изолированы от доменных клиентов;
- для каждого этапа есть regression-тесты;
- deprecated API явно отделены и задокументированы;
- строгая типизация подтверждена `mypy` strict или эквивалентным профилем из `STYLEGUIDE.md`;
- `poetry build` и полный тестовый набор проходят без ручных правок.
