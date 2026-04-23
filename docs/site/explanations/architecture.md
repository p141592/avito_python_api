# Архитектура SDK

!!! note "Раздел в разработке"
    Полное объяснение архитектуры будет добавлено в PR 3.

    Сейчас страница содержит минимальную Mermaid-диаграмму, чтобы строгая сборка сайта проверяла поддержку диаграмм в MkDocs Material.

```mermaid
flowchart LR
    user[Пользовательский код] --> facade[AvitoClient]
    facade --> domain[Доменный объект]
    domain --> section[SectionClient]
    section --> transport[Transport]
    transport --> auth[AuthProvider]
    transport --> api[Avito API]
    section --> mapper[Mapper]
    mapper --> model[SDK model]
```
