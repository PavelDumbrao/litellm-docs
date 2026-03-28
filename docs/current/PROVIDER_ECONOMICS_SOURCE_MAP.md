# Provider Economics Source Map

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Назначение:** Источник истины для internal economics view. Не для customer surface.

---

## 1. Главные источники данных

| Источник | Авторитетен для | Не авторитетен для | Где лежит |
|---|---|---|---|
| `billing.public_model_tariff` | Активный retail tariff: `billing_unit`, `input_rate_credits`, `output_rate_credits`, `is_active` | Runtime provider cost | PostgreSQL / schema `billing` |
| `/opt/billing-portal/.env` | Runtime conversion constant `FIXED_RUB_PER_CREDIT=85.0` | Provider routing / provider cost | VPS |
| `/docker/litellm-xne6/config.yaml` | Public alias → provider paths, `api_base`, `order`, `input_cost_per_token`, `output_cost_per_token` | Customer tariff truth | VPS |
| `LIVE_PUBLIC_MODEL_CATALOG.md` | Public surface inventory | Retail price / live upstream cost | `docs/current/` |
| `SPECIAL_UNIT_BILLING_DESIGN.md` | Caveat для proxy/special billing units | Token-model exact economics | `docs/current/` |
| `LIVE_PRICING_REFERENCE.md` | Исторический/derived reference | Нельзя использовать как единственный live economics truth | `docs/current/` |

---

## 2. Что контролирует каждый слой

### A. `billing.public_model_tariff`

Использовать для ответа на вопросы:

- Модель вообще активна?
- Какой у неё `billing_unit`?
- Какая customer-facing ставка в credits?

Ключевые поля:

| Поле | Значение |
|---|---|
| `public_model_name` | public alias |
| `billing_unit` | `token` / `audio_token` / `search_token` / `realtime_token` / `research_token` / `chars_token` |
| `input_rate_credits` | retail credits за input unit |
| `output_rate_credits` | retail credits за output unit |
| `is_active` | признак активной customer модели |

---

### B. `/opt/billing-portal/.env`

Использовать для runtime conversion constants.

Live на момент аудита:

```env
FIXED_RUB_PER_CREDIT=85.0
LOYALTY_THRESHOLD_RUB=50000
```

Для economics view **важен только** `FIXED_RUB_PER_CREDIT`.

---

### C. `/docker/litellm-xne6/config.yaml`

Использовать для ответа на вопросы:

- Через какого upstream provider идёт primary path?
- Есть ли fallback path?
- Какой текущий provider cost на вход/выход?

Ключевые поля:

| Поле | Значение |
|---|---|
| `model_name` | public alias |
| `litellm_params.api_base` | upstream/provider base |
| `litellm_params.order` | routing priority |
| `model_info.input_cost_per_token` | upstream input cost per token |
| `model_info.output_cost_per_token` | upstream output cost per token |

---

## 3. Правила расчёта economics view

### Runtime retail proxy (RUB)

```text
retail_rub_per_1m = rate_credits * 1_000_000 * FIXED_RUB_PER_CREDIT
```

Где:

- `rate_credits` = `input_rate_credits` или `output_rate_credits`
- `FIXED_RUB_PER_CREDIT = 85.0`

### Analytical retail proxy (USD)

Для сопоставления с provider cost используется **FX90 proxy**, потому что именно 90 RUB/USD используется в существующих pricing references.

```text
retail_usd_per_1m_fx90 = retail_rub_per_1m / 90
```

**Важно:** FX90 — это **аналитическая нормализация**, а не runtime billing constant.

### Provider cost (USD)

```text
provider_cost_usd_per_1m = cost_per_token * 1_000_000
```

### Proxy-margin

```text
margin_pct = ((retail_usd_per_1m_fx90 - provider_cost_usd_per_1m) / retail_usd_per_1m_fx90) * 100
```

---

## 4. Как выбирается primary provider path

Для economics view берётся **primary runtime path**:

1. если в `config.yaml` есть `order`, берётся путь с минимальным `order`;
2. если `order` отсутствует, берётся первый path в live конфиге;
3. fallback paths сохраняются как secondary context, но margin считается по primary path.

---

## 5. Confidence rules

### Exact

Модель получает статус **Exact**, если одновременно выполнено:

1. есть активная строка в `billing.public_model_tariff`;
2. найден live provider path в `config.yaml`;
3. `billing_unit = token`.

### Estimated

Модель получает статус **Estimated**, если:

1. активный retail tariff есть;
2. provider path найден;
3. `billing_unit != token`.

То есть economics view можно посчитать, но это special/proxy-billed cluster.

### Incomplete

Модель получает статус **Incomplete**, если:

1. активный retail tariff есть, а provider path не найден; **или**
2. provider path есть, но активной tariff строки нет.

---

## 6. Что нельзя делать

### Нельзя считать economics только по `LIVE_PRICING_REFERENCE.md`

Потому что он не является главным runtime truth при конфликте с:

- `billing.public_model_tariff`
- `FIXED_RUB_PER_CREDIT`
- `config.yaml`

### Нельзя маркировать special-unit модели как Exact

Для:

- `audio_token`
- `search_token`
- `realtime_token`
- `research_token`

нужно оставлять статус **Estimated**.

---

## 7. Decision tree для следующих агентов

```text
Нужен retail?
    -> billing.public_model_tariff

Нужно перевести credits в RUB?
    -> /opt/billing-portal/.env -> FIXED_RUB_PER_CREDIT

Нужен upstream provider cost?
    -> /docker/litellm-xne6/config.yaml

Нужен exact/estimated/incomplete verdict?
    -> billing_unit + наличие provider path + наличие active tariff

Док конфликтует с DB/config/env?
    -> Док неверен, доверять live источникам
```

---

## Финальный вывод

**Единственный надёжный economics stack:**

1. `billing.public_model_tariff`
2. `/opt/billing-portal/.env`
3. `/docker/litellm-xne6/config.yaml`

Все остальные docs — только derived helpers и snapshots.
