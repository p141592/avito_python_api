# Модели

Публичные модели SDK — frozen dataclass-объекты с `slots=True`. Они не раскрывают
transport DTO и возвращают JSON-совместимое представление через
`to_dict()` / `model_dump()`.

## Сериализация

::: avito.core.serialization.SerializableModel

## Доменные модели

Модели экспортируются из публичных доменных пакетов и также раскрываются на
страницах доменов:

- `accounts`
- `ads`
- `autoteka`
- `cpa`
- `jobs`
- `messenger`
- `orders`
- `promotion`
- `ratings`
- `realty`
- `tariffs`
