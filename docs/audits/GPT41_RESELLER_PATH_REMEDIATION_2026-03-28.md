# GPT-4.1 Reseller Path Remediation Audit

**Дата:** 2026-03-28  
**Модель:** `gpt-4.1` (без суффикса)  
**Alert статус до:** INCOMPLETE_ECONOMICS HIGH  
**Правило:** retail tariff НЕ изменяется

---

## 1. Retail source (billing.public_model_tariff)

| Поле | Значение |
|---|---|
| `public_model_name` | `gpt-4.1` |
| `billing_unit` | `token` |
| `input_rate_credits` | `0.00000424` |
| `output_rate_credits` | `0.00001694` |
| `notes` | `OpenAI gpt-4.1; $2.00/$8 per 1M × markup 2x` |
| `is_active` | `true` |

**Статус:** retail truth существует ✅

---

## 2. LiteLLM config анализ

**Файл:** `/docker/litellm-xne6/config.yaml`

**Результат:** `gpt-4.1` (model_name без суффикса) **ОТСУТСТВУЕТ** в конфиге.

| model_name | Статус в config |
|---|---|
| `gpt-4.1-mini` | ✅ Есть (POLO order:1, JENIYA order:2) |
| `gpt-4.1-nano` | ✅ Есть (POLO order:1, JENIYA order:2) |
| `gpt-4.1` | ❌ Нет ни одного entry |

---

## 3. Где рвётся economics completeness

| Gap | Детали |
|---|---|
| **Нет provider mapping** | `gpt-4.1` не сконфигурирован в LiteLLM routing |
| **Нет cost basis** | Нет `model_info.input_cost_per_token` / `output_cost_per_token` |
| **Нет reseller path** | Неизвестно через POLO / JENIYA / ANIDEAAI или прямой OpenAI |
| **Нет трафика** | Без LiteLLM routing трафик на gpt-4.1 не маршрутизируется |

**Root cause:** Модель добавлена в `billing.public_model_tariff` (retail ready), но не добавлена в LiteLLM routing config. Отсутствует как deployable route → нет cost basis → Incomplete economics.

---

## 4. Связанные модели — паттерн для reference

`gpt-4.1-mini` и `gpt-4.1-nano` показывают паттерн:

```yaml
# gpt-4.1-mini — POLO
- model_name: gpt-4.1-mini
  litellm_params:
    model: openai/gpt-4.1-mini
    api_base: https://poloai.top/v1
    api_key: os.environ/POLO_AZ_API_KEY
    order: 1
  model_info:
    input_cost_per_token: 8.2e-08   # $0.082/1M
    output_cost_per_token: 3.29e-07  # $0.329/1M

# gpt-4.1-mini — JENIYA
- model_name: gpt-4.1-mini
  litellm_params:
    model: openai/gpt-4.1-mini
    api_base: https://jeniya.top/v1
    api_key: os.environ/JENIYA_AZ15_API_KEY
    order: 2
  model_info:
    input_cost_per_token: 8.2e-08
    output_cost_per_token: 3.29e-07
```

Оба reseller (POLO, JENIYA) поддерживают семейство gpt-4.1-* — likely они же могут поддерживать gpt-4.1.

---

## 5. Можно ли закрыть gap без изменения retail pricing?

**Да — но только после бизнес-решения по routing.**

**Шаги для закрытия gap:**
1. Решить через какой reseller маршрутизировать gpt-4.1 (POLO? JENIYA? оба?)
2. Проверить поддерживает ли reseller `gpt-4.1` базовую модель
3. Добавить entry в LiteLLM config с `model_info.input/output_cost_per_token`
4. Обновить economics matrix с `confidence = Estimated` (если cost basis из provider pattern) или `Exact` (если есть invoice)
5. Retail tariff НЕ трогать

**Blocker:** без подтверждения reseller поддержки gpt-4.1 — нельзя добавить routing и cost basis.

---

## 6. Estimated cost basis (для внутреннего расчёта)

Если POLO/JENIYA поддерживают gpt-4.1 по официальному OpenAI pricing ($2.00/$8.00/1M):

```
provider_input_cost_usd_per_1m  = 2.00   (official OpenAI, Estimated)
provider_output_cost_usd_per_1m = 8.00   (official OpenAI, Estimated)

retail_input_usd_per_1m  = 0.00000424 × 1_000_000 × 85 ÷ 90 = 4.005
retail_output_usd_per_1m = 0.00001694 × 1_000_000 × 85 ÷ 90 = 16.003

input_margin_pct  = (4.005 - 2.00) / 4.005 × 100 = 50.0%
output_margin_pct = (16.003 - 8.00) / 16.003 × 100 = 50.0%
```

**Economics confidence при Estimated basis: OK** — margin ~50%, в норме.

*Но это Estimated — реальная стоимость через reseller может отличаться.*
