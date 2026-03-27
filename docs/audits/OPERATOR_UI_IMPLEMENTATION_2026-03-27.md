# Operator UI Implementation Report

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** ✅ Implemented

---

## 1. Что добавлено

### Экран / компонент

Добавлен **minimal internal operator UI** прямо в существующий экран `Usage`:

- **Файл:** `billing-portal-src/frontend/src/pages/Usage.tsx`
- **Точка входа:** `/usage?operator=1`
- **Customer default path:** `/usage`

Отдельная страница и отдельный route **не добавлялись**. Это сделано специально, чтобы:

1. не расширять customer-facing surface,
2. не добавлять новую публичную навигацию,
3. оставить operator flow как скрытый internal режим поверх уже существующей usage table.

### Что появилось в UI

1. **Operator mode card** вверху страницы при открытии `/usage?operator=1`
2. Ввод `X-Operator-Secret` через `prompt()`
3. Хранение секрета в `localStorage` (`billing_operator_secret`)
4. Новая колонка **Operator** в usage table только в operator mode
5. Кнопка **Details** у каждой usage/debit строки
6. **Modal operator details** с полным internal troubleshooting context

---

## 2. Как оператор находит snapshot и открывает details

### Реальный workflow

1. Оператор открывает:

```text
/usage?operator=1
```

2. Видит обычную usage table, но в internal режиме — с колонкой **Operator**

3. Нажимает **Details** у нужной строки

4. Frontend использует уже существующий `log.id` как `snapshot_id`

5. Делает запрос:

```http
GET /api/billing/operator/usage-detail/{snapshot_id}
Authorization: Bearer <jwt>
X-Operator-Secret: <secret>
```

6. Показывает modal с internal полями

### Важный факт

Никакой SQL для поиска `snapshot_id` больше не нужен:

- `snapshot_id` уже присутствует в каждом usage row (`log.id`)
- UI просто использует его напрямую

---

## 3. Какие internal fields показываются

### Billing context

- `model`
- `charged_credits`
- `billing_type_label`
- `billing_unit`
- `provider`
- `raw_provider_cost_usd`
- `created_at`
- `snapshot_id`
- `litellm_spend_log_id`
- `api_key_hash`

### Tariff + formula

- `tariff.input_rate_credits`
- `tariff.output_rate_credits`
- `tariff.active_from`
- `tariff.notes`
- `calculated_expected_credits`
- `formula_note`
- `input_tokens`
- `output_tokens`
- `loyalty_discount_percent`

### Ledger reference

- `ledger_entry.amount_credits`
- `ledger_entry.balance_after`
- `ledger_entry.created_at`
- `user_id`

### Final operator decision

- `operator_verdict`
- `caveat_text` (для Estimated/proxy-billed строк)

---

## 4. Что остаётся скрытым от customer surface

Следующие поля **не попадают** в обычный customer flow `/usage`:

| Поле | Customer `/usage` | Operator `/usage?operator=1` |
|---|---|---|
| `provider` | ❌ | ✅ |
| `raw_provider_cost_usd` | ❌ | ✅ |
| `litellm_spend_log_id` | ❌ | ✅ |
| `billing_unit` | ❌ | ✅ |
| `api_key_hash` full | ❌ | ✅ |
| `formula_note` | ❌ | ✅ |
| `calculated_expected_credits` | ❌ | ✅ |
| `ledger_entry` | ❌ | ✅ |
| `operator_verdict` | ❌ | ✅ |

### Почему это безопасно

Operator UI защищён **двумя слоями**:

1. **UI gating** — internal controls видны только при `?operator=1`
2. **Backend auth** — без корректного `X-Operator-Secret` endpoint возвращает `403`

То есть даже если customer вручную откроет `/usage?operator=1`, internal data не раскроются без секрета.

---

## 5. Auth / access safety

### Что реализовано

- Operator mode не добавлен в sidebar/navigation
- Новый route не создан
- Customer default path остаётся `/usage`
- Internal режим включается только query param `?operator=1`
- Secret хранится локально в браузере оператора
- Secret можно обновить или очистить через UI
- Backend остаётся главным барьером безопасности

### Конфиг / env

Для operator API уже используется:

```env
OPERATOR_SECRET=op-internal-proai-2026-secret
```

### Практический internal entrypoint

```text
https://billing.proaicommunity.online/usage?operator=1
```

---

## 6. Что именно было изменено в коде

### `Usage.tsx`

Добавлены:

- типы `OperatorDetail`, `OperatorTariff`, `OperatorLedgerEntry`
- helper formatting functions
- `OperatorModeCard`
- `OperatorDetailModal`
- секции modal:
  - billing context
  - tariff + formula
  - ledger reference
  - operator verdict
- кнопка `Details` в usage table
- fetch к operator endpoint с `X-Operator-Secret`
- локальное хранение operator secret

### Build / deploy

Frontend успешно собран и задеплоен:

```bash
cd /opt/billing-portal/frontend && npm run build
docker cp /opt/billing-portal/static/. billing-portal:/app/static/
docker restart billing-portal
```

Build status: **PASS**

---

## 7. Финальный вердикт

| Критерий | Статус |
|---|---|
| Support/operator может inspect debit без SQL | ✅ |
| Snapshot открывается прямо из usage row | ✅ |
| Internal troubleshooting стал practical, а не API-only | ✅ |
| Customer и operator surface разделены | ✅ |
| Внутренние поля не утекли в обычный customer UI | ✅ |

**Итог:** Operator UI — **IMPLEMENTED**.
