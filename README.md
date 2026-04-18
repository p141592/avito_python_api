# SDK для Avito

[![CI](https://github.com/p141592/avito/actions/workflows/ci.yml/badge.svg)](https://github.com/p141592/avito/actions/workflows/ci.yml)

`avito-py` — Python SDK для работы с Avito API через единый объектный фасад `AvitoClient`.

Цели SDK:

- скрыть transport, OAuth и retry-логику от пользовательского кода;
- возвращать типизированные `dataclass`-модели вместо сырого JSON;
- дать единый вход в доменные сценарии вида `avito.ad(...).get()` и `avito.chat(...).send_message(...)`;
- покрыть все swagger-документы из каталога [docs](docs).

## Установка

```bash
poetry add avito-py
```

или

```bash
pip install avito-py
```

Требование к интерпретатору: Python `3.14` и выше в рамках ветки `3.x`. Репозиторий и релизный контур валидируются именно на Python `3.14`.

## Быстрый старт

Получение ключей - https://www.avito.ru/professionals/api

```python
from avito import AvitoClient

with AvitoClient() as avito:
    profile = avito.account().get_self()
    ad = avito.ad(42).get()

print(profile.name)
print(ad.title)
```

По умолчанию настройки читаются из переменных окружения с префиксом `AVITO_`.

Официальный способ конфигурации SDK:

```python
from avito import AuthSettings, AvitoClient, AvitoSettings

settings = AvitoSettings(
    base_url="https://api.avito.ru",
    user_id=123,
    auth=AuthSettings(
        client_id="client-id",
        client_secret="client-secret",
    ),
)
client = AvitoClient(settings)
```

Инициализация из окружения и `.env`:

```python
from avito import AvitoClient, AvitoSettings

settings = AvitoSettings.from_env()
client = AvitoClient.from_env()
```

Поддерживаемые env-переменные и alias-имена:

- `AVITO_BASE_URL`, alias: `BASE_URL`
- `AVITO_USER_ID`, alias: `USER_ID`
- `AVITO_AUTH__CLIENT_ID`, alias: `AVITO_CLIENT_ID`, `CLIENT_ID`
- `AVITO_AUTH__CLIENT_SECRET`, alias: `AVITO_CLIENT_SECRET`, `AVITO_SECRET`, `CLIENT_SECRET`, `SECRET`
- `AVITO_AUTH__REFRESH_TOKEN`, alias: `AVITO_REFRESH_TOKEN`, `REFRESH_TOKEN`
- `AVITO_AUTH__SCOPE`, alias: `AVITO_SCOPE`, `SCOPE`
- `AVITO_AUTH__TOKEN_URL`, alias: `AVITO_TOKEN_URL`, `TOKEN_URL`
- `AVITO_AUTH__LEGACY_TOKEN_URL`, alias: `AVITO_LEGACY_TOKEN_URL`, `LEGACY_TOKEN_URL`
- `AVITO_AUTH__AUTOTEKA_TOKEN_URL`, alias: `AVITO_AUTOTEKA_TOKEN_URL`, `AUTOTEKA_TOKEN_URL`
- `AVITO_AUTH__AUTOTEKA_CLIENT_ID`, alias: `AVITO_AUTOTEKA_CLIENT_ID`, `AUTOTEKA_CLIENT_ID`
- `AVITO_AUTH__AUTOTEKA_CLIENT_SECRET`, alias: `AVITO_AUTOTEKA_CLIENT_SECRET`, `AUTOTEKA_CLIENT_SECRET`
- `AVITO_AUTH__AUTOTEKA_SCOPE`, alias: `AVITO_AUTOTEKA_SCOPE`, `AUTOTEKA_SCOPE`

Правила resolution:

- значения из process environment имеют приоритет над `.env`;
- `AvitoSettings.from_env()` и `AvitoClient.from_env()` детерминированно читают `.env` из текущей рабочей директории или из переданного `env_file`;
- при отсутствии `client_id` или `client_secret` SDK завершает инициализацию с typed-ошибкой `ConfigurationError`.

## Примеры по доменам

### Аккаунт и объявления

```python
from avito import AvitoClient

with AvitoClient() as avito:
    account = avito.account(user_id=123)
    balance = account.get_balance()
    ad = avito.ad(item_id=42, user_id=123).get()
    stats = avito.ad_stats(item_id=42, user_id=123).get()
```

### Автозагрузка

```python
from avito import AvitoClient

with AvitoClient() as avito:
    profile = avito.autoload_profile(user_id=123).get()
    report = avito.autoload_report(report_id=777).get()
```

### Мессенджер

```python
from avito import AvitoClient
from avito.messenger import UploadImageFile

with AvitoClient() as avito:
    chats = avito.chat(user_id=123).list()
    message = avito.chat(chat_id="chat-1", user_id=123).send_message(message="Здравствуйте")
    uploaded = avito.chat_media(user_id=123).upload_images(
        files=[
            UploadImageFile(
                field_name="image",
                filename="photo.jpg",
                content=b"...",
                content_type="image/jpeg",
            )
        ]
    )
    subscriptions = avito.chat_webhook().list()
```

### Продвижение

```python
from avito import AvitoClient

with AvitoClient() as avito:
    services = avito.promotion_order().list_orders()
    forecast = avito.bbip_promotion(item_id=42).get_forecasts(items=[])
    campaign = avito.autostrategy_campaign(campaign_id=15).get()
```

### Заказы и доставка

```python
from avito import AvitoClient

with AvitoClient() as avito:
    order = avito.order(order_id=100500).get()
    label = avito.order_label(task_id="task-1").download()
    sandbox = avito.sandbox_delivery(task_id="task-1").get()
```

### Работа

```python
from avito import AvitoClient
from avito.jobs import ApplicationIdsQuery, ResumeSearchQuery

with AvitoClient() as avito:
    vacancies = avito.vacancy().list()
    applications = avito.application().list(
        query=ApplicationIdsQuery(updated_at_from="2026-04-18")
    )
    resumes = avito.resume().list(query=ResumeSearchQuery(query="оператор"))
    webhooks = avito.job_webhook().list()
```

### CPA и CallTracking

```python
from avito import AvitoClient

with AvitoClient() as avito:
    calls = avito.cpa_call().list()
    records = avito.call_tracking_call(call_id=10).download()
```

## Пагинация

Публичные list-операции, которые поддерживают lazy pagination, возвращают обычные SDK-результаты, а поле `items` в них ведет себя как list-like коллекция `PaginatedList`.

Текущий стабильный контракт:

- первая страница загружается сразу, остальные страницы подгружаются только при чтении элементов за ее пределами;
- доступ к уже загруженным элементам не делает повторных запросов;
- частичная итерация и slicing загружают только необходимые страницы;
- явная полная материализация выполняется через `items.materialize()`.

Пример:

```python
from avito import AvitoClient

with AvitoClient() as avito:
    result = avito.ad(user_id=123).list(status="active", limit=50)

    first = result.items[0]
    preview = result.items[:10]
    all_items = result.items.materialize()
```

### Автотека

```python
from avito import AvitoClient
from avito.autoteka import PreviewReportRequest, VinRequest

with AvitoClient() as avito:
    preview = avito.autoteka_vehicle().create_preview_by_vin(
        request=VinRequest(vin="XTA00000000000000")
    )
    report = avito.autoteka_report().create_report(
        request=PreviewReportRequest(preview_id=int(preview.preview_id or 0))
    )
```

### Недвижимость, отзывы и тарифы

```python
from avito import AvitoClient
from avito.realty import RealtyBookingsUpdateRequest, RealtyPricePeriod, RealtyPricesUpdateRequest

with AvitoClient() as avito:
    booking = avito.realty_booking(item_id=20, user_id=10)
    booking.update_bookings_info(
        request=RealtyBookingsUpdateRequest(blocked_dates=["2026-05-01"])
    )
    bookings = booking.list_realty_bookings(date_start="2026-05-01", date_end="2026-05-05")
    avito.realty_pricing(item_id=20, user_id=10).update_realty_prices(
        request=RealtyPricesUpdateRequest(
            periods=[RealtyPricePeriod(date_from="2026-05-01", price=5000)]
        )
    )
    reviews = avito.review().list_reviews_v1()
    tariff = avito.tariff().get_tariff_info()
```

## Отладка интеграции

SDK не раскрывает сырой transport в основном API, но даёт безопасный debug snapshot без секретов:

```python
from avito import AvitoClient

client = AvitoClient()
info = client.debug_info()

print(info.base_url)
print(info.user_id)
print(info.retry_max_attempts)
client.close()
```

`debug_info()` подходит для smoke-проверок окружения и диагностики конфигурации. Стабильный контракт включает `base_url`, `user_id`, флаг `requires_auth`, таймауты и retry-настройки. Access token, `client_secret` и `Authorization` header в этот снимок не попадают.

## Проверки качества

Минимальный релизный набор:

```bash
make check
```

Для локальной разработки команды разделены:

```bash
make fmt
make lint
make typecheck
make test
make build
```

## GitHub Actions

Для репозитория настроены два workflow:

- `CI` запускается на каждый `push` в `main`/`master` и на каждый `pull_request`, выполняет `make check`.
- `Release` запускается при пуше тега вида `v*`, выставляет версию пакета из тега, повторно выполняет `make check`, публикует пакет на PyPI и создаёт GitHub Release.

Для публикации релиза нужно добавить secret:

- `PYPI_API_TOKEN` — токен публикации в PyPI для `poetry publish`.

Порядок релиза:

```bash
git tag v1.0.2
git push origin v1.0.2
```

## Документация репозитория

- [STYLEGUIDE.md](STYLEGUIDE.md) — нормативные архитектурные правила
- [docs/inventory.md](docs/inventory.md) — матрица соответствия swagger-операций и публичного API SDK
