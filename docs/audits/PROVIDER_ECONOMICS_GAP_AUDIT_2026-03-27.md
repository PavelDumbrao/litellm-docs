# Provider Economics Gap Audit

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** Gap audit завершён

---

## 1. Цель аудита

Нужно собрать **внутренний economics layer** для оператора:

- видеть retail по модели,
- видеть upstream provider cost,
- считать proxy-margin по модели и категории,
- не менять customer UI,
- не менять каталог моделей,
- не менять billing logic.

---

## 2. Что уже есть в live state

### Авторитетные runtime-источники

1. **`billing.public_model_tariff`**  
   Контролирует активные customer-facing тарифы: `billing_unit`, `input_rate_credits`, `output_rate_credits`, `is_active`.

2. **`/opt/billing-portal/.env`**  
   Контролирует runtime conversion constant:
   - `FIXED_RUB_PER_CREDIT=85.0`

3. **`/docker/litellm-xne6/config.yaml`**  
   Контролирует runtime routing и upstream provider costs:
   - `model_name`
   - `litellm_params.api_base`
   - `order`
   - `model_info.input_cost_per_token`
   - `model_info.output_cost_per_token`

4. **`docs/current/SPECIAL_UNIT_BILLING_DESIGN.md`**  
   Уже фиксирует, что special-unit billing paths (`audio_token`, `search_token`, `realtime_token`, `research_token`, `chars_token`) не являются fully exact economics truth и в части кейсов являются proxy / approximation.

---

## 3. Главные найденные gaps

### GAP 1 — нет единого internal economics view

Сейчас retail и provider cost живут в разных местах:

- retail → `billing.public_model_tariff`
- runtime conversion → `/opt/billing-portal/.env`
- provider cost → `/docker/litellm-xne6/config.yaml`

Оператору или следующему агенту приходится собирать economics вручную.

---

### GAP 2 — `LIVE_PRICING_REFERENCE.md` нельзя использовать как единственный источник economics

Для internal economics `LIVE_PRICING_REFERENCE.md` больше не является достаточным источником, потому что:

- он не учитывает runtime `FIXED_RUB_PER_CREDIT=85.0` как главный billing conversion constant;
- он не отражает все текущие live primary paths из `config.yaml`;
- он даёт значения, которые расходятся с фактическим `tariff × 85 RUB / 90 FX` proxy-view.

**Пример конфликта:**

| Модель | `LIVE_PRICING_REFERENCE.md` | Live tariff + `FIXED_RUB_PER_CREDIT=85` + FX90 proxy |
|---|---:|---:|
| `claude-haiku-4-5` input/output | `$0.22 / $1.10` | `$1.596 / $7.999` |
| `claude-sonnet-4-6` input/output | `$0.66 / $3.29` | `$5.997 / $29.996` |

**Вывод:** для customer pricing truth нужно доверять live DB + runtime constants, а не старому reference snapshot.

---

### GAP 3 — special-unit economics нельзя маркировать как Exact

Следующие активные public models используют special billing units:

- `audio_token`
- `search_token`
- `realtime_token`
- `research_token`

Для них можно посчитать **proxy-margin**, но нельзя честно назвать его fully exact, потому что:

- runtime billing path уже задокументирован как approximation,
- часть unit-метрик path-dependent,
- special-unit cost exposure и customer charge не всегда 1:1 с реальным upstream usage primitive.

**Следствие:** эти модели должны попадать в статус **Estimated**, а не Exact.

---

### GAP 4 — есть incomplete coverage на публичной поверхности

По live reconciliation получаем **4 incomplete модели**:

1. `gpt-4.1`  
   Активный тариф есть, но public alias отсутствует в live `config.yaml` model paths.

2. `i7dc-claude-haiku-4-5`
3. `i7dc-claude-sonnet-4-6`
4. `i7dc-claude-opus-4-6`

Для трёх I7DC моделей есть provider cost path в `config.yaml`, но **нет активных строк в `billing.public_model_tariff`**, значит retail side incomplete.

---

### GAP 5 — нет category-level rollup

До этой задачи не существовало внутреннего отчёта вида:

- margin по категориям,
- breakdown по confidence,
- список anomalies,
- список incomplete моделей,
- internal-only summary для оператора/владельца.

---

## 4. Что доступно уже сейчас и чего не хватает

| Блок данных | Есть? | Комментарий |
|---|---|---|
| Активные customer тарифы | ✅ | Из `billing.public_model_tariff` |
| Runtime RUB-per-credit | ✅ | Из `/opt/billing-portal/.env` |
| Upstream provider costs | ✅ | Из live `config.yaml` |
| Routing priority / primary path | ✅ | Из `order` в `config.yaml` |
| Special-unit caveat | ✅ | Уже задокументирован |
| Internal economics matrix | ❌ | Нужно добавить |
| Confidence classification для всех public моделей | ❌ | Нужно добавить |
| Category rollup | ❌ | Нужно добавить |
| Single internal economics report | ❌ | Нужно добавить |

---

## 5. Итоговое live состояние после аудита

### Confidence split

- **Exact:** 29 моделей
- **Estimated:** 11 моделей
- **Incomplete:** 4 модели

### Incomplete models

- `gpt-4.1`
- `i7dc-claude-haiku-4-5`
- `i7dc-claude-sonnet-4-6`
- `i7dc-claude-opus-4-6`

### Special-unit models (Estimated)

- `gpt-4o-audio-preview`
- `gpt-audio`
- `gpt-audio-mini`
- `gpt-4o-mini-realtime-preview`
- `gpt-4o-realtime-preview`
- `gpt-4o-mini-search-preview`
- `gpt-4o-search-preview`
- `gpt-5-search-api`
- `o4-mini-deep-research`
- `gpt-4o-mini-transcribe`
- `gpt-4o-transcribe`

---

## 6. Решение для BLOCK C

Для этой итерации безопаснее и точнее сделать **internal report**, а не runtime endpoint, потому что:

1. задача явно допускает **endpoint _или_ report**;
2. report не меняет customer surface;
3. report не требует прокидывать billing-portal runtime к host path `/docker/litellm-xne6/config.yaml`;
4. report даёт нужный economics view уже сейчас и без риска для продового API.

---

## 7. Выходные артефакты после этого аудита

После gap audit должны появиться:

1. `docs/current/PROVIDER_ECONOMICS_SOURCE_MAP.md`
2. `docs/current/PROVIDER_ECONOMICS_REPORT.md`
3. `docs/current/PROVIDER_ECONOMICS_CONFIDENCE_MATRIX.md`
4. `docs/audits/PROVIDER_ECONOMICS_IMPLEMENTATION_2026-03-27.md`

---

## Финальный вывод

**Gap подтверждён:** все исходные live-данные для internal provider economics уже существуют, но они разорваны между DB, `.env` и `config.yaml`, а existing reference docs недостаточны для принятия economics-решений.

Нужен отдельный internal economics layer в виде:

- source map,
- confidence matrix,
- margin report,
- implementation report.
