# Пагинация

`PaginatedList[T]` — ленивый контейнер: первая страница загружается при создании, остальные подгружаются только при обращении к данным за их пределами. Это позволяет работать с большими списками без полной загрузки всех страниц сразу.

## Ленивая итерация

`for`-цикл читает страницы по одной. Если вам нужны только первые несколько элементов, обход прекращается без лишних HTTP-запросов.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(status="active", limit=2)
    for item in listings:
        print(item.item_id, item.title)
```

## Полная загрузка

`materialize()` загружает все оставшиеся страницы и возвращает обычный `list[T]`. Используйте этот метод, когда нужны все элементы сразу.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(status="active", limit=2)
    items = listings.materialize()

print(len(items))
print(items[0].title)
```

## Доступ по индексу

Обращение по индексу подгружает только нужные страницы. Отрицательный индекс вызывает полную загрузку.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(status="active", limit=2)
    first = listings[0]

print(first.item_id)
```

## Контроль размера страницы

Параметр `limit` управляет количеством элементов на странице. Меньший `limit` снижает объём первого ответа, больший — уменьшает число запросов при полной загрузке.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    compact = avito.ad(user_id=7).list(limit=1)
    large = avito.ad(user_id=7).list(limit=10)

print(compact[0].title)
print(large[0].title)
```

## Проверка общего числа элементов

`len()` возвращает известный total из ответа API, если он был передан. Если total неизвестен, `len()` дозагружает все страницы.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    listings = avito.ad(user_id=7).list(status="active", limit=2)
    total = len(listings)

print(total)
```

## Пагинация со смещением

Параметр `offset` позволяет начать чтение не с первого элемента. Используйте его для постраничного перехода с фиксированными позициями.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    page2 = avito.ad(user_id=7).list(limit=2, offset=0)
    items = page2.materialize()

print(items[0].item_id)
```

Полный контракт `PaginatedList` описан в [reference по пагинации](../reference/pagination.md). Семантика ленивой загрузки подробно разобрана в [explanations](../explanations/pagination-semantics.md).
