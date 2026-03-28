# Provider Economics Implementation Report

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** ✅ Implemented as internal documentation/report layer

---

## 1. Что было сделано

### BLOCK A

Создан audit-файл:

- `docs/audits/PROVIDER_ECONOMICS_GAP_AUDIT_2026-03-27.md`

В нём зафиксировано:

- какие live sources already exist,
- почему старого pricing reference недостаточно,
- где именно incomplete coverage,
- почему special-unit cluster должен быть Estimated.

### BLOCK B

Создан source map:

- `docs/current/PROVIDER_ECONOMICS_SOURCE_MAP.md`

В нём описано:

- что authoritative,
- что derived,
- какие формулы применяются,
- как выбирать primary provider path,
- как присваивается confidence.

### BLOCK C

Вместо нового runtime endpoint добавлен **internal report**:

- `docs/current/PROVIDER_ECONOMICS_REPORT.md`

Это сознательный выбор, потому что задача допускала **endpoint или report**, а report:

1. не меняет runtime surface,
2. не требует читать host `config.yaml` из billing-portal runtime,
3. не добавляет новый auth layer,
4. сразу даёт usable economics view по модели и категории.

### BLOCK D

Создан полный confidence matrix:

- `docs/current/PROVIDER_ECONOMICS_CONFIDENCE_MATRIX.md`

Он содержит:

- все public models,
- grouped tables: Exact / Estimated / Incomplete,
- primary provider path,
- retail proxy,
- provider cost,
- proxy-margin.

---

## 2. Что НЕ менялось

В этой итерации **не менялось**:

- customer UI,
- public model catalog,
- billing logic,
- DB schema,
- FastAPI runtime endpoints,
- operator security surface.

То есть economics layer добавлен **как internal аналитический слой**, а не как новая продовая фича для клиентов.

---

## 3. Какие live sources использованы

### Runtime / authoritative

1. `billing.public_model_tariff`
2. `/opt/billing-portal/.env`
3. `/docker/litellm-xne6/config.yaml`

### Supporting docs

1. `LIVE_PUBLIC_MODEL_CATALOG.md`
2. `SPECIAL_UNIT_BILLING_DESIGN.md`
3. `CURRENT_SOURCE_OF_TRUTH.md`

---

## 4. Принятые правила расчёта

### Retail

```text
retail_rub_per_1m = rate_credits * 1_000_000 * 85
retail_usd_per_1m_fx90 = retail_rub_per_1m / 90
```

### Upstream

```text
provider_cost_usd_per_1m = cost_per_token * 1_000_000
```

### Margin

```text
primary_margin_pct = ((retail_usd_per_1m_fx90 - primary_provider_cost_usd_per_1m) / retail_usd_per_1m_fx90) * 100
```

### Primary path selection

1. minimal `order`
2. если `order` нет — первый live path в config

---

## 5. Финальный результат

### Confidence split

| Status | Models |
|---|---:|
| Exact | 29 |
| Estimated | 11 |
| Incomplete | 4 |

### Incomplete models

- `gpt-4.1`
- `i7dc-claude-haiku-4-5`
- `i7dc-claude-sonnet-4-6`
- `i7dc-claude-opus-4-6`

### Category highlights

| Category | Main observation |
|---|---|
| Claude | Самый высокий exact-margin cluster (`~96.5%`) |
| Gemini | Смешанный exact cluster (`~48.5%` до `~93%`) |
| General Chat | Неоднородный cluster: от `~47%` до `~89%+` |
| Audio/Search/Realtime/Transcription | Почти ровный `~50%`, но только Estimated |
| I7DC Relay | Incomplete retail coverage |

---

## 6. Почему это решение безопасное

### Безопасно для продукта

- customer-facing surface не расширился,
- новые internal secrets не понадобились,
- продовая логика списаний не менялась,
- экономика стала наблюдаемой без вмешательства в runtime billing.

### Безопасно для дальнейших итераций

Теперь можно отдельно принимать решения:

1. чинить `gpt-4.1` coverage;
2. чинить I7DC retail rows;
3. при необходимости добавлять internal endpoint уже поверх готовой source map и confidence matrix.

---

## 7. Что можно делать следующим шагом

Если понадобится именно runtime-интерфейс, а не только docs/report, следующий шаг может быть:

1. добавить **internal-only** read-only endpoint;
2. защитить его тем же operator pattern, что и troubleshooting layer;
3. отдавать уже готовую economics matrix как JSON snapshot.

Но это **следующая** задача. Для текущего объёма BLOCK C закрыт report-форматом.

---

## Финальный вывод

**Provider economics layer реализован как internal documentation/report layer.**  
Все 5 блоков закрыты без изменения public/customer behavior.
