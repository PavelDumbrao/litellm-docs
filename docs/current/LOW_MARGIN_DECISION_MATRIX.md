# LOW_MARGIN Decision Matrix

**Дата:** 2026-03-28  
**Назначение:** слой решений для LOW_MARGIN production surface без auto-repricing retail.

---

## 1) Правила принятия решений

| Условие | Решение | Класс действия |
|---|---|---|
| Exact + lowest margin < 49% | `provider_path_review` | P1 targeted remediation (cost/routing), retail не трогаем |
| Exact + lowest margin 49–50% | `monitor_only` | P2 мониторинг следующего snapshot |
| Estimated + LOW warning | `monitor_only` | P2 мониторинг + сбор точной себестоимости |
| Estimated-only category | `category_monitoring` | P2 категорийный мониторинг, upgrade до Exact при наличии данных |
| Test-only incomplete | `defer_test_scope` | Вне production remediation scope |

Boundary rule: `billing.public_model_tariff` не модифицируется этой матрицей.

---

## 2) Матрица по моделям (LOW_MARGIN_WARNING = 18)

| Модель | Категория | Confidence | Lowest margin % | Провайдер | Решение | Приоритет | Обоснование |
|---|---|---|---:|---|---|---|---|
| `gpt-5.4-nano` | General Chat | Exact | 47.06 | JENIYA | provider_path_review | P1 | Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail. |
| `gemini-3-flash-preview-nothinking` | Gemini | Exact | 48.57 | POLO | provider_path_review | P1 | Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail. |
| `gemini-3-flash-preview-thinking` | Gemini | Exact | 48.57 | POLO | provider_path_review | P1 | Exact-маржа ниже 49%; кандидат на cost/routing review без изменения retail. |
| `gpt-4o-mini-search-preview` | Search/Research | Estimated | 48.82 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-4o-mini-transcribe` | Transcription | Estimated | 49.61 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-4o-mini-realtime-preview` | Realtime | Estimated | 49.81 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-5.4-mini` | General Chat | Exact | 49.85 | JENIYA | monitor_only | P2 | Exact-маржа в зоне 49-50%; достаточно мониторинга. |
| `gpt-4o-realtime-preview` | Realtime | Estimated | 49.89 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-audio` | Audio/Speech | Estimated | 49.89 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gemini-3.1-pro-preview` | Gemini | Exact | 49.98 | POLO | monitor_only | P2 | Exact-маржа в зоне 49-50%; достаточно мониторинга. |
| `gemini-3.1-pro-preview-high` | Gemini | Exact | 49.98 | POLO | monitor_only | P2 | Exact-маржа в зоне 49-50%; достаточно мониторинга. |
| `gemini-3.1-pro-preview-low` | Gemini | Exact | 49.98 | POLO | monitor_only | P2 | Exact-маржа в зоне 49-50%; достаточно мониторинга. |
| `gemini-3.1-pro-preview-medium` | Gemini | Exact | 49.98 | POLO | monitor_only | P2 | Exact-маржа в зоне 49-50%; достаточно мониторинга. |
| `gpt-4o-audio-preview` | Audio/Speech | Estimated | 49.98 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-4o-search-preview` | Search/Research | Estimated | 49.98 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-4o-transcribe` | Transcription | Estimated | 49.98 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `gpt-5-search-api` | Search/Research | Estimated | 49.98 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |
| `o4-mini-deep-research` | Search/Research | Estimated | 49.98 | POLO | monitor_only | P2 | Estimated-покрытие; нужна верификация точной себестоимости провайдера. |

---

## 3) Матрица по категориям (ESTIMATED_ONLY_CATEGORY = 4)

| Категория | Решение | Приоритет | Follow-up |
|---|---|---|---|
| Audio/Speech | category_monitoring | P2 | Получить exact provider cost basis и перевести категорию из Estimated в Exact. |
| Realtime | category_monitoring | P2 | Получить exact provider cost basis и перевести категорию из Estimated в Exact. |
| Search/Research | category_monitoring | P2 | Получить exact provider cost basis и перевести категорию из Estimated в Exact. |
| Transcription | category_monitoring | P2 | Получить exact provider cost basis и перевести категорию из Estimated в Exact. |

---

## 4) P1-кандидаты для optional BLOCK C

- `gpt-5.4-nano` — lowest margin 47.06%, provider `JENIYA`, provider_paths_count=2
- `gemini-3-flash-preview-nothinking` — lowest margin 48.57%, provider `POLO`, provider_paths_count=2
- `gemini-3-flash-preview-thinking` — lowest margin 48.57%, provider `POLO`, provider_paths_count=2

Правило исполнения BLOCK C:
- Только cost/routing изменения при доказуемой безопасности.
- Обязательные smoke-check после каждого runtime/config изменения.
- Retail pricing не менять.

---

## 5) Non-goals

- No automatic retail repricing.
- No test-only promotion в production scope.
- No broad docs cleanup вне этого governance pass.

