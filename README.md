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

```python
from avito import AvitoClient

with AvitoClient() as avito:
    profile = avito.account().get_self()
    ad = avito.ad(42).get()

print(profile.name)
print(ad.title)
```

По умолчанию настройки читаются из переменных окружения с префиксом `AVITO_`.

Базовые переменные:

- `AVITO_AUTH__CLIENT_ID`
- `AVITO_AUTH__CLIENT_SECRET`
- `AVITO_AUTH__REFRESH_TOKEN`
- `AVITO_BASE_URL`

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

with AvitoClient() as avito:
    chats = avito.chat(user_id=123).list()
    message = avito.chat(chat_id="chat-1", user_id=123).send_message(message="Здравствуйте")
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

with AvitoClient() as avito:
    vacancies = avito.vacancy().list()
    applications = avito.application().list()
    webhooks = avito.job_webhook().list()
```

### CPA и CallTracking

```python
from avito import AvitoClient

with AvitoClient() as avito:
    calls = avito.cpa_call().list()
    records = avito.call_tracking_call(call_id=10).download()
```

### Автотека

```python
from avito import AvitoClient

with AvitoClient() as avito:
    preview = avito.autoteka_vehicle().create_preview_by_vin(payload={"vin": "XTA00000000000000"})
    report = avito.autoteka_report(report_id=preview.preview_id).get_report()
```

### Недвижимость, отзывы и тарифы

```python
from avito import AvitoClient

with AvitoClient() as avito:
    bookings = avito.realty_booking().list()
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
print(info.retry_max_attempts)
client.close()
```

`debug_info()` подходит для smoke-проверок окружения и диагностики конфигурации. Access token, `client_secret` и `Authorization` header в этот снимок не попадают.

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

- [STYLEGUIDE.md](STYLEGUIDE.md) — нормативные архитектурные правила.
- [TODO.md](TODO.md) — этапы реализации и релизный gate.
- [docs/inventory.md](docs/inventory.md) — матрица соответствия swagger-операций и публичного API SDK.
- [docs/release.md](docs/release.md) — политика changelog и checklist релиза.
