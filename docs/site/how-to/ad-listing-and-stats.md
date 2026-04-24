# Объявления, статистика и продвижение

Этот рецепт покрывает повседневный сценарий домена `ads`: найти объявления, открыть карточку, посмотреть статистику и подготовить безопасное действие продвижения.

## Список объявлений

`ad().list()` возвращает `PaginatedList[Listing]`. Первую страницу SDK загружает сразу, остальные страницы дочитываются при обращении по индексу, итерации или `materialize()`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(status="active", limit=2)
    items = listings.materialize()

print(items[0].item_id)
print(items[0].title)
```

## Карточка объявления

Для чтения одного объявления нужны оба идентификатора: `user_id` и `item_id`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    item = avito.ad(item_id=101, user_id=7).get()

print(item.status)
print(item.price)
```

## Статистика объявлений

`ad_stats()` группирует статистику, аналитику, звонки и расходы. Если `item_id` передан в фабрику, методы используют его по умолчанию.

```python
from datetime import datetime, timezone

from avito import AvitoClient

with AvitoClient.from_env() as avito:
    stats = avito.ad_stats(item_id=101, user_id=7)
    item_stats = stats.get_item_stats(
        date_from=datetime(2026, 4, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 4, 23, tzinfo=timezone.utc),
    )
    calls = stats.get_calls_stats()
    spendings = stats.get_account_spendings()

print(item_stats.items[0].views)
print(calls.items[0].answered_calls)
print(spendings.total)
```

## Аналитика по списку объявлений

Когда нужно сравнить несколько объявлений, передайте `item_ids` явно.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    analytics = avito.ad_stats(user_id=7).get_item_analytics(
        item_ids=[101],
        fields=["views", "contacts", "favorites"],
    )

print(analytics.items[0].contacts)
```

## Цены продвижения и dry-run

Перед включением услуг продвижения проверьте доступные цены. Для write-операций используйте `dry_run=True`, чтобы получить preview результата без вызова transport.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    promotion = avito.ad_promotion(item_id=101, user_id=7)
    prices = promotion.get_vas_prices(item_ids=[101])
    preview = promotion.apply_vas(codes=["xl"], dry_run=True)

print(prices.items[0].price)
print(preview.applied)
print(preview.request_payload)
```

## Обновление цены

`update_price()` меняет цену конкретного объявления. Для повторяемых запусков передавайте `idempotency_key`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    result = avito.ad(item_id=101, user_id=7).update_price(
        price=10900,
        idempotency_key="ad-price-example-1",
    )

print(result.status)
print(result.price)
```

Полный список методов домена смотрите в [reference по ads](../reference/domains/ads.md), а общие правила `PaginatedList` — в [reference по пагинации](../reference/pagination.md).
