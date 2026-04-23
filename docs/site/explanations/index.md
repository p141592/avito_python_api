# Explanations

!!! note "Раздел в разработке"
    Концептуальные статьи будут добавлены в PR 3. Они объясняют архитектурные решения и инварианты SDK.

    **Запланированные статьи:**

    | Статья | Описание |
    |---|---|
    | Архитектура SDK | Слои, их границы, почему они именно такие |
    | Transport | Как устроен httpx-слой, retry, error mapping |
    | Retry и backoff | Sequence-диаграмма поведения при 5xx/429 |
    | Семантика пагинации | Flow подгрузки страниц, гарантии lazy loading |
    | Контракт dry_run | Ветвление после `build_payload()`, что не вызывается |
    | Модель ошибок | Почему 401 и 403 — siblings, не parent/child |
    | Обратная совместимость | SemVer, политика deprecation, `DeprecationWarning` |
    | Только синхронный API | Почему нет async, где будет `avito.aio` |

    Пока изучите [README](https://github.com/p141592/avito_python_api#readme) для общего обзора.
