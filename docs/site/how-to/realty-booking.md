# Бронирование недвижимости

Этот рецепт показывает основной цикл домена `realty`: заблокировать даты, прочитать бронирования и обновить цены краткосрочной аренды.

## Блокировка дат

`realty_booking()` требует `item_id` и `user_id`. Даты передаются списком строк в формате upstream API.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    result = avito.realty_booking(20, user_id=10).update_bookings_info(
        blocked_dates=["2026-05-01"],
    )

print(result.success)
print(result.status)
```

## Список бронирований

Для чтения бронирований задайте границы периода. Если нужны неоплаченные бронирования, передайте `with_unpaid=True`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    bookings = avito.realty_booking(20, user_id=10).list_realty_bookings(
        date_start="2026-05-01",
        date_end="2026-05-05",
        with_unpaid=True,
    )

print(bookings.items[0].booking_id)
print(bookings.items[0].check_in)
```

## Обновление цен

Для цен используйте публичную модель `RealtyPricePeriod`.

```python
from avito import AvitoClient
from avito.realty import RealtyPricePeriod

with AvitoClient.from_env() as avito:
    updated = avito.realty_pricing(20, user_id=10).update_realty_prices(
        periods=[RealtyPricePeriod(date_from="2026-05-01", price=5000)],
    )

print(updated.success)
```

Полный контракт смотрите в [reference по realty](../reference/domains/realty.md). Ошибки валидации входных параметров описаны в [reference по исключениям](../reference/exceptions.md).
