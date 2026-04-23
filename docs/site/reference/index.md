# Reference

!!! note "Раздел в разработке"
    Полный справочник будет добавлен в PR 2 с автогенерацией из docstring'ов через `mkdocstrings`.

    **Что будет здесь:**

    | Страница | Описание |
    |---|---|
    | [AvitoClient](client.md) | Фасад SDK: все фабричные методы |
    | Конфигурация | `AvitoSettings`, `AuthSettings`, таблица env-переменных |
    | Домены | По одной странице на каждый из 10 пакетов: accounts, ads, messenger, promotion, orders, jobs, cpa, autoteka, realty, ratings/tariffs |
    | Модели | Контрактные модели: `PaginatedList`, `PromotionActionResult`, `SerializableModel` |
    | Исключения | Иерархия `AvitoError`, таблица HTTP-код → тип |
    | Пагинация | `PaginatedList[T]`: контракт, ленивая загрузка, `materialize()` |
    | Тестирование | `FakeTransport`, `FakeResponse`: scripting, inspection, error injection |

    Пока используйте [README](https://github.com/p141592/avito#readme) для обзора публичного API.
