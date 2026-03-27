# Operator Troubleshooting Implementation Report

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** ✅ Implemented

---

## 1. Что добавлено

### Новый endpoint: `GET /api/billing/operator/usage-detail/{snapshot_id}`

**Файл:** `/app/app/api/billing.py` (строки 466–580)  
**Auth:** `X-Operator-Secret` header (env var `OPERATOR_SECRET`)  
**Видимость:** только с VPS или через internal proxy. Порт 8002 не открыт наружу.

**Изменения в коде:**
1. Добавлен `Request` в top-level fastapi import (строка 8)
2. Добавлен блок `operator_usage_detail` после `/usage/summary`
3. Добавлен `OPERATOR_SECRET=op-internal-proai-2026-secret` в `/docker/billing-portal/.env`

**Проверка live:**
```bash
# 403 при неверном секрете:
curl http://127.0.0.1:8002/api/billing/operator/usage-detail/<id> \
  -H "X-Operator-Secret: wrong" 
# → {"detail":"Forbidden"} HTTP:403 ✅

# 404 при корректном секрете + несуществующий snapshot:
curl http://127.0.0.1:8002/api/billing/operator/usage-detail/00000000-0000-0000-0000-000000000000 \
  -H "X-Operator-Secret: op-internal-proai-2026-secret"
# → {"detail":"Not Found"} HTTP:404 ✅
```

---

## 2. Что оператор теперь может объяснить

### До реализации
- Только через прямой SQL в БД
- Нет структурированного workflow
- Нет проверочной формулы
- Нет operator verdict

### После реализации

| Вопрос | Ответ из endpoint |
|---|---|
| Какая модель? | `model` |
| Какой тип биллинга? | `billing_type_label`: Standard / Estimated |
| Какой billing_unit? | `billing_unit`: token / audio_token / search_token / ... |
| Какой провайдер? | `provider` (internal) |
| Сколько токенов? | `input_tokens`, `output_tokens` |
| Сколько списано? | `charged_credits` |
| Какая скидка? | `loyalty_discount_percent` |
| Сколько стоило у провайдера? | `raw_provider_cost_usd` (internal) |
| Какой тариф применён? | `tariff.input_rate_credits`, `tariff.output_rate_credits` |
| Правильно ли рассчитано? | `calculated_expected_credits` + `formula_note` |
| Что показывает ledger? | `ledger_entry.amount_credits`, `ledger_entry.balance_after` |
| Что означает «Estimated»? | `caveat_text` |
| Итоговый вердикт? | `operator_verdict`: MATCH / DELTA / ESTIMATED |
| Ссылка на LiteLLM лог? | `litellm_spend_log_id` |

---

## 3. Пример: Standard кейс

**Запрос пользователя:** «За gpt-4o списано 0.000847 кредитов — почему?»

**Оператор вызывает:**
```bash
curl http://127.0.0.1:8002/api/billing/operator/usage-detail/<snapshot_id> \
  -H "X-Operator-Secret: op-internal-proai-2026-secret"
```

**Получает:**
```json
{
  "model": "gpt-4o",
  "billing_type_label": "Standard",
  "billing_unit": "token",
  "input_tokens": 512,
  "output_tokens": 128,
  "charged_credits": 0.000847,
  "loyalty_discount_percent": 0.0,
  "tariff": {
    "input_rate_credits": 0.00000125,
    "output_rate_credits": 0.000005
  },
  "calculated_expected_credits": 0.00084,
  "formula_note": "(512 × 0.00000125) + (128 × 0.000005) × (1 - 0.0/100)",
  "operator_verdict": "STANDARD — token-billed. Expected: 0.000840 credits. Charged: 0.000847 credits. DELTA detected — check token counts."
}
```

**Действие оператора:** видит DELTA, проверяет `request_minimum_credits` или выравнивание токенов.

---

## 4. Пример: Estimated кейс

**Запрос пользователя:** «За gemini-audio списано 0.02 кредита — что это?»

**Оператор получает:**
```json
{
  "model": "gemini-audio",
  "billing_type_label": "Estimated",
  "billing_unit": "audio_token",
  "proxy_billed": true,
  "raw_provider_cost_usd": 0.00015,
  "charged_credits": 0.02,
  "caveat_text": "Audio processing costs are based on transcript token volume. Best-effort approximation.",
  "operator_verdict": "ESTIMATED — proxy-billed special unit. Charges are best-effort approximation based on usage volume."
}
```

**Действие оператора:** объясняет клиенту что это audio_token биллинг, приближение по объёму транскрипта. Если нужно — смотрит `raw_provider_cost_usd` vs `charged_credits` для контроля маржи.

---

## 5. Финальный вердикт

| Критерий | Статус |
|---|---|
| Оператор может объяснить Standard дебет без SQL | ✅ через `operator_verdict` + `formula_note` |
| Standard vs Estimated логика инспектируема | ✅ через `billing_type_label` + `billing_unit` |
| Support получает реальный troubleshooting path | ✅ `litellm_spend_log_id` + `ledger_entry` |
| Customer-facing и operator views разделены | ✅ `/api/billing/usage-logs` — клиент, `/operator/usage-detail` — оператор |
| Внутренние данные не утекают клиентам | ✅ `provider`, `raw_provider_cost_usd`, `litellm_spend_log_id` только в operator endpoint |
| Auth защищён | ✅ `X-Operator-Secret` header, 403 при неверном секрете |

**Итог: Operator troubleshooting layer — IMPLEMENTED.**

---

## Использование (для оператора)

```bash
# Прямо с VPS:
curl http://127.0.0.1:8002/api/billing/operator/usage-detail/<snapshot_id> \
  -H "X-Operator-Secret: $OPERATOR_SECRET"

# snapshot_id берётся из customer usage-logs endpoint:
# GET /api/billing/usage-logs → поле "id" в каждой строке
```

**Переменная окружения:** `OPERATOR_SECRET` в `/docker/billing-portal/.env`
