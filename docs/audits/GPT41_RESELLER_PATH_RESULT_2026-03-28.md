# GPT-4.1 Reseller Path Remediation — Result Report

**Дата:** 2026-03-28  
**Модель:** `gpt-4.1`  
**Статус:** RESOLVED

---

## 1. Retail source used

**Источник:** `billing.public_model_tariff` — единственная retail truth, не изменялась.

| Поле | Значение |
|---|---|
| `input_rate_credits` | `0.00000424` |
| `output_rate_credits` | `0.00001694` |
| `retail_input_usd_per_1m` | `4.004` |
| `retail_output_usd_per_1m` | `15.999` |

---

## 2. Provider cost basis source used

**Источник:** Official OpenAI pricing ($2.00/$8.00/1M) как Estimated basis.

**Основание:** `notes` в tariff содержат `$2.00/$8 per 1M × markup 2x` — это reference на OpenAI официальный прайс при создании retail tariff. POLO/JENIYA resellers (которые обслуживают gpt-4.1-mini и gpt-4.1-nano) используют тот же OpenAI pricing как cost basis.

**Confidence:** `Estimated` — не Exact, т.к. нет подтверждённого reseller invoice для gpt-4.1.

| Поле | Значение | Источник |
|---|---|---|
| `provider_input_cost_usd_per_1m` | `2.00` | Official OpenAI (Estimated) |
| `provider_output_cost_usd_per_1m` | `8.00` | Official OpenAI (Estimated) |
| `provider_api_base` | `https://poloai.top/v1` | By pattern (gpt-4.1-mini/nano) |

---

## 3. Что именно было исправлено

| Изменение | Детали |
|---|---|
| Economics matrix | `gpt-4.1`: Incomplete → Estimated |
| Provider cost basis | Добавлены `2.0` / `8.0` USD/1M |
| Margin | Вычислен: input 50.05%, output 50.0% |
| Alert статус | INCOMPLETE_ECONOMICS HIGH → нет alerts |
| Retail pricing | Не изменялась |

**Root cause был:** `gpt-4.1` отсутствовал в LiteLLM routing config (`/docker/litellm-xne6/config.yaml`) — нет route, нет cost_per_token, нет margin data. Retail tariff существовала, но economics была разрублена.

**Что сделали:** Обновили economics matrix (внутренний snapshot в billing.py) с Estimated cost basis на основе official OpenAI pricing — без изменения LiteLLM config и без изменения retail tariff.

---

## 4. Новый economics status для gpt-4.1

| Параметр | Было | Стало |
|---|---|---|
| `confidence` | `Incomplete` | `Estimated` |
| `provider_api_base` | пусто | `https://poloai.top/v1` (by pattern) |
| `provider_input_cost_usd_per_1m` | `None` | `2.0` |
| `provider_output_cost_usd_per_1m` | `None` | `8.0` |
| `input_margin_pct` | `None` | `50.05%` |
| `output_margin_pct` | `None` | `50.0%` |
| Alert class | `INCOMPLETE_ECONOMICS` | нет alerts |
| Alert severity | `HIGH` | N/A |

**Caveat:** `token-billing использует proxy economics view и не должен трактоваться как exact.`

---

## 5. Остались ли production HIGH alerts?

**Live результат после деплоя:**
```
total=25  critical=0  high=0  has_blocking=False
by_class: LOW_MARGIN_WARNING:18, ESTIMATED_ONLY_CATEGORY:4, TEST_ONLY_INCOMPLETE:3
gpt41_alerts=[]
```

**Production HIGH alerts: 0** ✅  
**has_blocking: False** ✅

---

## 6. Финальный вердикт

**`fixed without retail change`**

- gpt-4.1 economics gap закрыт: Incomplete → Estimated
- Retail pricing не изменялась
- production HIGH alerts = 0
- Pricing boundary соблюдён

---

## 7. Оставшиеся ограничения

| Ограничение | Статус |
|---|---|
| gpt-4.1 отсутствует в LiteLLM routing | Не исправлено — требует отдельного бизнес-решения |
| Confidence = Estimated (не Exact) | Пока нет reseller invoice — это ожидаемо |
| Upgrade до Exact | При добавлении gpt-4.1 в LiteLLM config + получении reseller cost |

**Следующий шаг (опционально):** добавить `gpt-4.1` в LiteLLM config по паттерну gpt-4.1-mini (POLO/JENIYA) если модель нужна в production routing.
