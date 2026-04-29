## Проверки

- [ ] `make check` проходит локально или в CI.
- [ ] `make docs-strict` проходит, если изменены README, docs, публичные сигнатуры или Swagger bindings.
- [ ] README/tutorials/how-to примеры соответствуют актуальным публичным сигнатурам SDK.
- [ ] Новая публичная операция связана со Swagger operation binding и покрыта reference.
- [ ] Публичное переименование: alias сохранён, `DeprecationWarning` добавлен, `CHANGELOG.md` обновлён в секции `Deprecated`.
