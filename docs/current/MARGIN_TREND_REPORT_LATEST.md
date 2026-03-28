# Margin Trend Report (Latest)

**Generated at:** 2026-03-28T08:43:27.603390+00:00  
**Window:** `d71e587` -> `798a5e4`

## Summary

- `models_current`: **44**
- `models_previous`: **44**
- `low_margin_warning_current`: **18**
- `low_margin_warning_previous`: **18**
- `repeated_low_margin_models`: **18**
- `worsening_models`: **0**
- `improving_models`: **1**
- `stable_models`: **43**

## Category Trend

| Category | Warning<=Current | Warning<=Previous | Avg margin current | Avg margin previous | Trend | Reason |
|---|---:|---:|---:|---:|---|---|
| Audio/Speech | 2 | 2 | 49.96 | 49.96 | stable | no_material_change |
| Claude | 0 | 0 | 96.54 | 96.54 | stable | no_material_change |
| Embeddings | 0 | 0 | 89.54 | 89.54 | stable | no_material_change |
| Gemini | 6 | 6 | 59.91 | 59.91 | stable | no_material_change |
| General Chat | 2 | 2 | 69.95 | 72.44 | worsening | avg_margin_delta:-2.49 |
| I7DC Relay | 0 | 0 | None | None | stable | no_material_change |
| Other | 0 | 0 | 70.28 | 70.28 | stable | no_material_change |
| Realtime | 2 | 2 | 49.85 | 49.85 | stable | no_material_change |
| Search/Research | 4 | 4 | 49.69 | 49.69 | stable | no_material_change |
| Transcription | 2 | 2 | 49.8 | 49.8 | stable | no_material_change |

## Low-Margin Model Trend

| Model | Category | Confidence prev->curr | Lowest margin prev->curr | Band prev->curr | Trend |
|---|---|---|---|---|---|
| `gemini-3-flash-preview-nothinking` | Gemini | Exact -> Exact | 48.57 -> 48.57 | warning -> warning | stable |
| `gemini-3-flash-preview-thinking` | Gemini | Exact -> Exact | 48.57 -> 48.57 | warning -> warning | stable |
| `gemini-3.1-pro-preview` | Gemini | Exact -> Exact | 49.98 -> 49.98 | warning -> warning | stable |
| `gemini-3.1-pro-preview-high` | Gemini | Exact -> Exact | 49.98 -> 49.98 | warning -> warning | stable |
| `gemini-3.1-pro-preview-low` | Gemini | Exact -> Exact | 49.98 -> 49.98 | warning -> warning | stable |
| `gemini-3.1-pro-preview-medium` | Gemini | Exact -> Exact | 49.98 -> 49.98 | warning -> warning | stable |
| `gpt-4o-audio-preview` | Audio/Speech | Estimated -> Estimated | 49.98 -> 49.98 | warning -> warning | stable |
| `gpt-4o-mini-realtime-preview` | Realtime | Estimated -> Estimated | 49.81 -> 49.81 | warning -> warning | stable |
| `gpt-4o-mini-search-preview` | Search/Research | Estimated -> Estimated | 48.82 -> 48.82 | warning -> warning | stable |
| `gpt-4o-mini-transcribe` | Transcription | Estimated -> Estimated | 49.61 -> 49.61 | warning -> warning | stable |
| `gpt-4o-realtime-preview` | Realtime | Estimated -> Estimated | 49.89 -> 49.89 | warning -> warning | stable |
| `gpt-4o-search-preview` | Search/Research | Estimated -> Estimated | 49.98 -> 49.98 | warning -> warning | stable |
| `gpt-4o-transcribe` | Transcription | Estimated -> Estimated | 49.98 -> 49.98 | warning -> warning | stable |
| `gpt-5-search-api` | Search/Research | Estimated -> Estimated | 49.98 -> 49.98 | warning -> warning | stable |
| `gpt-5.4-mini` | General Chat | Exact -> Exact | 49.85 -> 49.85 | warning -> warning | stable |
| `gpt-5.4-nano` | General Chat | Exact -> Exact | 47.06 -> 47.06 | warning -> warning | stable |
| `gpt-audio` | Audio/Speech | Estimated -> Estimated | 49.89 -> 49.89 | warning -> warning | stable |
| `o4-mini-deep-research` | Search/Research | Estimated -> Estimated | 49.98 -> 49.98 | warning -> warning | stable |

## Repeated LOW_MARGIN_WARNING

- `gemini-3-flash-preview-nothinking`
- `gemini-3-flash-preview-thinking`
- `gemini-3.1-pro-preview`
- `gemini-3.1-pro-preview-high`
- `gemini-3.1-pro-preview-low`
- `gemini-3.1-pro-preview-medium`
- `gpt-4o-audio-preview`
- `gpt-4o-mini-realtime-preview`
- `gpt-4o-mini-search-preview`
- `gpt-4o-mini-transcribe`
- `gpt-4o-realtime-preview`
- `gpt-4o-search-preview`
- `gpt-4o-transcribe`
- `gpt-5-search-api`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-audio`
- `o4-mini-deep-research`

## Confidence Caveat

- **Exact**: Точные economics значения, приоритетный сигнал для действий.
- **Estimated**: Прокси-оценка себестоимости, требует осторожной интерпретации тренда.
- **Incomplete**: Неполные economics данные, тренд ограниченно интерпретируем.

