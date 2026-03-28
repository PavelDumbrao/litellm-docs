# Provider Economics Confidence Matrix

**Дата:** 2026-03-27  
**Назначение:** Полная классификация публичных моделей по economics confidence.

---

## 1. Правила чтения

### Confidence

- **Exact** — есть active tariff, есть live provider path, `billing_unit=token`
- **Estimated** — есть active tariff и provider path, но `billing_unit!=token`
- **Incomplete** — отсутствует active tariff или provider path

### Сокращения provider

- `ANIDEAAI` = `https://anideaai.com/v1`
- `POLO` = `https://poloai.top/v1`
- `JENIYA` = `https://jeniya.top/v1`
- `I7DC` = `https://i7dc.com/api`

### Колонки

- `retail in/out` — analytical proxy USD/1M через `FIXED_RUB_PER_CREDIT=85` и `FX90`
- `cost in/out` — upstream provider cost USD/1M по primary path
- `margin in/out` — proxy-margin по primary path

---

## 2. Exact (29)

| Model | Category | Unit | Primary | Retail in/out $1M | Cost in/out $1M | Margin in/out % |
|---|---|---|---|---:|---:|---:|
| `claude-haiku-4-5` | Claude | token | ANIDEAAI | `1.596 / 7.999` | `0.056 / 0.280` | `96.49 / 96.50` |
| `claude-haiku-4-5-thinking` | Claude | token | POLO | `1.596 / 7.999` | `0.110 / 0.548` | `93.11 / 93.15` |
| `claude-opus-4-5-thinking` | Claude | token | POLO | `29.996 / 149.997` | `0.548 / 2.740` | `98.17 / 98.17` |
| `claude-opus-4-6` | Claude | token | ANIDEAAI | `29.996 / 149.997` | `0.280 / 1.400` | `99.07 / 99.07` |
| `claude-opus-4-6-thinking` | Claude | token | JENIYA | `29.996 / 149.997` | `0.822 / 4.110` | `97.26 / 97.26` |
| `claude-sonnet-4-5-thinking` | Claude | token | POLO | `5.997 / 29.996` | `0.329 / 1.644` | `94.51 / 94.52` |
| `claude-sonnet-4-6` | Claude | token | ANIDEAAI | `5.997 / 29.996` | `0.170 / 0.840` | `97.17 / 97.20` |
| `text-embedding-3-large` | Embeddings | token | POLO | `0.264 / 0.000` | `0.027 / 0.027` | `89.79 / —` |
| `text-embedding-3-small` | Embeddings | token | POLO | `0.038 / 0.000` | `0.004 / 0.004` | `89.41 / —` |
| `text-embedding-ada-002` | Embeddings | token | POLO | `0.198 / 0.000` | `0.021 / 0.021` | `89.41 / —` |
| `gemini-2.5-flash` | Gemini | token | JENIYA | `0.302 / 1.199` | `0.032 / 0.268` | `89.41 / 77.66` |
| `gemini-2.5-flash-lite` | Gemini | token | POLO | `0.198 / 0.803` | `0.014 / 0.055` | `92.94 / 93.15` |
| `gemini-2.5-flash-thinking` | Gemini | token | POLO | `0.302 / 1.199` | `0.041 / 0.342` | `86.43 / 71.49` |
| `gemini-3-flash-preview` | Gemini | token | JENIYA | `0.132 / 0.822` | `0.053 / 0.321` | `59.92 / 60.93` |
| `gemini-3-flash-preview-nothinking` | Gemini | token | POLO | `0.132 / 0.822` | `0.068 / 0.411` | `48.57 / 49.98` |
| `gemini-3-flash-preview-thinking` | Gemini | token | POLO | `0.132 / 0.822` | `0.068 / 0.411` | `48.57 / 49.98` |
| `gemini-3.1-pro-preview` | Gemini | token | POLO | `0.548 / 3.287` | `0.274 / 1.644` | `49.98 / 49.98` |
| `gemini-3.1-pro-preview-high` | Gemini | token | POLO | `0.548 / 3.287` | `0.274 / 1.644` | `49.98 / 49.98` |
| `gemini-3.1-pro-preview-low` | Gemini | token | POLO | `0.548 / 3.287` | `0.274 / 1.644` | `49.98 / 49.98` |
| `gemini-3.1-pro-preview-medium` | Gemini | token | POLO | `0.548 / 3.287` | `0.274 / 1.644` | `49.98 / 49.98` |
| `gpt-4.1-mini` | General Chat | token | POLO | `0.803 / 3.192` | `0.082 / 0.329` | `89.79 / 89.69` |
| `gpt-4.1-nano` | General Chat | token | POLO | `0.198 / 0.803` | `0.021 / 0.082` | `89.41 / 89.79` |
| `gpt-4o` | General Chat | token | POLO | `4.996 / 20.003` | `0.514 / 2.055` | `89.71 / 89.73` |
| `gpt-4o-mini` | General Chat | token | POLO | `0.302 / 1.199` | `0.031 / 0.123` | `89.74 / 89.75` |
| `gpt-5.3-codex` | General Chat | token | JENIYA | `0.378 / 2.994` | `0.187 / 1.497` | `50.50 / 50.00` |
| `gpt-5.4` | General Chat | token | JENIYA | `1.029 / 8.217` | `0.267 / 1.604` | `74.06 / 80.48` |
| `gpt-5.4-mini` | General Chat | token | JENIYA | `0.123 / 0.718` | `0.060 / 0.360` | `51.13 / 49.85` |
| `gpt-5.4-nano` | General Chat | token | JENIYA | `0.038 / 0.397` | `0.020 / 0.200` | `47.06 / 49.58` |
| `deepseek-v3.2` | Other | token | JENIYA | `0.538 / 2.201` | `0.160 / 0.241` | `70.28 / 89.05` |

---

## 3. Estimated (11)

| Model | Category | Unit | Primary | Retail in/out $1M | Cost in/out $1M | Margin in/out % |
|---|---|---|---|---:|---:|---:|
| `gpt-4o-audio-preview` | Audio/Speech | audio_token | POLO | `1.029 / 4.108` | `0.514 / 2.055` | `50.07 / 49.98` |
| `gpt-audio` | Audio/Speech | audio_token | POLO | `1.029 / 2.049` | `0.514 / 1.027` | `50.07 / 49.89` |
| `gpt-audio-mini` | Audio/Speech | audio_token | POLO | `30.827 / 61.653` | `15.411 / 30.822` | `50.01 / 50.01` |
| `gpt-4o-mini-realtime-preview` | Realtime | realtime_token | POLO | `0.246 / 0.982` | `0.123 / 0.493` | `49.91 / 49.81` |
| `gpt-4o-realtime-preview` | Realtime | realtime_token | POLO | `2.049 / 8.217` | `1.027 / 4.110` | `49.89 / 49.98` |
| `gpt-4o-mini-search-preview` | Search/Research | search_token | POLO | `0.057 / 0.227` | `0.029 / 0.115` | `48.82 / 49.26` |
| `gpt-4o-search-preview` | Search/Research | search_token | POLO | `1.029 / 4.108` | `0.514 / 2.055` | `50.07 / 49.98` |
| `gpt-5-search-api` | Search/Research | search_token | POLO | `1.029 / 8.217` | `0.514 / 4.110` | `50.07 / 49.98` |
| `o4-mini-deep-research` | Search/Research | research_token | POLO | `0.822 / 3.287` | `0.411 / 1.644` | `49.98 / 49.98` |
| `gpt-4o-mini-transcribe` | Transcription | audio_token | POLO | `0.510 / 2.049` | `0.257 / 1.027` | `49.61 / 49.89` |
| `gpt-4o-transcribe` | Transcription | audio_token | POLO | `1.029 / 4.108` | `0.514 / 2.055` | `50.07 / 49.98` |

---

## 4. Incomplete (4)

| Model | Category | Unit | Что есть | Что отсутствует | Current note |
|---|---|---|---|---|---|
| `gpt-4.1` | General Chat | token | Active retail tariff | Нет public provider path в `config.yaml` | Retail есть, upstream path incomplete |
| `i7dc-claude-haiku-4-5` | I7DC Relay | — | Provider cost `0.150 / 0.750` через I7DC | Нет active tariff row | Public docs/model presence не закрыты retail-side |
| `i7dc-claude-sonnet-4-6` | I7DC Relay | — | Provider cost `0.450 / 2.250` через I7DC | Нет active tariff row | Public docs/model presence не закрыты retail-side |
| `i7dc-claude-opus-4-6` | I7DC Relay | — | Provider cost `0.750 / 3.750` через I7DC | Нет active tariff row | Public docs/model presence не закрыты retail-side |

---

## 5. Итог

| Confidence | Models |
|---|---:|
| Exact | 29 |
| Estimated | 11 |
| Incomplete | 4 |

Этот файл — основной internal reference для вопроса: **какие модели можно считать точно, какие только приблизительно, а какие пока incomplete.**
