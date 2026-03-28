# Margin Alert Policy

**Дата:** 2026-03-28  
**Область:** Internal operator monitoring — не customer-facing  
**Применяется к:** `/api/billing/operator/margin-alerts`

---

## Общие принципы

1. Alerts оцениваются по snapshot economics data (тот же источник что `operator/economics-view`)
2. Alerts видны только оператору (требуют `X-Operator-Secret`)
3. Blocking alerts означают: модель несёт известный финансовый риск прямо сейчас
4. Informational alerts означают: модель требует внимания, но не обязательно немедленного действия
5. Alerts не блокируют API-запросы клиентов — только информируют оператора
6. Пороги пересматриваются при изменении `FIXED_RUB_PER_CREDIT` или FX proxy

---

## Alert Classes

---

### NEGATIVE_MARGIN

**Severity:** `CRITICAL` (blocking)  
**Условие:** `input_margin_pct < 0` ИЛИ `output_margin_pct < 0`  
**Confidence scope:** Exact, Estimated  
**Описание:** Модель продаётся ниже себестоимости провайдера.  

**Operator action:**
1. Немедленно проверить retail tariff (`billing.public_model_tariff`) vs provider cost
2. Если подтверждён — скорректировать retail rate или деактивировать модель до исправления
3. Если margin отрицательный только по output (при положительном input) — проверить token ratio реальных запросов
4. Документировать решение в audit trail

**Exposes to customer:** Нет. API модели остаётся доступным до явного action оператора.

---

### LOW_MARGIN_CRITICAL

**Severity:** `HIGH` (blocking)  
**Условие:** `0 <= input_margin_pct < 30` ИЛИ `0 <= output_margin_pct < 30`  
**Confidence scope:** Exact  
**Описание:** Очень низкий запас прочности. Любое FX движение >10% или ценовое изменение провайдера может перевести в отрицательный margin.

**Operator action:**
1. Сравнить с предыдущим snapshot (если есть)
2. Оценить реальный token mix по usage-logs (input-heavy vs output-heavy)
3. Рассмотреть увеличение retail rate
4. Поставить напоминание на следующую ревизию

---

### LOW_MARGIN_WARNING

**Severity:** `MEDIUM` (informational)  
**Условие:** `30 <= input_margin_pct < 50` ИЛИ `30 <= output_margin_pct < 50`  
**Confidence scope:** Exact, Estimated  
**Описание:** Ниже целевого 50% операционного буфера.

**Operator action:**
1. Мониторить при следующем обновлении economics snapshot
2. Если Estimated — уточнить provider cost из официального прайса
3. Документировать если сознательное бизнес-решение (competitive pricing)

---

### INCOMPLETE_ECONOMICS

**Severity:** `HIGH` (blocking)  
**Условие:** `confidence == "Incomplete"`  
**Описание:** Отсутствуют данные для расчёта margin. Реальная экономика модели неизвестна.

**Operator action:**
1. Для `i7dc-*` моделей: запросить актуальный прайс у i7dc.com и внести в economics matrix
2. Для `gpt-4.1`: найти официальный OpenAI прайс и определить provider path
3. Если данные недоступны — рассмотреть деактивацию модели или явную markup политику
4. После заполнения — перевести модель в Estimated или Exact

---

### ESTIMATED_ONLY_CATEGORY

**Severity:** `LOW` (informational)  
**Условие:** Все модели в категории имеют `confidence == "Estimated"`  
**Описание:** Вся категория работает на proxy economics — отклонение реального margin возможно.

**Operator action:**
1. Отметить категорию в мониторинге
2. При доступности реальных provider costs — обновить до Exact
3. Рассмотреть более консервативный markup для Estimated категорий

**Affected categories (snapshot 2026-03-27):** Audio/Speech, Realtime, Search/Research, Transcription

---

### MISSING_COST_BASIS

**Severity:** `MEDIUM` (informational)  
**Условие:** `provider_input_cost_usd_per_1m == None` ИЛИ `provider_output_cost_usd_per_1m == None`  
**Confidence scope:** Exact, Estimated (не Incomplete — там это ожидаемо)  
**Описание:** Неполные данные о стоимости провайдера при наличии retail tiff.

**Operator action:**
1. Найти актуальный provider cost и дополнить economics matrix
2. До обновления — трактовать как Incomplete по риску

---

### PROVIDER_COST_DRIFT

**Severity:** `MEDIUM` (informational) — **Future implementation**  
**Условие:** Расхождение provider cost >10% между текущим и предыдущим snapshot  
**Описание:** Провайдер обновил цены — margin сместился.

**Operator action:**
1. Верифицировать новый прайс на сайте провайдера
2. Пересчитать retail rate если необходимо
3. Обновить economics matrix

*Реализация: требует хранение baseline snapshots — зарезервировано для следующего этапа.*

---

## Threshold matrix

```
margin%     <0%          0-30%          30-50%         ≥50%
Exact    → CRITICAL    → HIGH          → WARNING       → OK
Estimated→ CRITICAL    → HIGH          → WARNING       → OK
Incomplete→ INCOMPLETE_ECONOMICS (независимо от margin)
```

---

## Порядок review

1. Operator запрашивает `GET /api/billing/operator/margin-alerts`
2. Endpoint возвращает список alerts с severity, model, category, values, recommended_action
3. Operator разбирает CRITICAL + HIGH alerts в первую очередь
4. После исправления — обновить economics matrix в `billing.py` и пересмотреть snapshot
5. Фиксировать решения в audit trail (docs/audits/)

---

## Ограничения текущей реализации

- Snapshot статический (hardcoded matrix в `billing.py`) — не обновляется автоматически при изменении провайдерских цен
- `PROVIDER_COST_DRIFT` не реализован (нет baseline storage)
- Alerts не отправляются автоматически (email/Telegram) — только по запросу
- Alerts не блокируют customer API — только информируют оператора
