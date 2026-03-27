# Operator Troubleshooting Source Map

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Назначение:** Справочник источников данных для operator troubleshooting. Не для клиентов.

---

## Источники данных

### 1. `billing.usage_billing_snapshot` — главная запись дебета

**Авторитетен для:** каждое конкретное списание, его сумма, токены, модель, время  
**Не авторитетен для:** тарифная ставка (не хранится в снимке), upstream routing path

| Поле | Тип | Видимость | Назначение |
|---|---|---|---|
| `id` | UUID | operator | Внутренний ID снимка |
| `litellm_spend_log_id` | String | operator | Ссылка на LiteLLM spend log |
| `user_id` | UUID | operator | Портальный ID пользователя |
| `api_key_hash` | String | operator (full) | Хеш API ключа |
| `public_model_name` | String | клиент + operator | Публичное имя модели |
| `provider` | String | **operator only** | Upstream провайдер (openai/anthropic/google) |
| `input_tokens` | Integer | клиент + operator | Входные токены |
| `output_tokens` | Integer | клиент + operator | Выходные токены |
| `raw_provider_cost_usd` | Decimal | **operator only** | Upstream стоимость в USD |
| `charged_credits` | Decimal | клиент + operator | Списанные кредиты (итог) |
| `loyalty_discount_percent` | Decimal | клиент + operator | Применённая скидка |
| `created_at` | DateTime | клиент + operator | Время записи |

**Когда консультировать:** всегда как первый шаг. Содержит исходные данные события.

---

### 2. `billing.public_model_tariff` — тарифная таблица

**Авторитетен для:** текущий тарифный план модели, `billing_unit`, ставки  
**Не авторитетен для:** ставка применённая к конкретному историческому дебету (тариф мог измениться)

| Поле | Тип | Видимость | Назначение |
|---|---|---|---|
| `public_model_name` | String | публичный | Ключ — имя модели |
| `billing_unit` | String | **operator** | `token` / `audio_token` / `search_token` / `realtime_token` / `research_token` |
| `input_rate_credits` | Decimal | публичный (/tariffs) | Ставка за входной токен/единицу |
| `output_rate_credits` | Decimal | публичный (/tariffs) | Ставка за выходной токен/единицу |
| `request_minimum_credits` | Decimal | operator | Минимум за запрос |
| `active_from` | DateTime | operator | Дата вступления тарифа в силу |
| `is_active` | Boolean | operator | Активен ли тариф |
| `notes` | Text | operator | Примечания |

**Когда консультировать:** при проверке ставки. Помни: `active_from` — тариф мог быть другим на момент дебета.

---

### 3. `billing.credit_ledger` — ledger движений баланса

**Авторитетен для:** фактическое изменение баланса (`amount_credits`), `balance_after`  
**Не авторитетен для:** детали модели/токенов (их нет в ledger)

| Поле | Тип | Назначение |
|---|---|---|
| `source_type` | String | `usage_debit` / `recharge` / `bonus` / `refund` |
| `amount_credits` | Decimal | Δ баланса (отрицательный = дебет) |
| `balance_after` | Decimal | Баланс после операции |
| `reference_id` | String | Ссылка на `usage_billing_snapshot.id` для дебетов |
| `created_at` | DateTime | Время ledger записи |

**Когда консультировать:** при проверке «почему изменился баланс» — ledger показывает реальное списание с балансом до/после.

**Cross-reference:**
```sql
SELECT l.amount_credits, l.balance_after, s.charged_credits, s.public_model_name
FROM billing.credit_ledger l
JOIN billing.usage_billing_snapshot s ON s.id::text = l.reference_id
WHERE l.user_id = '<user_id>' AND l.source_type = 'usage_debit'
ORDER BY l.created_at DESC LIMIT 20;
```

---

### 4. GET /billing/usage-logs — customer API

**Авторитетен для:** customer-visible представление дебетов  
**Не авторитетен для:** internal поля (provider, raw_provider_cost_usd, litellm_spend_log_id, billing_unit)

Возвращает:
- `billing_type_label`: Standard / Estimated
- `proxy_billed`: boolean
- `caveat_text`: текст для клиента
- **Не возвращает:** provider, raw cost, litellm ref, billing_unit, rates

**Когда консультировать:** чтобы понять что видит клиент. Не для operator troubleshooting.

---

### 5. GET /billing/usage/summary — customer summary API

**Авторитетен для:** агрегированный Standard/Estimated split за период  
**Не авторитетен для:** детали отдельной строки

**Когда консультировать:** при жалобе на общую сумму за период, не конкретный дебет.

---

### 6. GET /billing/models/tariffs — публичный каталог

**Авторитетен для:** текущие активные тарифы для клиентов  
**Не авторитетен для:** исторические тарифы, billing_unit (не возвращается)

**Когда консультировать:** для подтверждения что модель в каталоге, и какая текущая ставка.

---

### 7. GET /operator/usage-detail/{snapshot_id} — operator API (BLOCK C)

**Авторитетен для:** полный контекст конкретного дебета для оператора  
**Не авторитетен для:** batch-анализ, trending

Возвращает (после реализации BLOCK C):
- Все поля из `usage_billing_snapshot`
- `billing_unit` из `public_model_tariff`
- `input_rate_credits`, `output_rate_credits` (текущий тариф)
- `calculated_expected_credits` (проверочная формула)
- `provider`, `raw_provider_cost_usd` (internal only)
- `litellm_spend_log_id` (internal ref)

**Когда консультировать:** первый шаг при жалобе на конкретный дебет.

---

## Decision Tree для оператора

```
Жалоба получена
    │
    ├─ Жалоба на конкретную строку?
    │       ↓
    │   GET /operator/usage-detail/{snapshot_id}
    │       ↓
    │   billing_type_label = Standard?
    │       ├─ ДА: проверить charged vs. (tokens × rate × discount)
    │       └─ НЕТ (Estimated): объяснить через billing_unit + caveat_text
    │
    ├─ Жалоба на общую сумму за период?
    │       ↓
    │   GET /billing/usage/summary?date_from=...&date_to=...
    │       ↓
    │   Standard/Estimated split виден
    │
    └─ Жалоба на баланс (несоответствие)?
            ↓
        SQL: credit_ledger WHERE source_type='usage_debit'
            ↓
        Сравнить sum(amount_credits) с sum(charged_credits)
```

---

## Что НЕ раскрывать клиенту

| Данные | Причина |
|---|---|
| `provider` | Раскрывает routing и vendor mix |
| `raw_provider_cost_usd` | Коммерческая тайна (наша маржа) |
| `litellm_spend_log_id` | Internal system reference |
| `billing_unit` подробности | Не нужны клиенту, достаточно Standard/Estimated label |
| `input_rate_credits` × token расчёт | Может использоваться для reverse-engineering тарифов |

---

*Источник истины: этот файл. Последнее обновление: 2026-03-27.*
