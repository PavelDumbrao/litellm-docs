# HIGH Alerts Remediation Under Pricing Boundary

**Дата:** 2026-03-28  
**Контекст:** Margin alerts layer live. HIGH alerts требуют разбора под строгим pricing boundary (см. `docs/current/ECONOMICS_PRICING_BOUNDARY.md`).  
**Правило:** retail tariff НЕ изменяется. Provider cost basis ищется отдельно.

---

## Текущие HIGH alerts (из /operator/margin-alerts)

| Модель | Alert class | Severity |
|---|---|---|
| `gpt-4.1` | INCOMPLETE_ECONOMICS | HIGH |
| `i7dc-claude-haiku-4-5` | INCOMPLETE_ECONOMICS | HIGH |
| `i7dc-claude-opus-4-6` | INCOMPLETE_ECONOMICS | HIGH |
| `i7dc-claude-sonnet-4-6` | INCOMPLETE_ECONOMICS | HIGH |

---

## MODEL 1: gpt-4.1

### Retail source (billing.public_model_tariff)

| Поле | Значение |
|---|---|
| `public_model_name` | `gpt-4.1` |
| `billing_unit` | `token` |
| `input_rate_credits` | `0.00000424` |
| `output_rate_credits` | `0.00001694` |
| `notes` | `OpenAI gpt-4.1; $2.00/$8 per 1M × markup 2x` |
| `is_active` | `true` |

**Retail в USD/1M (proxy FX 90):**
- input: `0.00000424 × 1_000_000 × 85 ÷ 90 = 4.005 USD/1M`
- output: `0.00001694 × 1_000_000 × 85 ÷ 90 = 16.003 USD/1M`

### Provider cost basis analysis

**Notes в тарифе указывают:** `$2.00/$8 per 1M × markup 2x`

Это значит:
- notes-based provider cost: input = $2.00/1M, output = $8.00/1M
- НО: это официальный OpenAI pricing, а не подтверждённый reseller cost
- Provider path для gpt-4.1 в economics matrix отсутствует (`provider_api_base` пустой)

**Критически важно:** `notes` в tariff содержат упоминание официальных OpenAI цен как reference для markup расчёта. Это НЕ означает что наш реальный provider cost = $2.00/$8.00. У нас нет подтверждённого reseller path для gpt-4.1.

### Margin estimate (только если notes-cost использовать как Estimated basis)

```
input_margin = (4.005 - 2.00) / 4.005 × 100 = ~50.0%  ← ОК
output_margin = (16.003 - 8.00) / 16.003 × 100 = ~50.0%  ← ОК
```

*Но это Estimated calculation — реальный reseller cost неизвестен.*

### Вердикт

| Критерий | Статус |
|---|---|
| Retail source | ✅ Есть в billing.public_model_tariff |
| Provider cost basis | ❌ Нет подтверждённого reseller path |
| Можно перевести в Exact? | ❌ Нет — нужен реальный provider invoice |
| Можно перевести в Estimated? | ⚠️ Частично — если официальный OpenAI pricing = наш reseller cost (не подтверждено) |
| Retail price изменяется? | ❌ Нет — retail корректна, margin при Estimated basis ~50% |
| Gap fixable without retail change? | ✅ Да — нужно только подтвердить provider path |

**Action required:**
1. Определить через какой reseller идёт трафик gpt-4.1 (POLO? ANIDEAAI? прямой OpenAI?)
2. Запросить реальный cost у reseller
3. Обновить economics matrix с `confidence = Exact` и реальным `provider_input/output_cost`
4. Retail тариф НЕ трогать

---

## MODEL 2: i7dc-claude-haiku-4-5

### Retail source (billing.public_model_tariff)

**Результат запроса:** 0 rows — модель ОТСУТСТВУЕТ в `billing.public_model_tariff`.

### Provider cost basis analysis

В economics matrix:
- `confidence = Incomplete`
- `provider_api_base = https://i7dc.com/api`
- `provider_input_cost_usd_per_1m = 0.15`
- `provider_output_cost_usd_per_1m = 0.75`

*Источник этих cost-данных неизвестен — нет документации.*

### Вердикт

| Критерий | Статус |
|---|---|
| Retail source | ❌ НЕТ в billing.public_model_tariff |
| Provider cost basis | ❌ Частичные данные без подтверждённого источника |
| Можно перевести в Exact? | ❌ Нет — нет retail tariff |
| Gap fixable without retail change? | ❌ Нет — нужно сначала создать retail tariff entry |
| Retail price изменяется? | N/A — retail записи не существует |

**Action required:**
1. Запросить актуальный прайс у i7dc.com (Claude Haiku)
2. Создать retail tariff entry в `billing.public_model_tariff` с обоснованным markup
3. Обновить economics matrix с реальным cost basis
4. До создания retail entry — модель технически работает через LiteLLM, но не биллится через наш portal

---

## MODEL 3: i7dc-claude-opus-4-6

### Retail source (billing.public_model_tariff)

**Результат запроса:** 0 rows — модель ОТСУТСТВУЕТ в `billing.public_model_tariff`.

### Provider cost basis analysis

В economics matrix:
- `confidence = Incomplete`
- `provider_api_base = https://i7dc.com/api`
- `provider_input_cost_usd_per_1m = 0.75`
- `provider_output_cost_usd_per_1m = 3.75`

### Вердикт

| Критерий | Статус |
|---|---|
| Retail source | ❌ НЕТ в billing.public_model_tariff |
| Provider cost basis | ❌ Без подтверждённого источника |
| Gap fixable without retail change? | ❌ Нет retail entry |

**Action required:** аналогично i7dc-claude-haiku-4-5.

---

## MODEL 4: i7dc-claude-sonnet-4-6

### Retail source (billing.public_model_tariff)

**Результат запроса:** 0 rows — модель ОТСУТСТВУЕТ в `billing.public_model_tariff`.

### Provider cost basis analysis

В economics matrix:
- `confidence = Incomplete`
- `provider_api_base = https://i7dc.com/api`
- `provider_input_cost_usd_per_1m = 0.45`
- `provider_output_cost_usd_per_1m = 2.25`

### Вердикт

| Критерий | Статус |
|---|---|
| Retail source | ❌ НЕТ в billing.public_model_tariff |
| Provider cost basis | ❌ Без подтверждённого источника |
| Gap fixable without retail change? | ❌ Нет retail entry |

**Action required:** аналогично i7dc-claude-haiku-4-5.

---

## Сводная таблица remediation

| Модель | Retail в tariff | Provider cost basis | Fixable gap? | Retail change? | Economics status после action |
|---|---|---|---|---|---|
| `gpt-4.1` | ✅ Есть | ❌ Нет reseller path | ✅ Да (нужен provider path) | ❌ Нет | Estimated → Exact после подтверждения |
| `i7dc-claude-haiku-4-5` | ❌ Нет | ❌ Неподтверждённый | ❌ Нет retail entry | N/A | Blocked — нужна retail entry + i7dc invoice |
| `i7dc-claude-opus-4-6` | ❌ Нет | ❌ Неподтверждённый | ❌ Нет retail entry | N/A | Blocked — нужна retail entry + i7dc invoice |
| `i7dc-claude-sonnet-4-6` | ❌ Нет | ❌ Неподтверждённый | ❌ Нет retail entry | N/A | Blocked — нужна retail entry + i7dc invoice |

---

## Финальный вердикт

### gpt-4.1

**`gap partially fixable — no retail change required`**

- Retail tariff корректна и существует
- При подтверждении reseller path → можно перевести в Estimated (official OpenAI cost как basis) или Exact (reseller invoice)
- Retail НЕ изменяется
- HIGH alert закрывается после подтверждения provider path

### i7dc-claude-haiku/opus/sonnet

**`blocked by missing retail tariff entry + missing provider cost basis`**

- Модели не имеют retail entry в `billing.public_model_tariff`
- Economics remediation без retail entry невозможна по принципу pricing boundary
- Action: запросить i7dc прайс → создать retail tariff entry → добавить в economics matrix
- До создания retail entry — HIGH alert остаётся активным

---

## Pricing boundary соблюдён

- Ни один retail тариф не был изменён в ходе этого анализа
- Официальный OpenAI pricing (упомянутый в notes `gpt-4.1`) рассматривается только как Estimated cost basis, не как retail
- i7dc cost данные в economics matrix (0.15/0.75, 0.75/3.75, 0.45/2.25) — без подтверждённого источника, рассматриваются как Incomplete
- Все решения по retail требуют явного operator action с аудитом
