# Первое продвижение

Этот tutorial показывает безопасный порядок запуска write-сценария: сначала собрать и проверить параметры, затем выполнить реальный запрос. Для продвижения это особенно важно, потому что ошибка в датах, бюджете или списке объявлений может затронуть деньги.

## Подготовка

Проверьте, что клиент создаётся из окружения и аккаунт доступен:

```python
from avito import AvitoClient

with AvitoClient.from_env() as avito:
    profile = avito.account().get_self()

print(profile.user_id)
```

## Сухой прогон

Write-операции, которые принимают `dry_run`, строят тот же payload, что и обычный вызов, но не отправляют запрос в transport. Это позволяет проверить consumer-код, сериализацию параметров и обработку результата до реального запуска.

```text
with AvitoClient.from_env() as avito:
    preview = avito.autostrategy_campaign().create_budget(
        campaign_type="AS",
        start_time="2026-05-01T00:00:00Z",
        finish_time="2026-05-07T00:00:00Z",
        items=[1001, 1002],
        dry_run=True,
    )
```

После проверки замените `dry_run=True` на `dry_run=False` или опустите параметр. Для повторяемых write-вызовов используйте `idempotency_key`, если метод его поддерживает.

## Следующий шаг

Полный список методов продвижения смотрите в [карте операций](../reference/operations.md) и reference-странице домена `promotion`.
