# Margin Alerts — Gap Audit

**Дата:** 2026-03-28  
**Автор:** internal operator review  
**Статус:** Gap identified → action required

---

## 1. Текущее состояние: что видно только вручную

Posle go-live `operator/economics-view` оператор может посмотреть margin picture, но:

| Проблема | Описание |
|---|---|
| Нет пороговых значений | Нет формального определения «нормального» margin — оператор гадает по строке таблицы |
| Нет агрегации рисков | Видно 44 строки таблицы, нет сводки «сколько моделей в опасной зоне» |
| Нет автоматического триггера | Margin может упасть незаметно после обновления провайдерских цен |
| Estimated-модели не выделены как риск | Оценочный margin не несёт confidence — но UI не предупреждает |
| Incomplete-модели не блокируют | 4 модели без margin данных просто показываются серым — нет explicit alert |
| PROVIDER_COST_DRIFT не отслеживается | Нет механизма сравнения текущих costs с baseline snapshot |

---

## 2. Операционно значимые пороги

### По margin %

| Уровень | Порог input | Порог output | Обоснование |
|---|---|---|---|
| NEGATIVE | < 0% | < 0% | Продаём дешевле себестоимости — блокирующий риск |
| CRITICAL | 0–30% | 0–30% | Крайне низкий запас — уязвим к любому FX сдвигу или ценовому изменению провайдера |
| WARNING | 30–50% | 30–50% | Ниже целевого уровня — требует мониторинга |
| OK | ≥ 50% | ≥ 50% | Нормальный операционный коридор |

*Обоснование 50% baseline: retail в кредитах пересчитывается через FIXED_RUB_PER_CREDIT + FX proxy. При FX волатильности ±10% и overhead costs нужен запас не менее 40-50%.*

### По confidence

| Состояние | Операционный смысл |
|---|---|
| Incomplete | Нет ни retail, ни provider cost — margin неизвестен. Риск неограничен. |
| Estimated | Margin вычислен приближённо через proxy economics. Может отклоняться на ±20%. |
| Exact | Токен-биллинг с подтверждёнными тарифами. Наиболее надёжно. |

---

## 3. Модели и категории в зоне риска (snapshot 2026-03-27)

### Incomplete — неизвестный риск (4 модели)

| Модель | Категория | Провайдер |
|---|---|---|
| `gpt-4.1` | General Chat | — (нет provider path) |
| `i7dc-claude-haiku-4-5` | I7DC Relay | i7dc.com |
| `i7dc-claude-opus-4-6` | I7DC Relay | i7dc.com |
| `i7dc-claude-sonnet-4-6` | I7DC Relay | i7dc.com |

**Риск:** margin неизвестен. Если i7dc ценообразование выше retail — торгуем в убыток.

### WARNING zone — margin 30–50% (выборка)

| Модель | Input margin | Output margin | Тип |
|---|---|---|---|
| `gpt-5.4-nano` | 47.06% | 49.58% | Exact |
| `gpt-5.4-mini` | 51.13% | **49.85%** | Exact |
| `gemini-3-flash-preview-*` | 48–50% | 50% | Exact |
| `gpt-5.3-codex` | 50.5% | 50.0% | Exact |
| `deepseek-v3.2` | **70.28%** | 89.05% | Exact |
| `gemini-2.5-flash` | 89.41% | **77.66%** | Exact |

### Estimated — proxy confidence (11 моделей)

Категории Audio/Speech, Realtime, Search/Research, Transcription — все Estimated.
Margin вычислен приближённо. При изменении провайдерской цены реальный margin может отклониться.

---

## 4. Что должно триггерить alerts

| Alert class | Когда триггерить | Тип |
|---|---|---|
| `NEGATIVE_MARGIN` | input или output margin < 0% | **Blocking** |
| `LOW_MARGIN_CRITICAL` | margin 0–30% | **Blocking** |
| `LOW_MARGIN_WARNING` | margin 30–50% | Informational |
| `INCOMPLETE_ECONOMICS` | confidence == Incomplete | **Blocking** |
| `ESTIMATED_ONLY_CATEGORY` | категория содержит только Estimated модели | Informational |
| `MISSING_COST_BASIS` | provider_input/output_cost == None при non-Incomplete | Informational |
| `PROVIDER_COST_DRIFT` | (future) cost отклонился >10% от baseline | Informational |

---

## 5. Gap summary

| Gap | Приоритет | Действие |
|---|---|---|
| Нет формальных threshold'ов | P0 | Определить в MARGIN_ALERT_POLICY.md |
| Нет автоматической оценки по snapshot | P0 | Реализовать `/operator/margin-alerts` endpoint |
| Incomplete модели не блокируются | P0 | Alert + operator action required |
| Estimated confidence не выделен как риск | P1 | Informational alert |
| PROVIDER_COST_DRIFT не отслеживается | P2 | Future: diff между snapshot'ами |

---

**Вывод:** текущая economics view даёт данные, но не даёт actionable signal. Margin monitoring gap требует немедленного закрытия через alert policy + minimal endpoint.
