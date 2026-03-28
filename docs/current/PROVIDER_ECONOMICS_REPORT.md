# Provider Economics Report

**Дата:** 2026-03-27  
**Статус:** Internal report completed  
**BLOCK C:** выполнен как **report**, без добавления нового runtime endpoint

---

## 1. Что это

Это внутренний economics view по всем публичным моделям, собранный из live источников:

- `billing.public_model_tariff`
- `/opt/billing-portal/.env`
- `/docker/litellm-xne6/config.yaml`

Отчёт **не меняет customer UI**, **не меняет billing logic** и **не расширяет публичную API surface**.

---

## 2. Метод

### Retail side

```text
retail_rub_per_1m = rate_credits * 1_000_000 * 85
retail_usd_per_1m_fx90 = retail_rub_per_1m / 90
```

### Provider side

```text
provider_cost_usd_per_1m = cost_per_token * 1_000_000
```

### Margin

```text
primary_margin_pct = ((retail_usd_per_1m_fx90 - primary_provider_cost_usd_per_1m) / retail_usd_per_1m_fx90) * 100
```

### Caveat

- `FX90` используется как **аналитический proxy**, а не как runtime billing constant.
- Для special-unit моделей (`audio/search/realtime/research`) margin считается как **Estimated**, не Exact.

---

## 3. Confidence summary

| Confidence | Models |
|---|---:|
| Exact | 29 |
| Estimated | 11 |
| Incomplete | 4 |

### Incomplete models

- `gpt-4.1`
- `i7dc-claude-haiku-4-5`
- `i7dc-claude-sonnet-4-6`
- `i7dc-claude-opus-4-6`

---

## 4. Category rollup

| Category | Models | Confidence split | Avg input margin % | Avg output margin % | Комментарий |
|---|---:|---|---:|---:|---|
| Audio/Speech | 3 | 3 Estimated | 50.05 | 49.96 | Почти ровно 50/50 proxy-margin |
| Claude | 7 | 7 Exact | 96.54 | 96.55 | Самый аномально высокий exact-margin cluster |
| Embeddings | 3 | 3 Exact | 89.54 | — | Output почти не играет роли |
| Gemini | 10 | 10 Exact | 62.58 | 60.31 | Сильный разброс внутри семейства |
| General Chat | 9 | 8 Exact / 1 Incomplete | 72.67 | 73.61 | Внутри кластера большой разброс |
| I7DC Relay | 3 | 3 Incomplete | — | — | Нет complete retail-side coverage |
| Other | 1 | 1 Exact | 70.28 | 89.05 | Сейчас это `deepseek-v3.2` |
| Realtime | 2 | 2 Estimated | 49.90 | 49.89 | Почти ровный 50% proxy-margin |
| Search/Research | 4 | 4 Estimated | 49.73 | 49.80 | Почти ровный 50% proxy-margin |
| Transcription | 2 | 2 Estimated | 49.84 | 49.94 | Почти ровный 50% proxy-margin |

---

## 5. Главные выводы

### 5.1 Claude cluster — самый прибыльный exact cluster

Средний exact-margin по текущему primary path:

- **input:** `96.54%`
- **output:** `96.55%`

Причина:

- retail tariff в DB очень высокий,
- primary upstream path для части Claude-моделей идёт через `ANIDEAAI` / `JENIYA`,
- текущий provider cost кратно ниже retail proxy.

### 5.2 General Chat не однороден

Внутри General Chat есть как почти-50% модели, так и сильно более маржинальные:

- `gpt-5.3-codex` ≈ `50% / 50%`
- `gpt-5.4-mini` ≈ `51.13% / 49.85%`
- `gpt-5.4-nano` ≈ `47.06% / 49.58%`
- `gpt-5.4` ≈ `74.06% / 80.48%`
- `gpt-4o` ≈ `89.71% / 89.73%`
- `gpt-4.1-mini` и `gpt-4.1-nano` ≈ `89%+`

То есть General Chat — не единый pricing regime, а смесь нескольких regimes.

### 5.3 Gemini cluster тоже неоднороден

Ключевой split:

- `gemini-3-flash-preview-nothinking/thinking` ≈ `48.57% / 49.98%`
- `gemini-3.1-pro-preview*` ≈ `49.98% / 49.98%`
- `gemini-3-flash-preview` (JENIYA primary) ≈ `59.92% / 60.93%`
- `gemini-2.5-flash*` range ≈ `71%–93%` на части направлений

Следовательно, внутри Gemini family есть как почти идеальный 50% layer, так и materially more profitable slices.

### 5.4 Special-unit models — стабильный ~50% proxy layer

Все `Estimated` категории группируются около `50%` margin:

- Audio/Speech
- Realtime
- Search/Research
- Transcription

Это ожидаемо: текущий economics layer у них proxy-based и не должен трактоваться как fully exact.

### 5.5 Incomplete coverage нужно чинить отдельно

Самый важный incomplete case:

- `gpt-4.1` активен в retail tariff, но не найден как public model path в live `config.yaml`.

Также отдельный incomplete cluster:

- `i7dc-claude-haiku-4-5`
- `i7dc-claude-sonnet-4-6`
- `i7dc-claude-opus-4-6`

У них есть provider cost, но нет active tariff row.

---

## 6. Самые важные model-level observations

### Highest exact input margins

| Model | Input margin % | Output margin % |
|---|---:|---:|
| `claude-opus-4-6` | 99.07 | 99.07 |
| `claude-opus-4-5-thinking` | 98.17 | 98.17 |
| `claude-opus-4-6-thinking` | 97.26 | 97.26 |
| `claude-sonnet-4-6` | 97.17 | 97.20 |
| `claude-haiku-4-5` | 96.49 | 96.50 |

### Lowest exact input margins

| Model | Input margin % | Output margin % |
|---|---:|---:|
| `gpt-5.4-nano` | 47.06 | 49.58 |
| `gemini-3-flash-preview-nothinking` | 48.57 | 49.98 |
| `gemini-3-flash-preview-thinking` | 48.57 | 49.98 |
| `gemini-3.1-pro-preview` | 49.98 | 49.98 |
| `gpt-5.3-codex` | 50.50 | 50.00 |

---

## 7. Что делать дальше

### Не срочно, но важно

1. Отдельно расследовать `gpt-4.1`:
   - или добавить public routing path,
   - или убрать retail tariff,
   - или пометить как hidden/not-for-sale.

2. Отдельно решить I7DC cluster:
   - или добавить active tariff rows,
   - или убрать из public catalog docs.

3. Не использовать `LIVE_PRICING_REFERENCE.md` как economics truth без проверки против DB + `.env`.

### Не делать в этой итерации

- не менять customer pricing,
- не менять catalog,
- не менять billing logic,
- не добавлять новый публичный endpoint.

---

## 8. Ссылки на companion docs

- `docs/current/PROVIDER_ECONOMICS_SOURCE_MAP.md`
- `docs/current/PROVIDER_ECONOMICS_CONFIDENCE_MATRIX.md`
- `docs/audits/PROVIDER_ECONOMICS_GAP_AUDIT_2026-03-27.md`
- `docs/audits/PROVIDER_ECONOMICS_IMPLEMENTATION_2026-03-27.md`

---

## Финальный вывод

**BLOCK C закрыт как internal report.**  
Теперь есть единый внутренний economics view по:

- модели,
- категории,
- primary provider path,
- proxy-margin,
- confidence status.
