# TODO: Исправления STYLEGUIDE и API-контракт

## Context

Полный анализ проекта выявил 7 категорий несоответствий между кодом, STYLEGUIDE.md и README.md.
Все изменения направлены на устранение конкретных нарушений; backward-compatibility не соблюдается.
Порядок шагов: сначала код, затем тесты, в конце документация.

---

## Шаг 1 — Исправить `Any` в domain-файлах

**Нарушение:** STYLEGUIDE §Типизация: "`Any` запрещен, кроме узких boundary-layer мест с локальным объяснением".

### 1.1 `avito/promotion/domain.py`

| Строка | Было | Станет |
|--------|------|--------|
| 5 | `from typing import Any` | удалить |
| 62 | `items: Sequence[Any]` | `items: Sequence[object]` |
| 83 | `target: dict[str, Any]` | `target: dict[str, object]` |
| 84 | `request_payload: dict[str, Any]` | `request_payload: dict[str, object]` |

### 1.2 `avito/ads/domain.py`

| Строка | Было | Станет |
|--------|------|--------|
| 6 | `from typing import Any` | удалить |
| 49 | `items: Sequence[Any]` | `items: Sequence[object]` |
| 65 | `target: dict[str, Any]` | `target: dict[str, object]` |
| 66 | `request_payload: dict[str, Any]` | `request_payload: dict[str, object]` |

**Тест:** `make typecheck` не должен выдавать `[assignment]` / `[arg-type]` по этим файлам.

---

## Шаг 2 — Добавить `SerializableModel` публичным моделям в `avito/ads/models.py`

**Нарушение:** STYLEGUIDE §Dataclass: "Каждая публичная модель должна предоставлять единообразную сериализацию через `to_dict()` и `model_dump()`." Классы ниже не наследуют `SerializableModel` — получают методы только через runtime-патч `enable_module_serialization`. При strict mypy вызов `.to_dict()` на них даст `[attr-defined]`.

Добавить `(SerializableModel)` как базовый класс (без изменения полей):

- `UpdatePriceResult` (строка 44)
- `ItemAnalyticsResult` (строка 133)
- `VasPricesResult` (строка 188)
- `VasApplyResult` (строка 195)
- `UploadResult` (строка 270)
- `AutoloadFieldsResult` (строка 288)
- `AutoloadTreeResult` (строка 304)
- `IdMappingResult` (строка 311)
- `AutoloadReportsResult` (строка 329)
- `AutoloadReportItemsResult` (строка 347)
- `AutoloadFeesResult` (строка 364)
- `ActionResult` (строка 392)

**Тест:** добавить в `tests/test_stage8_serialization_contract.py`:

```python
def test_ads_result_models_serialize_correctly() -> None:
    from avito.ads.models import UpdatePriceResult, IdMappingResult

    r = UpdatePriceResult(item_id=42, price=999.0, status="active")
    assert r.to_dict() == {"item_id": 42, "price": 999.0, "status": "active"}
    json.dumps(r.to_dict())

    m = IdMappingResult(items=[])
    assert m.to_dict() == {"items": []}
```

---

## Шаг 3 — Добавить `SerializableModel` публичным моделям в `avito/promotion/models.py`

**Нарушение:** то же, что в шаге 2.

Следующие классы возвращаются публичными методами `AutostrategyCampaign`, но не наследуют `SerializableModel`:

- `AutostrategyBudgetPoint` (строка 566)
- `AutostrategyPriceRange` (строка 579)
- `AutostrategyBudget` (строка 592) — возвращается `autostrategy_campaign().create_budget()`
- `CampaignActionResult` (строка 625) — возвращается `create()`, `update()`, `delete()`
- `CampaignInfo` (строка 632) — вложена в `CampaignActionResult` и `CampaignsResult`
- `CampaignsResult` (строка 685) — возвращается `list()`
- `AutostrategyStat` (строка 693) — возвращается `get_stat()`

Добавить `(SerializableModel)` как базовый класс.

**Тест:** добавить в `tests/test_stage8_serialization_contract.py`:

```python
def test_autostrategy_models_serialize_correctly() -> None:
    from avito.promotion.models import (
        AutostrategyBudget,
        CampaignActionResult,
        CampaignsResult,
        AutostrategyStat,
        AutostrategyStatItem,
        AutostrategyStatTotals,
    )

    budget = AutostrategyBudget(
        calc_id=1, recommended=None, minimal=None, maximal=None, price_ranges=[]
    )
    assert budget.to_dict() == {
        "calc_id": 1,
        "recommended": None,
        "minimal": None,
        "maximal": None,
        "price_ranges": [],
    }
    json.dumps(budget.to_dict())

    result = CampaignActionResult(campaign=None)
    assert result.to_dict() == {"campaign": None}

    campaigns = CampaignsResult(items=[], total_count=0)
    assert campaigns.to_dict() == {"items": [], "total_count": 0}

    stat = AutostrategyStat(
        items=[AutostrategyStatItem(date="2026-01-01", calls=5, views=10)],
        totals=AutostrategyStatTotals(calls=5, views=10),
    )
    dumped = stat.to_dict()
    assert dumped["totals"] == {"calls": 5, "views": 10}
    json.dumps(dumped)
```

---

## Шаг 4 — Удалить пустые `enums.py` файлы

**Нарушение:** STYLEGUIDE §Чего в проекте быть не должно: "устаревший код". Все перечисленные файлы содержат только docstring, не импортируются ни в одном модуле — мёртвый код. (`auth/enums.py` содержит константы и импортируется — его не трогать.)

Удалить:
```
avito/accounts/enums.py
avito/ads/enums.py
avito/autoteka/enums.py
avito/cpa/enums.py
avito/jobs/enums.py
avito/messenger/enums.py
avito/orders/enums.py
avito/promotion/enums.py
avito/ratings/enums.py
avito/realty/enums.py
avito/tariffs/enums.py
```

**Тест:** `make check` проходит без ошибок (lint, typecheck, test).

---

## Шаг 5 — Исправить имя env-переменной в `README.md`

**Нарушение:** README.md строка 81 документирует несуществующую переменную.

```
# Было:
- `AVITO_AUTH__LEGACY_TOKEN_URL`, alias: `AVITO_LEGACY_TOKEN_URL`, `LEGACY_TOKEN_URL`

# Станет:
- `AVITO_AUTH__ALTERNATE_TOKEN_URL`, alias: `AVITO_ALTERNATE_TOKEN_URL`, `ALTERNATE_TOKEN_URL`
```

**Тест:** добавить в `tests/test_readme_examples.py`:

```python
def test_auth_settings_env_var_names_match_readme() -> None:
    from avito.auth.settings import AuthSettings

    supported = AuthSettings.supported_env_vars()
    alternate_aliases = supported.get("alternate_token_url", ())

    assert "AVITO_AUTH__ALTERNATE_TOKEN_URL" in alternate_aliases
    assert "AVITO_ALTERNATE_TOKEN_URL" in alternate_aliases
    assert "ALTERNATE_TOKEN_URL" in alternate_aliases

    all_aliases = {alias for aliases in supported.values() for alias in aliases}
    assert not any("LEGACY" in a for a in all_aliases)
```

---

## Шаг 6 — Исправить STYLEGUIDE.md: `apply_vas_v2` → `apply_vas_direct`

**Нарушение:** STYLEGUIDE.md строка 378 называет метод `apply_vas_v2()`, которого нет в коде. Метод переименован в `apply_vas_direct()`, но STYLEGUIDE не обновлён.

```
# STYLEGUIDE.md строка 378
# Было:
- `ad_promotion().apply_vas_v2(...)`

# Станет:
- `ad_promotion().apply_vas_direct(...)`
```

**Тест:** расширить `test_readme_references_current_public_method_names` в `tests/test_readme_examples.py`:

```python
    from avito.ads.domain import AdPromotion

    assert hasattr(AdPromotion, "apply_vas_direct")
    assert not hasattr(AdPromotion, "apply_vas_v2")
```

---

## Шаг 7 — Обновить CHANGELOG.md

Добавить в раздел `Unreleased`:

```markdown
- Документация: исправлено имя env-переменной в README (`LEGACY_TOKEN_URL` → `ALTERNATE_TOKEN_URL`)
- Документация: исправлено имя метода в STYLEGUIDE (`apply_vas_v2` → `apply_vas_direct`)
- Типизация: `Sequence[Any]` и `dict[str, Any]` заменены на `Sequence[object]`
  и `dict[str, object]` в `ads/domain.py` и `promotion/domain.py`
- Типизация: публичные result-модели autostrategy и ads теперь явно наследуют
  `SerializableModel` вместо runtime-патча
- Удалены 11 пустых `enums.py` файлов (accounts, ads, autoteka, cpa, jobs, messenger,
  orders, promotion, ratings, realty, tariffs)
```

---

## Шаг 8 — Финальная проверка

```bash
make check   # fmt + lint + typecheck + test + build
```

---

## Сводная таблица файлов

| Файл | Изменение |
|------|-----------|
| `avito/promotion/domain.py` | Шаг 1: убрать `Any` |
| `avito/ads/domain.py` | Шаг 1: убрать `Any` |
| `avito/ads/models.py` | Шаг 2: добавить `SerializableModel` 12 классам |
| `avito/promotion/models.py` | Шаг 3: добавить `SerializableModel` 7 классам |
| `avito/*/enums.py` (11 файлов) | Шаг 4: удалить |
| `README.md` | Шаг 5: исправить env var |
| `STYLEGUIDE.md` | Шаг 6: исправить метод |
| `CHANGELOG.md` | Шаг 7: добавить запись |
| `tests/test_stage8_serialization_contract.py` | Шаги 2, 3: snapshot-тесты |
| `tests/test_readme_examples.py` | Шаги 5, 6: env var + метод тесты |
