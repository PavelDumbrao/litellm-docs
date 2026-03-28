# Economics Pricing Boundary

**Дата:** 2026-03-28  
**Область:** Internal operator rule — обязателен для всей economics работы  
**Статус:** Canonical

---

## 1. Retail Truth — единственный источник customer billing

**Источник:** `billing.public_model_tariff` в PostgreSQL  
**Поля:** `input_rate_credits`, `output_rate_credits`, `billing_unit`, `is_active`

```sql
SELECT public_model_name, input_rate_credits, output_rate_credits
FROM billing.public_model_tariff
WHERE is_active = true;
```

**Правило:** Именно эти значения используются для списания с клиента. Никакой другой источник не может определять customer billing.

---

## 2. Provider Cost Basis — только для внутреннего расчёта margin

**Источники (в порядке приоритета):**
1. Прямой прайс провайдера (reseller invoice, API pricing page) — Exact
2. Официальный OpenAI/Anthropic/Google pricing — Estimated (если совпадает с нашим reseller path)
3. Proxy economics через LiteLLM config cost_per_token — Estimated
4. Отсутствие данных — Incomplete

**Правило:** Provider cost используется только для:
- расчёта gross margin (retail − cost)
- risk analysis (margin threshold alerts)
- incomplete economics remediation (заполнение пробелов в matrix)

**Строгое ограничение:** Provider cost НЕ является и НЕ становится customer price.

---

## 3. Что запрещено

| Запрещённое действие | Причина |
|---|---|
| Перезапись `input_rate_credits` из официального прайса OpenAI/Anthropic | Официальный прайс ≠ наша retail цена для клиента |
| Использование provider cost как retail | Смешивание уровней ломает billing truth |
| Автоматическое обновление тарифов из внешних источников | Только ручной процесс с аудитом |
| Считать официальный OpenAI pricing нашим provider cost если reseller другой | Reseller margin может существенно отличаться |

---

## 4. Как вычисляется margin

```
retail_input_usd_per_1m = input_rate_credits × 1_000_000 × FIXED_RUB_PER_CREDIT ÷ FX_RUB_PER_USD
retail_output_usd_per_1m = output_rate_credits × 1_000_000 × FIXED_RUB_PER_CREDIT ÷ FX_RUB_PER_USD

input_margin_pct = (retail_input − provider_input_cost) ÷ retail_input × 100
output_margin_pct = (retail_output − provider_output_cost) ÷ retail_output × 100
```

**Константы (snapshot 2026-03-27):**
- `FIXED_RUB_PER_CREDIT = 85.0`
- `FX_RUB_PER_USD = 90.0` (proxy)

**Важно:** margin — это вычисленная величина, не хранимая. Она обновляется только при:
1. Изменении retail tariff в `billing.public_model_tariff`
2. Изменении provider cost (обновление economics matrix)
3. Изменении `FIXED_RUB_PER_CREDIT` или FX proxy

---

## 5. Почему официальный прайс провайдера не может перезаписывать customer billing

1. **Разные уровни ценообразования.** Мы покупаем через resellers (ANIDEAAI, POLO, JENIYA, I7DC), у которых собственные цены. Официальный OpenAI $2.00/1M input ≠ реальная наша себестоимость через reseller.

2. **Retail — это наше бизнес-решение.** Мы выставляем markup исходя из: операционных расходов, FX risk buffer, loyalty программы, конкурентной среды. Ни один из этих факторов не отражён в официальном прайсе.

3. **Billing truth нельзя изменять автоматически.** Любое изменение `billing.public_model_tariff` должно проходить через явный operator action с аудитом и коммитом.

4. **Inconsistency-only exception.** Если обнаружена реальная ошибка (retail rate меньше provider cost при подтверждённом provider path), это единственный случай для пересмотра retail — и только после явного операторского решения.

---

## 6. Применение в economics работе

| Задача | Источник данных | Запрет |
|---|---|---|
| Списание с клиента | `billing.public_model_tariff` | Использовать provider cost |
| Расчёт margin | retail из tariff − provider cost | Менять tariff для выравнивания margin |
| Remediation Incomplete | Найти provider cost, НЕ менять retail | Автовставка из official pricing |
| Alert threshold | margin на основе текущего retail | Перезаписать retail при low margin alert |
| Snapshot audit | retail + cost, оба источника явно | Смешивать в одной строке без разделения |

---

## 7. Ответственность

- **retail tariff** изменяет: только оператор, только вручную, только с явным обоснованием
- **provider cost в economics matrix** изменяет: оператор на основе актуального prайса reseller
- **margin alerts** генерирует: автоматически через `/operator/margin-alerts`
- **Customer** видит: только charged_credits из `billing.usage_billing_snapshot`, не видит margin, provider_cost, economics data
