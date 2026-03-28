# MARGIN_TREND_POLICY

**Дата:** 2026-03-28  
**Назначение:** политика интерпретации trend-отчётов economics для operator governance.  
**Scope:** internal monitoring/reporting only (не customer UI, не retail repricing).

---

## 1) Неподвижные boundary-правила

1. `billing.public_model_tariff` — единственный источник retail pricing.
2. Provider/upstream costs используются только в internal economics слое.
3. Trend monitoring не имеет права автоматически менять retail pricing.
4. Любые runtime/config/API изменения требуют отдельного smoke-check.

---

## 2) Источник данных и окно наблюдения

- Базовый источник: `billing-portal-src/app/api/billing.py`.
- Snapshot извлекается из:
  - `OPERATOR_ECONOMICS_SNAPSHOT_DATE`
  - `OPERATOR_ECONOMICS_MODEL_MATRIX_TSV`
- Окно сравнения: `current` и `previous` валидные snapshot из git history файла `billing.py`.

---

## 3) Model trend policy

### 3.1 Margin band

- `negative` : lowest margin < 0
- `critical` : 0 <= lowest margin < 30
- `warning`  : 30 <= lowest margin < 50
- `ok`       : lowest margin >= 50
- `unknown`  : margin не вычисляется

### 3.2 Классификация тренда

Приоритет классификации:

1. `unknown -> known` => `improving` (улучшение покрытости).
2. `known -> unknown` => `worsening` (деградация покрытости).
3. Ухудшение/улучшение margin band => `worsening/improving`.
4. Деградация/улучшение confidence (`Exact/Estimated/Incomplete`) => `worsening/improving`.
5. Delta lowest margin:
   - `<= -0.5` => `worsening`
   - `>= +0.5` => `improving`
6. Иначе => `stable`.

---

## 4) Category trend policy

1. Primary signal: изменение `warning_or_worse` count.
2. Secondary signal: изменение `avg_lowest_margin`.
   - `<= -0.5` => `worsening`
   - `>= +0.5` => `improving`
3. Если warning-count не растёт, а ухудшение только по среднему margin — трактовать как monitor-signal, не как trigger для pricing change.

---

## 5) Decision matrix

| Условие | Решение | Приоритет |
|---|---|---|
| worsening + Exact + low band (`warning/critical/negative`) | provider_path_review (cost/routing only) | P1 |
| stable + repeated low-margin model | monitor_only | P2 |
| improving за счёт unknown->known или confidence upgrade | monitor_only + data-quality note | P2 |
| category worsening без роста warning-count | monitor_only + ручной review | P2 |
| confidence = Estimated/Incomplete | осторожная интерпретация, no auto action | P2 |

---

## 6) Артефакты и периодичность

Обязательные артефакты latest-run:

- `docs/current/MARGIN_TREND_REPORT_LATEST.json`
- `docs/current/MARGIN_TREND_REPORT_LATEST.md`

Рекомендуемая периодичность:
- при каждом обновлении economics snapshot,
- либо по операторскому регламенту (ежедневно/еженедельно).

---

## 7) Non-goals

- Не менять retail pricing автоматически.
- Не изменять customer-facing API/UI в рамках этой политики.
- Не использовать trend-слой как замену ручного operator decision для high-impact действий.

