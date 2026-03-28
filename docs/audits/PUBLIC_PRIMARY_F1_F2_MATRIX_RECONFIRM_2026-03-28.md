# PUBLIC PRIMARY / F1 / F2 MATRIX — RECONFIRM

**Дата reconfirm-аудита (UTC):** 2026-03-28T13:20:19Z  
**Scope:** только factual audit по PUBLIC моделям LiteLLM (без изменений runtime/config).  
**Source of truth:** live `/docker/litellm-xne6/config.yaml`, live env key groups (`.env`), live `/v1/models`, live public billing tariffs, live smoke requests.  
**Rule:** если docs/markdown расходятся с live, истиной считается live.

---

## BLOCK A — LIVE SOURCE AUDIT

### A1. Что перепроверено live
1. `/docker/litellm-xne6/config.yaml`
2. `/docker/litellm-xne6/.env` и live env key groups
3. `GET /v1/models` (master key)
4. `GET /v1/model/info` (master key)
5. `GET /api/billing/models/tariffs` (public billing set)
6. `GET /health/readiness` и `/health/liveliness`
7. Smoke requests по public моделям

### A2. Live summary
- `model_list` entries: **104**
- `routing_strategy`: **simple-shuffle**
- `router num_retries`: **2**
- `router timeout`: **60s**
- `enable_pre_call_checks`: **True**
- `fallbacks` rules count: **36**
- Public models (from billing tariffs): **41**
- `/v1/models` exposed ids: **60**
- Visible helper `-tools` aliases on `/v1/models`: **13**
- Visible `i7dc-*` aliases on `/v1/models`: **3**

### A3. Callbacks/router settings (только то, что влияет на PUBLIC runtime)
- `JsonHealingV1Handler`: **active**
- `ToolsRoutingHandler`: **active**
- `TtsBillingHandler`: **active**
- `_PROXY_MaxBudgetLimiter`: **active**
- `_PROXY_MaxParallelRequestsHandler_v3`: **active**

---

## BLOCK B — ГЛАВНАЯ PUBLIC MATRIX

| Public Model | Primary Model/Route | Primary Provider | Primary Key Group | Primary Confirmed? | Fallback1 Model/Route | Fallback1 Provider | Fallback1 Key Group | Fallback1 Confirmed? | Fallback2 Model/Route | Fallback2 Provider | Fallback2 Key Group | Fallback2 Confirmed? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `claude-haiku-4-5` | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `claude-haiku-4-5` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths |
| `claude-haiku-4-5-thinking` | `claude-haiku-4-5-thinking` | POLO | `POLO_CLAUDE_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `claude-haiku-4-5-thinking` шире public-слота: 2 deployment paths |
| `claude-opus-4-5-thinking` | `claude-opus-4-5-thinking` | POLO | `POLO_CLAUDE_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `claude-opus-4-5-thinking` шире public-слота: 2 deployment paths |
| `claude-opus-4-6` | `claude-opus-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config) | `claude-sonnet-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config) | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config) | Runtime для `claude-opus-4-6` шире public-слота: 2 deployment paths ; Runtime для `claude-sonnet-4-6` шире public-слота: 2 deployment paths ; Runtime для `claude-haiku-4-5` шире public-слота: 2 deployment paths |
| `claude-opus-4-6-thinking` | `claude-opus-4-6-thinking` | JENIYA | `JENIYA_CLAUDE15_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `claude-sonnet-4-5-thinking` | `claude-sonnet-4-5-thinking` | POLO | `POLO_CLAUDE_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `claude-sonnet-4-5-thinking` шире public-слота: 2 deployment paths |
| `claude-sonnet-4-6` | `claude-sonnet-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config + smoke request) | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | YES (live config) | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `claude-sonnet-4-6` шире public-слота: 2 deployment paths ; Runtime для `claude-haiku-4-5` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o` шире public-слота: 2 deployment paths ; CONFIRMED MISMATCH: smoke для `claude-sonnet-4-6` вернул model_group `gpt-4o-mini` (attempted_fallbacks=1), а public chain = Primary `claude-sonnet-4-6` -> F1 `claude-haiku-4-5` -> F2 `gpt-4o` ; Smoke provider evidence: x-litellm-model-api-base=https://poloai.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=gpt-4o-mini, order=1 |
| `deepseek-v3.2` | `deepseek-v3.2` | JENIYA | `JENIYA_SKIDKA_API_KEY` | YES (smoke: stayed on Primary) | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `deepseek-v3.2` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Smoke provider evidence: x-litellm-model-api-base=https://jeniya.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=deepseek-v3.2, order=2 |
| `gemini-2.5-flash` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths |
| `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths |
| `gemini-2.5-flash-thinking` | `gemini-2.5-flash-thinking` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths |
| `gemini-3.1-pro-preview` | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths ; Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths |
| `gemini-3.1-pro-preview-high` | `gemini-3.1-pro-preview-high` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3.1-pro-preview-high` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths |
| `gemini-3.1-pro-preview-low` | `gemini-3.1-pro-preview-low` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3.1-pro-preview-low` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths |
| `gemini-3.1-pro-preview-medium` | `gemini-3.1-pro-preview-medium` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3.1-pro-preview-medium` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths |
| `gemini-3-flash-preview` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (smoke: stayed on Primary) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths ; Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Smoke provider evidence: x-litellm-model-api-base=https://jeniya.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=gemini-3-flash-preview, order=1 |
| `gemini-3-flash-preview-nothinking` | `gemini-3-flash-preview-nothinking` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3-flash-preview-nothinking` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths ; Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths |
| `gemini-3-flash-preview-thinking` | `gemini-3-flash-preview-thinking` | POLO | `POLO_GEMINI_API_KEY` | YES (live config) | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | YES (live config) | Runtime для `gemini-3-flash-preview-thinking` шире public-слота: 2 deployment paths ; Runtime для `gemini-3-flash-preview` шире public-слота: 2 deployment paths ; Runtime для `gemini-2.5-flash` шире public-слота: 2 deployment paths |
| `gpt-4.1` | `gpt-4.1` | POLO | `POLO_AZ_API_KEY` | YES (smoke: stayed on Primary) | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-4.1` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths ; Smoke provider evidence: x-litellm-model-api-base=https://poloai.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=gpt-4.1, order=1 |
| `gpt-4.1-mini` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-nano` шире public-слота: 2 deployment paths |
| `gpt-4.1-nano` | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-4.1-nano` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths |
| `gpt-4o` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-4o` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths |
| `gpt-4o-audio-preview` | `gpt-4o-audio-preview` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `gpt-4o-audio-preview` шире public-слота: 2 deployment paths |
| `gpt-4o-mini` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-nano` шире public-слота: 2 deployment paths |
| `gpt-4o-mini-realtime-preview` | `gpt-4o-mini-realtime-preview` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-4o-mini-search-preview` | `gpt-4o-mini-search-preview` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-4o-mini-transcribe` | `gpt-4o-mini-transcribe` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-4o-realtime-preview` | `gpt-4o-realtime-preview` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-4o-search-preview` | `gpt-4o-search-preview` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-4o-transcribe` | `gpt-4o-transcribe` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `gpt-4o-transcribe` шире public-слота: 2 deployment paths |
| `gpt-5.3-codex` | `gpt-5.3-codex` | JENIYA | `JENIYA_CODEX_API_KEY` | YES (live config) | `gpt-5.4` | JENIYA | `JENIYA_CODEX_API_KEY` | YES (live config) | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-5.3-codex` шире public-слота: 2 deployment paths ; Runtime для `gpt-5.4` шире public-слота: 4 deployment paths ; Runtime для `gpt-4o` шире public-слота: 2 deployment paths |
| `gpt-5.4` | `gpt-5.4` | JENIYA | `JENIYA_CODEX_API_KEY` | YES (live config + smoke request) | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | YES (smoke: request resolved to Fallback1) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-5.4` шире public-слота: 4 deployment paths ; Runtime для `gpt-4o` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Smoke: `gpt-5.4` ушёл на Fallback1 `gpt-4o` (attempted_fallbacks=1) ; Smoke provider evidence: x-litellm-model-api-base=https://poloai.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=gpt-4o, order=1 |
| `gpt-5.4-mini` | `gpt-5.4-mini` | JENIYA | `JENIYA_DEFAULT_API_KEY` | YES (live config + smoke request) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (smoke: request resolved to Fallback1) | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-5.4-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-mini` шире public-слота: 2 deployment paths ; Smoke: `gpt-5.4-mini` ушёл на Fallback1 `gpt-4o-mini` (attempted_fallbacks=1) ; Smoke provider evidence: x-litellm-model-api-base=https://poloai.top/v1 ; Smoke key-group direct evidence: UNCONFIRMED (header не содержит key-group); inferred deployment by model_id -> model_name=gpt-4o-mini, order=1 |
| `gpt-5.4-nano` | `gpt-5.4-nano` | JENIYA | `JENIYA_DEFAULT_API_KEY` | YES (live config) | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | Runtime для `gpt-5.4-nano` шире public-слота: 2 deployment paths ; Runtime для `gpt-4.1-nano` шире public-слота: 2 deployment paths ; Runtime для `gpt-4o-mini` шире public-слота: 2 deployment paths |
| `gpt-5-search-api` | `gpt-5-search-api` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-audio` | `gpt-audio` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `gpt-audio-mini` | `gpt-audio-mini` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `o4-mini-deep-research` | `o4-mini-deep-research` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | — |
| `text-embedding-3-large` | `text-embedding-3-large` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `text-embedding-3-large` шире public-слота: 2 deployment paths |
| `text-embedding-3-small` | `text-embedding-3-small` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `text-embedding-3-small` шире public-слота: 2 deployment paths |
| `text-embedding-ada-002` | `text-embedding-ada-002` | POLO | `POLO_AZ_API_KEY` | YES (live config) | `None` | None | `None` | YES (N/A) | `None` | None | `None` | YES (N/A) | Runtime для `text-embedding-ada-002` шире public-слота: 2 deployment paths |

---

## BLOCK C — Public Policy vs Live Runtime Graph

> Эта секция намеренно отделена от главной public-матрицы.

| Scope | PUBLIC Primary/F1/F2 (policy) | Live runtime observation | Classification |
|---|---|---|---|
| gpt-4.1 | `gpt-4.1 -> gpt-4o -> gpt-4.1-mini` | Smoke stayed on Primary `gpt-4.1` (POLO); runtime has extra provider path on JENIYA inside same slot | **expected technical detail** |
| gemini-3-flash-preview | `gemini-3-flash-preview -> gemini-2.5-flash -> gpt-4o-mini` | Smoke stayed on Primary `gemini-3-flash-preview` (JENIYA); runtime has extra POLO path inside slot | **expected technical detail** |
| deepseek-v3.2 | `deepseek-v3.2 -> gpt-4o -> gpt-4o-mini` | Smoke stayed on Primary `deepseek-v3.2` with attempted_retries=1 | **expected technical detail** |
| gpt-5.4 | `gpt-5.4 -> gpt-4o -> gpt-4o-mini` | Smoke resolved to fallback model_group `gpt-4o` with attempted_fallbacks=1 | **suspicious drift** |
| gpt-5.4-mini | `gpt-5.4-mini -> gpt-4o-mini -> gpt-4.1-mini` | Smoke resolved to fallback model_group `gpt-4o-mini` with attempted_fallbacks=1 | **suspicious drift** |
| claude-sonnet-4-6 | `claude-sonnet-4-6 -> claude-haiku-4-5 -> gpt-4o` | Smoke resolved to `gpt-4o-mini` (не входит в public F1/F2 chain) | **confirmed mismatch** |
| Public surface visibility | `Hidden/helper aliases не должны путаться с public policy` | В /v1/models видны 13 `-tools` и 3 `i7dc-*` alias alongside public models | **suspicious drift** |

---

## BLOCK D — SMOKE TESTS (MANDATORY)

| Requested PUBLIC model | HTTP status | Response model | Provider evidence | Key-group evidence | Attempted fallbacks | Attempted retries | Matrix path match? |
|---|---:|---|---|---|---:|---:|---|
| `gpt-4.1` | 200 | `gpt-4.1` | POLO (`https://poloai.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 0 | 0 | YES |
| `claude-sonnet-4-6` | 200 | `gpt-4o-mini-2024-07-18` | POLO (`https://poloai.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 1 | 0 | NO (runtime_group=gpt-4o-mini) |
| `gemini-3-flash-preview` | 200 | `gemini-3-flash-preview` | JENIYA (`https://jeniya.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 0 | 0 | YES |
| `gpt-5.4` | 200 | `gpt-4o-2024-08-06` | POLO (`https://poloai.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 1 | 0 | YES |
| `gpt-5.4-mini` | 200 | `gpt-4o-mini-2024-07-18` | POLO (`https://poloai.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 1 | 0 | YES |
| `deepseek-v3.2` | 200 | `deepseek-v3.2` | JENIYA (`https://jeniya.top/v1`) | UNCONFIRMED (нет прямого заголовка key-group) | 0 | 1 | YES |

### Container health after smoke
- `litellm-xne6-litellm-1|Up 6 hours (healthy)|0.0.0.0:32779->4000/tcp, [::]:32779->4000/tcp`

---

## BLOCK E — HARD VERDICT

1. **PUBLIC matrix сформирована:** YES (41 public models из live billing tariffs покрыты).
2. **Точно подтверждено live-фактами:** live config graph, live public tariffs, live `/v1/models`, smoke path для 6 representative public моделей.
3. **Где остались UNCONFIRMED:** прямой key-group из smoke headers (LiteLLM не возвращает key-group в response headers), модели без smoke подтверждены на уровне live config (не на уровне конкретного runtime события).
4. **Confirmed mismatches:** `claude-sonnet-4-6` smoke-resolve -> `gpt-4o-mini` (вне публичной цепочки Primary/F1/F2 для этой модели).
5. **Нужна отдельная remediation-задача:** YES (policy/runtime alignment, особенно для claude-sonnet-4-6 и visible helper aliases in `/v1/models`).
6. **Safe ли текущий LiteLLM runtime as-is:**
   - **Operational safety:** YES (smoke 200, контейнер healthy).
   - **Policy safety для строгих PUBLIC гарантий:** NO (есть policy/runtime drift и confirmed mismatch).

---

## Appendix — Helper/Hidden runtime aliases currently visible on `/v1/models`

### `-tools` aliases (visible)
- `claude-haiku-4-5-tools`
- `claude-opus-4-6-tools`
- `claude-sonnet-4-6-tools`
- `gemini-2.5-flash-tools`
- `gemini-3-flash-tools`
- `gemini-3.1-pro-preview-tools`
- `gpt-4.1-mini-tools`
- `gpt-4.1-nano-tools`
- `gpt-4o-mini-tools`
- `gpt-4o-tools`
- `gpt-5.4-mini-tools`
- `gpt-5.4-nano-tools`
- `gpt-5.4-tools`

### `i7dc-*` aliases (visible)
- `i7dc-claude-haiku-4-5`
- `i7dc-claude-opus-4-6`
- `i7dc-claude-sonnet-4-6`
