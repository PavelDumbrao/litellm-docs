# LOW_MARGIN Governance Audit

**Дата:** 2026-03-28  
**Scope:** production economics governance pass для `LOW_MARGIN_WARNING` + `ESTIMATED_ONLY_CATEGORY`  
**Граница:** `billing.public_model_tariff` остаётся единственным retail source of truth; audit не меняет retail-тарифы.

---

## 1) Источники данных

- `billing-portal-src/app/api/billing.py`
  - `OPERATOR_ECONOMICS_MODEL_MATRIX_TSV` (snapshot: 2026-03-27)
  - `_evaluate_margin_alerts()` (canonical logic классификации)
- `docs/current/MARGIN_ALERT_POLICY.md`
- `docs/current/ECONOMICS_PRICING_BOUNDARY.md`

---

## 2) Репликация alert-среза

- `SUMMARY_BY_CLASS`: `{'LOW_MARGIN_WARNING': 18, 'ESTIMATED_ONLY_CATEGORY': 4, 'TEST_ONLY_INCOMPLETE': 3}`
- `LOW_COUNT`: `18`
- `BY_CATEGORY`: `{'Audio/Speech': 2, 'Gemini': 6, 'General Chat': 2, 'Realtime': 2, 'Search/Research': 4, 'Transcription': 2}`
- `BY_CONFIDENCE`: `{'Estimated': 10, 'Exact': 8}`
- `BY_LOWEST_MARGIN_BAND`: `{'45-48.99': 4, '49-49.99': 14}`

Интерпретация:
- `NEGATIVE_MARGIN` = 0 (production)
- `LOW_MARGIN_CRITICAL` = 0 (production)
- Оставшийся production-сигнал: 18 `LOW_MARGIN_WARNING` + 4 `ESTIMATED_ONLY_CATEGORY`

---

## 3) Инвентарь LOW_MARGIN_WARNING (18 моделей)

| Модель | Категория | Confidence | Провайдер | Input margin % | Output margin % | Lowest margin % | Причина | Решение | Приоритет |
|---|---|---|---|---:|---:|---:|---|---|---|
| `gpt-5.4-nano` | General Chat | Exact | JENIYA | 47.06 | 49.58 | 47.06 | thin_exact_margin | provider_path_review | P1 |
| `gemini-3-flash-preview-nothinking` | Gemini | Exact | POLO | 48.57 | 49.98 | 48.57 | thin_exact_margin | provider_path_review | P1 |
| `gemini-3-flash-preview-thinking` | Gemini | Exact | POLO | 48.57 | 49.98 | 48.57 | thin_exact_margin | provider_path_review | P1 |
| `gpt-4o-mini-search-preview` | Search/Research | Estimated | POLO | 48.82 | 49.26 | 48.82 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-4o-mini-transcribe` | Transcription | Estimated | POLO | 49.61 | 49.89 | 49.61 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-4o-mini-realtime-preview` | Realtime | Estimated | POLO | 49.91 | 49.81 | 49.81 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-5.4-mini` | General Chat | Exact | JENIYA | 51.13 | 49.85 | 49.85 | near_threshold_exact_margin | monitor_only | P2 |
| `gpt-4o-realtime-preview` | Realtime | Estimated | POLO | 49.89 | 49.98 | 49.89 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-audio` | Audio/Speech | Estimated | POLO | 50.07 | 49.89 | 49.89 | proxy_economics_estimation | monitor_only | P2 |
| `gemini-3.1-pro-preview` | Gemini | Exact | POLO | 49.98 | 49.98 | 49.98 | near_threshold_exact_margin | monitor_only | P2 |
| `gemini-3.1-pro-preview-high` | Gemini | Exact | POLO | 49.98 | 49.98 | 49.98 | near_threshold_exact_margin | monitor_only | P2 |
| `gemini-3.1-pro-preview-low` | Gemini | Exact | POLO | 49.98 | 49.98 | 49.98 | near_threshold_exact_margin | monitor_only | P2 |
| `gemini-3.1-pro-preview-medium` | Gemini | Exact | POLO | 49.98 | 49.98 | 49.98 | near_threshold_exact_margin | monitor_only | P2 |
| `gpt-4o-audio-preview` | Audio/Speech | Estimated | POLO | 50.07 | 49.98 | 49.98 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-4o-search-preview` | Search/Research | Estimated | POLO | 50.07 | 49.98 | 49.98 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-4o-transcribe` | Transcription | Estimated | POLO | 50.07 | 49.98 | 49.98 | proxy_economics_estimation | monitor_only | P2 |
| `gpt-5-search-api` | Search/Research | Estimated | POLO | 50.07 | 49.98 | 49.98 | proxy_economics_estimation | monitor_only | P2 |
| `o4-mini-deep-research` | Search/Research | Estimated | POLO | 49.98 | 49.98 | 49.98 | proxy_economics_estimation | monitor_only | P2 |

Легенда причин:
- `proxy_economics_estimation` — оценочная economics-модель, требуется точный provider cost для ужесточения confidence.
- `thin_exact_margin` — exact-данные, но минимальная маржа <49%; кандидаты для targeted review.
- `near_threshold_exact_margin` — exact-данные около порога 50%; достаточно мониторинга.

---

## 4) ESTIMATED_ONLY_CATEGORY (4 категории)

| Категория | Статус | Действие |
|---|---|---|
| Audio/Speech | ESTIMATED_ONLY_CATEGORY | Держать в мониторинге и переводить в Exact после появления подтверждённого provider cost basis. |
| Realtime | ESTIMATED_ONLY_CATEGORY | Держать в мониторинге и переводить в Exact после появления подтверждённого provider cost basis. |
| Search/Research | ESTIMATED_ONLY_CATEGORY | Держать в мониторинге и переводить в Exact после появления подтверждённого provider cost basis. |
| Transcription | ESTIMATED_ONLY_CATEGORY | Держать в мониторинге и переводить в Exact после появления подтверждённого provider cost basis. |

Категории: `Audio/Speech`, `Realtime`, `Search/Research`, `Transcription`.

---

## 5) Governance-классификация

### P1 — targeted provider-path review

- `gpt-5.4-nano` (47.06%) — Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail.
- `gemini-3-flash-preview-nothinking` (48.57%) — Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail.
- `gemini-3-flash-preview-thinking` (48.57%) — Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail.

### P2 — monitor-only

- Все Estimated LOW-модели (10)
- Exact near-threshold модели (4) в диапазоне 49.85–49.98%
- 4 категории ESTIMATED_ONLY_CATEGORY

### Вне production remediation scope

- `TEST_ONLY_INCOMPLETE` (3 i7dc-модели) остаются в test-only периметре.

---

## 6) Boundary compliance

- Retail не изменялся.
- Provider cost трактуется только как internal economics слой.
- Автоперезаписи customer pricing не выполнялись.

---

## 7) Вердикт

`LOW_MARGIN governance baseline подтверждён.`

- Production blocking alerts: **0**
- LOW_MARGIN_WARNING: **18**
- ESTIMATED_ONLY_CATEGORY: **4**
- Следующий шаг: decision matrix + (опционально) targeted remediation только на cost/routing слое и только со smoke-check.

