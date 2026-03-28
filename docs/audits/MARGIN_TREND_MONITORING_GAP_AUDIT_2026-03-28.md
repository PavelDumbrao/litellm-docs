# MARGIN_TREND_MONITORING Gap Audit

**Дата:** 2026-03-28  
**Scope:** internal operator monitoring layer для economics trend (без изменения retail pricing).  
**Boundary:** `billing.public_model_tariff` остаётся единственным retail source of truth.

---

## 1) Цель и исходный gap

До этого прохода в проекте был economics snapshot и point-in-time alerts, но не было формального trend layer:

1. Не было стандартизированного сравнения `current vs previous` snapshot.
2. Не было model-level классификации тренда (`worsening/stable/improving`).
3. Не было category-level тренда по `warning_or_worse` и средней минимальной марже.
4. Не было persistence-сигнала по повторяющимся low-margin моделям.
5. Не было отдельного machine-readable артефакта для governance/automation.

---

## 2) Входные источники

- `billing-portal-src/app/api/billing.py`
  - `OPERATOR_ECONOMICS_MODEL_MATRIX_TSV`
  - `OPERATOR_ECONOMICS_SNAPSHOT_DATE`
- Git history по `billing.py` (окно последних ревизий с валидным economics snapshot)
- `scripts/margin_trend_monitor.py` (minimal trend generator)

---

## 3) Закрытие gap (BLOCK C артефакты)

Реализован и прогнан minimal trend layer с генерацией двух итоговых артефактов:

- `docs/current/MARGIN_TREND_REPORT_LATEST.json`
- `docs/current/MARGIN_TREND_REPORT_LATEST.md`

Отчёт теперь даёт:
- observation window (commit-to-commit),
- summary и confidence caveat,
- category trend,
- model trend,
- low-margin model trend,
- repeated low-margin inventory.

---

## 4) Фактический результат последнего прогона

### Observation window

- `previous_commit`: `d71e58788c2f97b2dc60fd48ee4999330ae3f166`
- `current_commit`: `798a5e460179c5112a237aff3cefd8e9668816b2`
- `previous_snapshot_date`: `2026-03-27`
- `current_snapshot_date`: `2026-03-27`

### Summary

- `models_current`: **44**
- `models_previous`: **44**
- `low_margin_warning_current`: **18**
- `low_margin_warning_previous`: **18**
- `repeated_low_margin_models`: **18**
- `worsening_models`: **0**
- `improving_models`: **1**
- `stable_models`: **43**

### Improving models

| Model | Category | Confidence prev->curr | Lowest margin prev->curr | Причина |
|---|---|---|---|---|
| `gpt-4.1` | General Chat | Incomplete -> Estimated | None -> 50.0 | margin_band:unknown->ok |

### Non-stable categories

| Category | Trend | Reason | Warning prev->curr | Avg lowest margin prev->curr |
|---|---|---|---|---|
| General Chat | worsening | avg_margin_delta:-2.49 | 2 -> 2 | 72.44 -> 69.95 |

### Repeated LOW_MARGIN_WARNING inventory

- `gemini-3-flash-preview-nothinking`
- `gemini-3-flash-preview-thinking`
- `gemini-3.1-pro-preview`
- `gemini-3.1-pro-preview-high`
- `gemini-3.1-pro-preview-low`
- `gemini-3.1-pro-preview-medium`
- `gpt-4o-audio-preview`
- `gpt-4o-mini-realtime-preview`
- `gpt-4o-mini-search-preview`
- `gpt-4o-mini-transcribe`
- `gpt-4o-realtime-preview`
- `gpt-4o-search-preview`
- `gpt-4o-transcribe`
- `gpt-5-search-api`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-audio`
- `o4-mini-deep-research`

---

## 5) Оставшиеся риски и интерпретация

1. `repeated_low_margin_models = 18` означает устойчивую зону тонкой маржи: это governance-сигнал для monitor-only / provider-path review, но не auto repricing.
2. Category-level worsening в `General Chat` связан с `avg_margin_delta`, при этом warning-count не вырос (`2 -> 2`). Это нужно трактовать как сигнал для внимательного мониторинга, а не как автоматический pricing action.
3. Улучшение `gpt-4.1` (`unknown -> ok`) отражает улучшение покрытости economics (confidence), но всё ещё требует осторожной интерпретации до перехода в `Exact`.

---

## 6) Вердикт BLOCK A

`MARGIN_TREND_MONITORING gap` закрыт в рамках minimal implementation: тренд-слой теперь формализован и воспроизводим, без нарушения retail/pricing boundary.

