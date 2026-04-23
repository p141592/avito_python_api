# Конфигурация

SDK поддерживает три уровня инициализации: переменные окружения, короткие
OAuth-credentials и полный объект настроек. Приоритет при загрузке из окружения:
значения процесса, затем `.env`, затем значения по умолчанию.

## AvitoSettings

::: avito.AvitoSettings

## AuthSettings

::: avito.AuthSettings

## Env-переменные

| Поле | Переменные |
|---|---|
| `base_url` | `AVITO_BASE_URL` |
| `user_id` | `AVITO_USER_ID` |
| `user_agent_suffix` | `AVITO_USER_AGENT_SUFFIX` |
| `auth.client_id` | `AVITO_AUTH__CLIENT_ID`, `AVITO_CLIENT_ID` |
| `auth.client_secret` | `AVITO_AUTH__CLIENT_SECRET`, `AVITO_CLIENT_SECRET` |
| `auth.scope` | `AVITO_AUTH__SCOPE`, `AVITO_SCOPE` |
| `auth.refresh_token` | `AVITO_AUTH__REFRESH_TOKEN`, `AVITO_REFRESH_TOKEN` |
| `auth.token_url` | `AVITO_AUTH__TOKEN_URL`, `AVITO_TOKEN_URL` |
| `auth.alternate_token_url` | `AVITO_AUTH__ALTERNATE_TOKEN_URL`, `AVITO_ALTERNATE_TOKEN_URL` |
| `auth.autoteka_token_url` | `AVITO_AUTH__AUTOTEKA_TOKEN_URL`, `AVITO_AUTOTEKA_TOKEN_URL` |
| `auth.autoteka_client_id` | `AVITO_AUTH__AUTOTEKA_CLIENT_ID`, `AVITO_AUTOTEKA_CLIENT_ID` |
| `auth.autoteka_client_secret` | `AVITO_AUTH__AUTOTEKA_CLIENT_SECRET`, `AVITO_AUTOTEKA_CLIENT_SECRET` |
| `auth.autoteka_scope` | `AVITO_AUTH__AUTOTEKA_SCOPE`, `AVITO_AUTOTEKA_SCOPE` |

## Per-operation overrides

| Тип операции | Разрешённые overrides |
|---|---|
| read / list / probe | `timeout`, `retries` |
| write при `dry_run=False` | `timeout`, `retries`, `idempotency_key` |
| write при `dry_run=True` | `timeout` |
| pagination-чтение | `timeout`, `retries`, `page_size` |

`dry_run=True` обязан строить тот же payload, что и реальный write-вызов, но не
должен выполнять transport-вызов.
