# Reference

Справочник фиксирует публичный контракт SDK: фасад `AvitoClient`, настройки,
доменные объекты, модели, исключения, пагинацию и тестовые утилиты.

| Страница | Что искать |
|---|---|
| [AvitoClient](client.md) | Инициализация, контекстный менеджер, фабричные методы, `debug_info()` |
| [Конфигурация](config.md) | `AvitoSettings`, `AuthSettings`, env-переменные, per-operation overrides |
| [Покрытие API](coverage.md) | 204/204 Swagger operations из binding report |
| [Методы API](operations.md) | Карта Swagger operation → публичный SDK-метод |
| Домены | Публичные объекты и модели каждого доменного пакета |
| [Enum](enums.md) | Все публичные перечисления доменных пакетов |
| [Модели](models.md) | Сериализация, dataclass-контракт, публичные модели |
| [Исключения](exceptions.md) | Иерархия ошибок и диагностические поля |
| [Пагинация](pagination.md) | `PaginatedList[T]` и lazy-loading контракт |
| [Тестирование](testing.md) | `avito.testing` и fake transport для consumer-side тестов |
