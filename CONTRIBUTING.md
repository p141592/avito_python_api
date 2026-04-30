# Contributing

## Проверки документации

Перед PR, который меняет публичный API, README или `docs/site/`, выполните:

```bash
make docs-strict
make docs-report
```

Для полной локальной проверки ссылок установите `lychee`:

```bash
brew install lychee
```

или на Linux:

```bash
cargo binstall lychee
```

После установки доступна проверка:

```bash
make docs-check
```

## TTFC measurement

TTFC показывает, за сколько минут новый пользователь проходит путь от чистого
окружения до первого реального `get_self()` из `docs/site/tutorials/getting-started.md`.
Цель документации: не больше 15 минут.

Процедура перед релизом:

1. Создайте новый временный каталог и виртуальное окружение.
2. Установите опубликованный пакет: `pip install avito-py`.
3. Установите реальные `AVITO_CLIENT_ID` и `AVITO_CLIENT_SECRET`.
4. Запустите секундомер.
5. Выполните tutorial `getting-started.md` до успешного `get_self()`.
6. Остановите секундомер и запишите результат в минутах.
7. Запишите результат в release notes или changelog релиза.

`make docs-report` генерирует machine-readable Swagger bindings report для
reference coverage; TTFC остаётся ручной release-проверкой.
