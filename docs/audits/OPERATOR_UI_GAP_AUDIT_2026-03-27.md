# Operator UI Gap Audit

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** Gap audit завершён

---

## 1. Как оператор использует endpoint сейчас

После реализации BLOCK C (2026-03-27) у оператора есть:
```
GET /api/billing/operator/usage-detail/{snapshot_id}
X-Operator-Secret: <secret>
```

**Проблема:** нет UI. Использование возможно только через:
1. `curl` прямо с VPS
2. Postman / HTTPie с ручным вводом snapshot_id
3. Прямой SQL для получения snapshot_id

**Это непрактично для daily support.** Оператор тратит 3–5 минут на получение одного snapshot_id и формирование запроса.

---

## 2. Откуда берётся snapshot_id в реальном workflow

`snapshot_id` = поле `id` в каждой строке `/api/billing/usage-logs`.

В Usage.tsx (customer UI) это поле **уже есть** в каждом объекте `UsageLog`:
```typescript
interface UsageLog {
    id: string   // ← это и есть snapshot_id
    ...
}
```

Но кнопки для инспекции нет — `id` используется только как React key.

**Минимальное решение:** добавить кнопку в каждую строку таблицы Usage.tsx, которая вызывает operator endpoint и показывает модальное окно.

---

## 3. Что нужно для быстрого инспекта дебета

| Потребность | Решение |
|---|---|
| Открыть конкретную строку | Кнопка в таблице |
| Получить operator detail | Modal с fetch к `/operator/usage-detail/{id}` |
| Auth без отдельного логина | `X-Operator-Secret` из `localStorage` (вводится через `prompt()` один раз) |
| Видеть внутренние поля | В модале: provider, raw_cost, billing_unit, formula, verdict |
| Не показывать клиенту | Модал закрыт для клиента (без секрета — 403) |

---

## 4. Что безопасно для оператора, но не для клиента

| Поле | В customer UI | В operator modal |
|---|---|---|
| `provider` | ❌ | ✅ |
| `raw_provider_cost_usd` | ❌ | ✅ |
| `litellm_spend_log_id` | ❌ | ✅ |
| `billing_unit` | ❌ | ✅ |
| `tariff.input_rate_credits` | ✅ только в /tariffs | ✅ в контексте строки |
| `calculated_expected_credits` | ❌ | ✅ |
| `formula_note` | ❌ | ✅ |
| `operator_verdict` | ❌ | ✅ |
| `ledger_entry` | ❌ | ✅ |
| `api_key_hash` (full) | prefix only | ✅ full |

**Защита:** без `OPERATOR_SECRET` backend возвращает 403. Клиент без секрета не получит данные даже если найдёт endpoint в коде.

---

## Итог

Minimal viable operator UI = кнопка в таблице Usage + модальное окно с operator detail. Отдельная страница/роут не нужны. Auth через localStorage secret — достаточно для internal tool.
