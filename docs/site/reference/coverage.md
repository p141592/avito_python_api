# Покрытие API

SDK покрывает 204 операции Avito API. Swagger/OpenAPI-спецификации в `docs/avito/api/` остаются источником истины, а inventory фиксирует соответствие операций публичным методам SDK.

!!! info "Источник данных"
    Эта страница не ссылается на файлы вне `docs_dir` относительными путями, чтобы `mkdocs build --strict` оставался зелёным. Ссылки ниже ведут на файлы спецификаций в GitHub.

| Документ API | Swagger/OpenAPI |
|---|---|
| CPA-аукцион | [CPA-аукцион.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/CPA-аукцион.json) |
| CPA Авито | [CPAАвито.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/CPAАвито.json) |
| Call Tracking | [CallTracking[КТ].json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/CallTracking%5BКТ%5D.json) |
| TrxPromo | [TrxPromo.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/TrxPromo.json) |
| Авито Работа | [АвитоРабота.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/АвитоРабота.json) |
| Автозагрузка | [Автозагрузка.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Автозагрузка.json) |
| Автостратегия | [Автостратегия.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Автостратегия.json) |
| Автотека | [Автотека.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Автотека.json) |
| Авторизация | [Авторизация.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Авторизация.json) |
| Аналитика по недвижимости | [Аналитикапонедвижимости.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Аналитикапонедвижимости.json) |
| Доставка | [Доставка.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Доставка.json) |
| Иерархия аккаунтов | [ИерархияАккаунтов.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/ИерархияАккаунтов.json) |
| Информация о пользователе | [Информацияопользователе.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Информацияопользователе.json) |
| Краткосрочная аренда | [Краткосрочнаяаренда.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Краткосрочнаяаренда.json) |
| Мессенджер | [Мессенджер.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Мессенджер.json) |
| Настройка цены целевого действия | [Настройкаценыцелевогодействия.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Настройкаценыцелевогодействия.json) |
| Объявления | [Объявления.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Объявления.json) |
| Продвижение | [Продвижение.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Продвижение.json) |
| Рассылка скидок и спецпредложений в мессенджере | [Рассылкаскидокиспецпредложенийвмессенджере.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Рассылкаскидокиспецпредложенийвмессенджере.json) |
| Рейтинги и отзывы | [Рейтингииотзывы.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Рейтингииотзывы.json) |
| Тарифы | [Тарифы.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Тарифы.json) |
| Управление заказами | [Управлениезаказами.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Управлениезаказами.json) |
| Управление остатками | [Управлениеостатками.json](https://github.com/p141592/avito_python_api/blob/main/docs/avito/api/Управлениеостатками.json) |

Полная карта «операция API → публичный метод SDK» хранится в [inventory.md](https://github.com/p141592/avito_python_api/blob/main/docs/avito/inventory.md).
