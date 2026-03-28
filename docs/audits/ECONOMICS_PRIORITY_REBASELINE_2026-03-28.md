# Economics Priority Rebaseline

**Дата:** 2026-03-28  
**Контекст:** После первоначального HIGH alerts разбора выявлено, что i7dc-* модели находятся в стадии тестирования и не являются частью production public surface. Требуется ребейзлайн приоритетов без удаления i7dc из economics layer.

---

## 1. Исходные HIGH alerts (до ребейзлайна)

| Модель | Alert class | Severity | Статус |
|---|---|---|---|
| `gpt-4.1` | INCOMPLETE_ECONOMICS | HIGH | Production |
| `i7dc-claude-haiku-4-5` | INCOMPLETE_ECONOMICS | HIGH | Test-only |
| `i7dc-claude-opus-4-6` | INCOMPLETE_ECONOMICS | HIGH | Test-only |
| `i7dc-claude-sonnet-4-6` | INCOMPLETE_ECONOMICS | HIGH | Test-only |

---

## 2. Переклассификация: I7DC как test-only

**Основание:**
- i7dc-claude-* модели не входят в production public surface
- Не участвуют в customer billing (нет retail entry в `billing.public_model_tariff`)
- Находятся в стадии тестирования — выводы по ним не влияют на боевые бизнес-решения
- Включение их в HIGH-priority remediation отвлекает внимание от реальных production gaps

**Действие:**
- i7dc-* модели помечены как `scope: test-only` в economics layer
- Alert severity для test-only моделей снижена: `INCOMPLETE_ECONOMICS → TEST_ONLY_INCOMPLETE (LOW)`
- i7dc-* исключены из immediate margin remediation priority
- i7dc-* НЕ удалены из economics matrix — сохранены для будущего при переходе в production

---

## 3. Исключённые кейсы (non-production/test-only)

| Модель | Причина исключения | Статус в economics |
|---|---|---|
| `i7dc-claude-haiku-4-5` | test-only, нет retail entry, не в production surface | Остаётся в matrix, severity → LOW |
| `i7dc-claude-opus-4-6` | test-only, нет retail entry, не в production surface | Остаётся в matrix, severity → LOW |
| `i7dc-claude-sonnet-4-6` | test-only, нет retail entry, не в production surface | Остаётся в matrix, severity → LOW |

---

## 4. Production economics priority после ребейзлайна

### Blocking (требует действия)

| Приоритет | Модель | Тип gap | Action |
|---|---|---|---|
| P0 | `gpt-4.1` | INCOMPLETE_ECONOMICS — нет reseller path | Определить reseller, обновить matrix до Estimated |

### Active monitoring (не blocking)

| Приоритет | Модель/Категория | Тип | Action |
|---|---|---|---|
| P1 | 18 моделей LOW_MARGIN_WARNING | margin 30–50% | Мониторить, пересмотреть при provider cost изменении |
| P2 | Audio/Speech, Realtime, Search, Transcription | ESTIMATED_ONLY_CATEGORY | При наличии real provider cost → upgrade to Exact |

### Non-production (мониторинг без приоритета)

| Модели | Статус | Когда возвращать в приоритет |
|---|---|---|
| `i7dc-claude-*` (3 модели) | test-only | При переходе в production public surface |

---

## 5. Финальный фокус следующего шага

**Единственный production-relevant incomplete case:**

`gpt-4.1` — retail tariff существует (`0.00000424`/`0.00001694` credits, notes: `$2.00/$8 × 2x markup`). Gap: нет подтверждённого reseller path (POLO? ANIDEAAI? прямой OpenAI?).

**Следующий шаг:**
1. Проверить LiteLLM config — через какой `api_base` идёт gpt-4.1 трафик
2. Если reseller path найден → обновить economics matrix с `confidence = Estimated` + real provider cost
3. HIGH alert для gpt-4.1 закроется после обновления matrix

**i7dc-* next step (не срочно):**
- При решении о production launch i7dc моделей: запросить прайс → создать retail tariff entries → обновить matrix
- До launch: TEST_ONLY_INCOMPLETE alerts остаются активными как reminder

---

## 6. Изменения в alert engine

- i7dc-* модели теперь генерируют `TEST_ONLY_INCOMPLETE` с severity `LOW` вместо `HIGH INCOMPLETE_ECONOMICS`
- `has_blocking` в summary рассчитывается без test-only моделей
- Retail pricing не изменялась
- Economics matrix не удалялась — только scope переклассифицирован
