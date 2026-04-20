# TODO: Устранение несоответствий STYLEGUIDE

Анализ всех Python-файлов проекта против STYLEGUIDE.md. 12 несоответствий, упорядочены по приоритету.

---

## Найденные несоответствия

### 1. `PromotionForecast: TypeAlias = BbipForecast` без deprecation-метки
**Файл**: `avito/promotion/models.py:211`
**Правило**: «Псевдонимы типов без явной deprecation-метки запрещены».
**Действие**: Добавить `warnings.warn(DeprecationWarning)` при определении алиаса.

---

### 2. Конфигурационные классы на `pydantic.BaseModel` / `BaseSettings`
**Файлы**: `avito/config.py`, `avito/auth/settings.py`, `avito/core/types.py`, `avito/core/retries.py`
**Правило**: STYLEGUIDE показывает `AvitoSettings`, `AuthSettings` как `@dataclass(slots=True, frozen=True)`. Pydantic допустим только для чтения env на границе системы — не как основа публичного SDK-объекта.
**Действие**: Переписать все четыре класса как `@dataclass(slots=True, frozen=True)` с ручным `from_env()` через уже существующий `_env.py`.

---

### 3. `avito/client/` — пакет вместо файла `avito/client.py`
**Файлы**: `avito/client/__init__.py`, `avito/client/client.py`
**Правило**: Целевая архитектура STYLEGUIDE прямо указывает `avito/client.py` (файл, не пакет).
**Действие**: Перенести `avito/client/client.py` → `avito/client.py`, обновить все импорты, удалить папку.

---

### 4. Даты как голый `str` без валидации формата
**Файлы**: `avito/ads/domain.py`, `avito/accounts/domain.py`
**Правило**: «Даты должны принимать `datetime` — голый `str` без проверки не допускается».
**Нарушение**: Параметры `date_from: str | None`, `date_to: str | None` в публичных методах `AdStats.*`, `Account.get_operations_history()`.
**Действие**: Изменить на `date_from: datetime | None`, преобразовывать в ISO 8601 перед передачей в transport.

---

### 5. Date-поля в моделях как `str | None` вместо `datetime | None`
**Файлы**:
- `avito/accounts/models.py`: `OperationRecord.created_at`
- `avito/messenger/models.py`: `MessageInfo.created_at`
- `avito/ads/models.py`: `AutoloadReportSummary.created_at/finished_at`, `AutoloadReportDetails.created_at/finished_at`
- `avito/promotion/models.py`: `CpaAuctionItemBid.expiration_time`
**Действие**: Изменить поля на `datetime | None`, парсить в mapper-ах.

---

### 6. Request-DTO в публичных сигнатурах domain-методов
**Файл**: `avito/promotion/domain.py:514-530` — `AutostrategyCampaign.list()`
**Правило**: «Request-DTO не должны появляться в публичных сигнатурах».
**Нарушение**: `filter: CampaignListFilter | None`, `order_by: list[CampaignOrderBy] | None`.
**Действие**: Раскрыть поля как keyword-only аргументы напрямую в `list()`.

---

### 7. Неиспользуемые поля `user_id` (мёртвый код)
**Файлы**:
- `avito/ads/domain.py`: `AutoloadReport.user_id`, `AutoloadArchive.user_id`
- `avito/tariffs/domain.py`: `Tariff.user_id`
- `avito/promotion/domain.py`: `CpaAuction.user_id`, `PromotionOrder.user_id`
**Правило**: «Мёртвый код не допускается».
**Действие**: Удалить поля там, где они нигде не читаются.

---

### 8. `TrxItemInput(TypedDict, total=False)` — неточная типизация
**Файл**: `avito/promotion/models.py:145`
**Нарушение**: `total=False` делает `item_id`, `commission`, `date_from` опциональными, хотя они обязательны.
**Действие**: Разделить на обязательную часть и `total=False`-блок только для `date_to`:
```python
class _TrxItemInputRequired(TypedDict):
    item_id: int
    commission: int
    date_from: datetime

class TrxItemInput(_TrxItemInputRequired, total=False):
    date_to: datetime | None
```

---

### 9. `AvitoError` без `frozen=True`
**Файл**: `avito/core/exceptions.py:43`
**Нарушение**: `@dataclass(slots=True)` — несогласованно с остальными моделями SDK.
**Действие**: Добавить `frozen=True`. `__post_init__` уже использует `object.__setattr__` — совместимо.

---

### 10. Тесты используют обобщённые env-алиасы `SECRET`, `BASE_URL`, `CLIENT_ID`
**Файл**: `tests/test_config.py:12-26`, `test_avito_settings_from_env_supports_alias_variables`
**Правило**: «Обобщённые имена вроде `SECRET` или `TOKEN` не должны быть официальными алиасами».
**Нарушение**: Тесты очищают `SECRET`, `CLIENT_ID`, `BASE_URL` и тестируют поведение, которого нет в `ENV_ALIASES`.
**Действие**: Удалить `BASE_URL`, `USER_ID`, `CLIENT_ID`, `SECRET`, `AVITO_SECRET` из `ENV_KEYS` и из тестовых `.env`-файлов.

---

### 11. Пропущена пустая строка в `avito/core/serialization.py`
**Файл**: `avito/core/serialization.py:7-8`
**Действие**: Добавить пустую строку между `from dataclasses import fields, is_dataclass` и `def _is_public_field`.

---

### 12. Отсутствуют docstring у публичных методов
**Файлы**:
- `avito/tariffs/domain.py:19` — `Tariff.get_tariff_info()` без docstring
- `avito/promotion/models.py` — `CampaignUpdateTimeFilter.to_payload()`, `CampaignListFilter.to_payload()`, `CampaignOrderBy.to_payload()` без docstring
**Действие**: Добавить однострочные docstring.

---

## Порядок выполнения (по возрастанию сложности)

| # | Файл(ы) | Сложность |
|---|---------|-----------|
| 11 | `avito/core/serialization.py` | Минимальная |
| 12 | `avito/tariffs/domain.py`, `avito/promotion/models.py` | Минимальная |
| 1 | `avito/promotion/models.py` — alias deprecation | Низкая |
| 9 | `avito/core/exceptions.py` — frozen | Низкая |
| 7 | Мёртвые `user_id` (5 файлов) | Низкая |
| 10 | `tests/test_config.py` — env aliases | Низкая |
| 8 | `avito/promotion/models.py` — TrxItemInput | Низкая |
| 6 | `avito/promotion/domain.py` — list() params | Средняя |
| 5 | Date-поля в 5 моделях | Средняя |
| 4 | Date-параметры в domain-методах | Средняя |
| 3 | `avito/client/` → `avito/client.py` | Средняя |
| 2 | Config: pydantic → dataclass (4 файла) | Высокая |
