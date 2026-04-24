# Заказы, этикетки и остатки

Этот рецепт показывает основной рабочий цикл домена `orders`: прочитать заказы, выполнить действие по заказу, создать PDF-этикетку, проверить delivery task и обновить остатки.

## Список заказов

`order().list()` возвращает типизированный результат с краткой информацией по заказам.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    orders = avito.order().list()

print(orders.items[0].order_id)
print(orders.items[0].buyer_name)
```

## Действия по заказу

Write-операции принимают конкретный `order_id`. Для повторяемых действий передавайте `idempotency_key`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    confirmed = avito.order().apply(
        order_id="ord-1",
        transition="confirm",
        idempotency_key="order-confirm-example-1",
    )
    marked = avito.order().update_markings(
        order_id="ord-1",
        codes=["marking-code-1"],
        idempotency_key="order-marking-example-1",
    )

print(confirmed.status)
print(marked.success)
```

## Генерация этикетки

Сначала создайте задачу генерации, затем скачайте PDF по `task_id`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    task = avito.order_label().create(
        order_ids=["ord-1"],
        idempotency_key="label-create-example-1",
    )
    label = avito.order_label(task.task_id).download()

print(label.filename)
print(label.binary.content_type)
```

## Доставка и delivery task

Production delivery API возвращает идентификатор задачи или сущности. Статус задачи можно прочитать через `delivery_task()`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    announcement = avito.delivery_order().create_announcement(
        order_id="ord-1",
        idempotency_key="delivery-announcement-example-1",
    )
    parcel = avito.delivery_order().create(
        order_id="ord-1",
        parcel_id="par-1",
        idempotency_key="delivery-parcel-example-1",
    )
    task = avito.delivery_task(announcement.task_id).get()

print(parcel.parcel_id)
print(task.status)
```

## Остатки

`stock()` читает и обновляет остатки по объявлениям. Для обновления используйте публичную модель `StockUpdateEntry`.

```python
from avito import AvitoClient
from avito.orders import StockUpdateEntry

with AvitoClient.from_env() as avito:
    current = avito.stock().get(item_ids=[101])
    updated = avito.stock().update(
        stocks=[StockUpdateEntry(item_id=101, quantity=7)],
        idempotency_key="stock-update-example-1",
    )

print(current.items[0].quantity)
print(updated.items[0].success)
```

Полный список методов смотрите в [reference по orders](../reference/domains/orders.md). Бинарные ответы, такие как PDF-этикетки, сериализуются через `to_dict()` с `content_base64`.
