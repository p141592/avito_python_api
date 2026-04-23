# Explanations

Explanations описывают причины архитектурных решений SDK: границы слоёв, retry-поведение, модель ошибок, безопасность диагностики и правила обратной совместимости.

| Статья | Что объясняет |
|---|---|
| [Архитектура SDK](architecture.md) | Как `AvitoClient`, домены, section clients, transport, auth и mappers разделяют ответственность |
| Transport и retry | Почему retry живёт в transport-слое и как учитываются 429/5xx |
| Модель ошибок | Как HTTP-коды превращаются в typed exceptions |
| Семантика пагинации | Почему `PaginatedList` ленивый и когда загружаются страницы |
| Dry-run и идемпотентность | Как write-операции проверяются без сетевого вызова |
| Security и redaction | Какие секреты SDK не раскрывает в диагностике и ошибках |
| Совместимость | Как deprecation отражается в runtime, reference и changelog |

Для практических сценариев используйте [how-to рецепты](../how-to/index.md), а для полного API-контракта — [reference](../reference/index.md).
