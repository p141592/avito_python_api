# Отчёт Автотеки

Этот рецепт показывает базовую цепочку домена `autoteka`: уточнить параметры каталога, создать preview по VIN, выпустить отчёт и прочитать список готовых отчётов.

## Каталог

`resolve_catalog()` помогает получить доступные поля автокаталога для выбранной марки. Метод принимает конкретный `brand_id` и возвращает типизированные поля.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    catalog = avito.autoteka_vehicle().resolve_catalog(brand_id=1)

print(catalog.items[0].field_id)
print(catalog.items[0].label)
```

## Preview по VIN

Перед выпуском отчёта создайте preview. Для повторяемых запусков передавайте `idempotency_key`.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    preview = avito.autoteka_vehicle().create_preview_by_vin(
        vin="XTA00000000000000",
        idempotency_key="autoteka-preview-example-1",
    )

print(preview.preview_id)
print(preview.vehicle_id)
```

## Выпуск отчёта

Отчёт создаётся по `preview_id`. Если `preview_id` пришёл строкой, приведите его к `int` перед вызовом.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    preview = avito.autoteka_vehicle().create_preview_by_vin(
        vin="XTA00000000000000",
        idempotency_key="autoteka-preview-example-2",
    )
    report = avito.autoteka_report().create_report(
        preview_id=int(preview.preview_id or 0),
        idempotency_key="autoteka-report-example-1",
    )

print(report.report_id)
print(report.status)
```

## Список отчётов

`list_reports()` возвращает готовые отчёты аккаунта Автотеки.

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    reports = avito.autoteka_report().list_reports()

print(reports.items[0].report_id)
print(reports.items[0].vehicle_id)
```

Полный контракт смотрите в [reference по autoteka](../reference/domains/autoteka.md). Для подробной карты HTTP-операций используйте [reference операций](../reference/operations.md).
