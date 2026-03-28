# PUBLIC PRIMARY / F1 / F2 MATRIX

**Дата:** 2026-03-28  
**Scope:** factual audit of PUBLIC fallback policy only.  
**Source of truth:** live `/docker/litellm-xne6/config.yaml`, live env key-group names, live billing public tariffs, live smoke checks where possible.  
**Rule:** markdown/docs below live runtime are not treated as truth if they conflict with live config.

---

## 1) Live sources audited

1. `/docker/litellm-xne6/config.yaml`
2. `/docker/litellm-xne6/.env` and live `docker-compose.yml` env wiring
3. `GET http://127.0.0.1:8002/api/billing/models/tariffs` (public billing tariffs)
4. `GET http://127.0.0.1:32779/v1/models`
5. Representative live chat smoke checks:
   - `gpt-4.1`
   - `claude-sonnet-4-6`
   - `gemini-3-flash-preview`

---

## 2) How public models were defined for this audit

Public/customer-facing models in the main matrix are taken from live billing tariffs (`/api/billing/models/tariffs`).

This is intentionally **not** the same as full LiteLLM runtime exposure, because `/v1/models` currently exposes additional runtime/helper/internal aliases and test-scope entries.

- Public tariff models count: **41**
- `/v1/models` exposed ids count: includes public models **plus** hidden/tools/thinking/test aliases

---

## 3) PUBLIC fallback matrix

| Public Model | Primary Model/Route | Primary Provider | Primary Key Group | Fallback1 Model/Route | Fallback1 Provider | Fallback1 Key Group | Fallback2 Model/Route | Fallback2 Provider | Fallback2 Key Group | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `claude-haiku-4-5` | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o-mini` has 2 provider paths; Fallback2 runtime route `gpt-4.1-mini` has 2 provider paths |
| `claude-haiku-4-5-thinking` | `claude-haiku-4-5-thinking` | JENIYA | `JENIYA_CLAUDE15_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `claude-opus-4-5-thinking` | `claude-opus-4-5-thinking` | JENIYA | `JENIYA_CLAUDE15_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `claude-opus-4-6` | `claude-opus-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | `claude-sonnet-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `claude-sonnet-4-6` has 2 provider paths; Fallback2 runtime route `claude-haiku-4-5` has 2 provider paths |
| `claude-opus-4-6-thinking` | `claude-opus-4-6-thinking` | JENIYA | `JENIYA_CLAUDE15_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `claude-sonnet-4-5-thinking` | `claude-sonnet-4-5-thinking` | JENIYA | `JENIYA_CLAUDE15_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `claude-sonnet-4-6` | `claude-sonnet-4-6` | ANIDEAAI | `ANIDEAAI_API_KEY` | `claude-haiku-4-5` | ANIDEAAI | `ANIDEAAI_API_KEY` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `claude-haiku-4-5` has 2 provider paths; Fallback2 runtime route `gpt-4o` has 2 provider paths; Smoke confirmed live provider=POLO key_group=POLO_CLAUDE_API_KEY (response served via gpt-4o-mini on POLO; attempted_fallbacks=1) |
| `deepseek-v3.2` | `deepseek-v3.2` | JENIYA | `JENIYA_SKIDKA_API_KEY` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths |
| `gemini-2.5-flash` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gemini-3-flash-preview` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths |
| `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | POLO | `POLO_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | Fallback1 runtime route `gemini-2.5-flash` has 2 provider paths; Fallback2 runtime route `gemini-3-flash-preview` has 2 provider paths |
| `gemini-2.5-flash-thinking` | `gemini-2.5-flash-thinking` | POLO | `POLO_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | Fallback1 runtime route `gemini-2.5-flash` has 2 provider paths; Fallback2 runtime route `gemini-3-flash-preview` has 2 provider paths |
| `gemini-3-flash-preview` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gemini-2.5-flash` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths; Smoke confirmed live provider=JENIYA key_group=JENIYA_GEMINI_API_KEY (x-litellm-model-api-base=https://jeniya.top/v1; attempted_fallbacks=0) |
| `gemini-3-flash-preview-nothinking` | `gemini-3-flash-preview-nothinking` | POLO | `POLO_FASTGEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gemini-3-flash-preview` has 2 provider paths; Fallback2 runtime route `gemini-2.5-flash` has 2 provider paths |
| `gemini-3-flash-preview-thinking` | `gemini-3-flash-preview-thinking` | POLO | `POLO_FASTGEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gemini-3-flash-preview` has 2 provider paths; Fallback2 runtime route `gemini-2.5-flash` has 2 provider paths |
| `gemini-3.1-pro-preview` | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | `gemini-2.5-flash` | JENIYA | `JENIYA_GEMINI_API_KEY` | Fallback1 runtime route `gemini-3-flash-preview` has 2 provider paths; Fallback2 runtime route `gemini-2.5-flash` has 2 provider paths |
| `gemini-3.1-pro-preview-high` | `gemini-3.1-pro-preview-high` | POLO | `POLO_FASTGEMINI_API_KEY` | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback2 runtime route `gemini-3-flash-preview` has 2 provider paths |
| `gemini-3.1-pro-preview-low` | `gemini-3.1-pro-preview-low` | POLO | `POLO_FASTGEMINI_API_KEY` | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback2 runtime route `gemini-3-flash-preview` has 2 provider paths |
| `gemini-3.1-pro-preview-medium` | `gemini-3.1-pro-preview-medium` | POLO | `POLO_FASTGEMINI_API_KEY` | `gemini-3.1-pro-preview` | POLO | `POLO_GEMINI_API_KEY` | `gemini-3-flash-preview` | JENIYA | `JENIYA_GEMINI_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback2 runtime route `gemini-3-flash-preview` has 2 provider paths |
| `gpt-4.1` | `gpt-4.1` | POLO | `POLO_AZ_API_KEY` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o` has 2 provider paths; Fallback2 runtime route `gpt-4.1-mini` has 2 provider paths; Smoke confirmed live provider=POLO key_group=POLO_AZ_API_KEY (x-litellm-model-api-base=https://poloai.top/v1; attempted_fallbacks=0) |
| `gpt-4.1-mini` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o-mini` has 2 provider paths; Fallback2 runtime route `gpt-4.1-nano` has 2 provider paths |
| `gpt-4.1-nano` | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4.1-mini` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths |
| `gpt-4o` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o-mini` has 2 provider paths; Fallback2 runtime route `gpt-4.1-mini` has 2 provider paths |
| `gpt-4o-audio-preview` | `gpt-4o-audio-preview` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-mini` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4.1-mini` has 2 provider paths; Fallback2 runtime route `gpt-4.1-nano` has 2 provider paths |
| `gpt-4o-mini-realtime-preview` | `gpt-4o-mini-realtime-preview` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-mini-search-preview` | `gpt-4o-mini-search-preview` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-mini-transcribe` | `gpt-4o-mini-transcribe` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-realtime-preview` | `gpt-4o-realtime-preview` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-search-preview` | `gpt-4o-search-preview` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-4o-transcribe` | `gpt-4o-transcribe` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-5-search-api` | `gpt-5-search-api` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-5.3-codex` | `gpt-5.3-codex` | JENIYA | `JENIYA_CODEX_API_KEY` | `gpt-5.4` | JENIYA | `JENIYA_CODEX_API_KEY` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-5.4` has 4 provider paths; Fallback2 runtime route `gpt-4o` has 2 provider paths |
| `gpt-5.4` | `gpt-5.4` | JENIYA | `JENIYA_CODEX_API_KEY` | `gpt-4o` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 4 provider paths in live config; Fallback1 runtime route `gpt-4o` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths |
| `gpt-5.4-mini` | `gpt-5.4-mini` | JENIYA | `JENIYA_DEFAULT_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | `gpt-4.1-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4o-mini` has 2 provider paths; Fallback2 runtime route `gpt-4.1-mini` has 2 provider paths |
| `gpt-5.4-nano` | `gpt-5.4-nano` | JENIYA | `JENIYA_DEFAULT_API_KEY` | `gpt-4.1-nano` | POLO | `POLO_AZ_API_KEY` | `gpt-4o-mini` | POLO | `POLO_AZ_API_KEY` | Runtime route for primary wider than public slot: 2 provider paths in live config; Fallback1 runtime route `gpt-4.1-nano` has 2 provider paths; Fallback2 runtime route `gpt-4o-mini` has 2 provider paths |
| `gpt-audio` | `gpt-audio` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `gpt-audio-mini` | `gpt-audio-mini` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `o4-mini-deep-research` | `o4-mini-deep-research` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `text-embedding-3-large` | `text-embedding-3-large` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `text-embedding-3-small` | `text-embedding-3-small` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |
| `text-embedding-ada-002` | `text-embedding-ada-002` | POLO | `POLO_AZ_API_KEY` | `None` | — | `—` | `None` | — | `—` | Runtime route for primary wider than public slot: 2 provider paths in live config; No explicit Fallback1/Fallback2 configured in litellm_settings.fallbacks |

---

## 4) Public Policy vs Live Runtime Graph

This section is intentionally separated from the main public table.

### `gpt-4.1`
- Public policy: `gpt-4.1 -> gpt-4o -> gpt-4.1-mini`
- Live runtime primary slot: POLO/POLO_AZ_API_KEY (order=1), JENIYA/JENIYA_AZ15_API_KEY (order=2)
- Classification: **expected technical detail**
- Note: Smoke stayed on Primary POLO path with no fallback; runtime still has second provider path on JENIYA behind same public slot.

### `gpt-5.4`
- Public policy: `gpt-5.4 -> gpt-4o -> gpt-4o-mini`
- Live runtime primary slot: JENIYA/JENIYA_CODEX_API_KEY (order=1), POLO/POLO_CODEX_GPT_API_KEY (order=2), POLO/POLO_AZ_API_KEY (order=3), JENIYA/JENIYA_AZ15_API_KEY (order=4)
- Classification: **expected technical detail**
- Note: Public policy gives 3 visible slots, runtime keeps a wider provider-path chain behind at least one slot.

### `gpt-5.4-mini`
- Public policy: `gpt-5.4-mini -> gpt-4o-mini -> gpt-4.1-mini`
- Live runtime primary slot: JENIYA/JENIYA_DEFAULT_API_KEY (order=1), JENIYA/JENIYA_AZ15_API_KEY (order=2)
- Classification: **expected technical detail**
- Note: Public policy gives 3 visible slots, runtime keeps a wider provider-path chain behind at least one slot.

### `claude-sonnet-4-6`
- Public policy: `claude-sonnet-4-6 -> claude-haiku-4-5 -> gpt-4o`
- Live runtime primary slot: ANIDEAAI/ANIDEAAI_API_KEY (order=1), POLO/POLO_CLAUDE_API_KEY (order=3)
- Classification: **confirmed mismatch**
- Note: Smoke request for public claude-sonnet-4-6 actually served via fallback model-group gpt-4o-mini on POLO, not by claude-sonnet-4-6 provider path.

### `claude-opus-4-6`
- Public policy: `claude-opus-4-6 -> claude-sonnet-4-6 -> claude-haiku-4-5`
- Live runtime primary slot: ANIDEAAI/ANIDEAAI_API_KEY (order=1), POLO/POLO_CLAUDE_API_KEY (order=3)
- Classification: **expected technical detail**
- Note: Public policy gives 3 visible slots, runtime keeps a wider provider-path chain behind at least one slot.

### `gemini-3-flash-preview`
- Public policy: `gemini-3-flash-preview -> gemini-2.5-flash -> gpt-4o-mini`
- Live runtime primary slot: JENIYA/JENIYA_GEMINI_API_KEY (order=1), POLO/POLO_GEMINI_API_KEY (order=2)
- Classification: **expected technical detail**
- Note: Smoke stayed on JENIYA primary path; runtime also has POLO fallback path inside the same public slot.

### `gemini-3.1-pro-preview`
- Public policy: `gemini-3.1-pro-preview -> gemini-3-flash-preview -> gemini-2.5-flash`
- Live runtime primary slot: POLO/POLO_GEMINI_API_KEY (order=none)
- Classification: **expected technical detail**
- Note: Public policy gives 3 visible slots, runtime keeps a wider provider-path chain behind at least one slot.

### `gpt-4o-mini`
- Public policy: `gpt-4o-mini -> gpt-4.1-mini -> gpt-4.1-nano`
- Live runtime primary slot: POLO/POLO_AZ_API_KEY (order=1), JENIYA/JENIYA_AZ15_API_KEY (order=2)
- Classification: **expected technical detail**
- Note: Public policy gives 3 visible slots, runtime keeps a wider provider-path chain behind at least one slot.


---

## 5) Models exposed in `/v1/models` but not treated as public matrix rows

These were visible in live `/v1/models`, but excluded from the main public matrix because they are not present in live billing tariffs.

### Internal/helper aliases
- `claude-haiku-4-5-tools`
- `claude-sonnet-4-6-tools`
- `claude-opus-4-6-tools`
- `gpt-4o-tools`
- `gpt-4o-mini-tools`
- `gpt-5.4-tools`
- `gpt-5.4-mini-tools`
- `gpt-4.1-mini-tools`
- `gpt-4.1-nano-tools`
- `gemini-2.5-flash-tools`
- `gemini-3-flash-tools`
- `gemini-3.1-pro-preview-tools`
- `gpt-5.4-nano-tools`

### Thinking / variant aliases exposed live
- `claude-haiku-4-5-thinking`
- `claude-sonnet-4-5-thinking`
- `claude-opus-4-5-thinking`
- `claude-opus-4-6-thinking`
- `gemini-2.5-flash-thinking`
- `gemini-3-flash-preview-thinking`
- `gemini-3-flash-preview-nothinking`
- `gemini-3.1-pro-preview-high`
- `gemini-3.1-pro-preview-low`
- `gemini-3.1-pro-preview-medium`

### Suspicious public exposure / test scope
- `i7dc-claude-haiku-4-5`
- `i7dc-claude-sonnet-4-6`
- `i7dc-claude-opus-4-6`

These three are visible in `/v1/models`, but absent from public billing tariffs, so they look like **runtime-visible non-public entries**.

---

## 6) Smoke checks

### `/v1/models`
- Status: **200 OK**
- Result: live model list includes public models **and** runtime/helper aliases.

### Representative chat checks

1. `gpt-4.1`
   - Status: **200 OK**
   - Confirmed provider evidence: `x-litellm-model-api-base=https://poloai.top/v1`
   - Confirmed live route: Primary on **POLO / `POLO_AZ_API_KEY`**
   - Attempted fallbacks: `0`

2. `claude-sonnet-4-6`
   - Status: **200 OK**
   - Response evidence shows:
     - `x-litellm-attempted-fallbacks: 1`
     - `x-litellm-model-group: gpt-4o-mini`
     - `x-litellm-model-api-base=https://poloai.top/v1`
   - Interpretation: live request for public `claude-sonnet-4-6` ended on **fallback model-group `gpt-4o-mini`**, not on claude provider path.

3. `gemini-3-flash-preview`
   - Status: **200 OK**
   - Confirmed provider evidence: `x-litellm-model-api-base=https://jeniya.top/v1`
   - Confirmed live route: Primary on **JENIYA / `JENIYA_GEMINI_API_KEY`**
   - Attempted fallbacks: `0`

### Health
- Container `litellm-xne6-litellm-1` is **healthy** in `docker ps`.
- Direct local probing mistake was corrected: service is bound on host port `32779`, not `4000`.

---

## 7) HARD VERDICT

1. **Public matrix formed:** **YES, but with caveats.**
2. **Precisely confirmed live facts:**
   - public model set from billing tariffs,
   - fallback policy from live `litellm_settings.fallbacks`,
   - provider/key-group mapping for visible primary runtime paths from live config,
   - smoke-confirmed actual path for `gpt-4.1`, `claude-sonnet-4-6`, `gemini-3-flash-preview`.
3. **Remaining uncertainties:**
   - Fallback1/Fallback2 provider actually chosen at runtime cannot be guaranteed in advance when the fallback route itself has multiple provider paths; matrix shows the first live route behind that fallback alias, but the deeper runtime path may widen.
   - Models not smoke-tested remain config-confirmed rather than response-confirmed.
4. **Suspicion of runtime divergence from intended public policy:** **YES.** Strongest evidence is public `claude-sonnet-4-6`, where live request resolved to fallback `gpt-4o-mini`.
5. **Need separate remediation task after this audit:** **YES.** At minimum to decide whether `/v1/models` should expose non-public/runtime aliases and whether `claude-sonnet-4-6` fallback behavior matches intended customer-facing policy.
