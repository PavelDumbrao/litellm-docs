# SPECIAL-UNIT OPERATING POLICY

Date: 2026-03-27. Version: 1.0.
Scope: all proxy-billed non-plain-token public models in billing.public_model_tariff.

## Policy Statement

All special-unit models listed below are sold as **ACCEPTED_PROXY** SKUs.
This means:
- Billing is token-based (proxy approximation of the native unit)
- LiteLLM does not expose native units (audio minutes, chars, queries) in spend log
- Worker has no special-unit logic — falls back to token proxy calculation
- This is intentional and operationally accepted until specific unit-aware billing is built

Customer-facing promise: **you pay per token consumed, not per native unit**. Rates reflect approximate fair cost for the native operation.

What is explicitly NOT promised:
- Per-character billing for audio output
- Per-query billing for search
- Per-audio-minute billing for transcription/realtime
- Any unit-level metering accuracy

## CATEGORY POLICIES

---

### AUDIO (audio_token)
**Models:** gpt-4o-audio-preview, gpt-audio, gpt-audio-mini, gpt-4o-transcribe, gpt-4o-mini-transcribe

**Current behavior:** proxy via token. Worker calculates spend from token counts in spend log.

**Policy class: ACCEPTED_PROXY**

**Acceptable:** Yes. Audio models are priced per audio token by OpenAI. LiteLLM records token counts which serve as a reasonable proxy. Under-charge risk is low.

**Customer promise:** billed per token consumed.

**NOT promised:** exact per-audio-minute or per-audio-second billing.

**Trigger for re-review:** if volume exceeds 1000 requests/day and delta between token-proxy cost and actual OpenAI invoice exceeds 10%.

---

### SEARCH (search_token)
**Models:** gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-5-search-api

**Current behavior:** proxy via token. Search models consume tokens for context + response.

**Policy class: ACCEPTED_PROXY**

**Acceptable:** Yes. Search token pricing maps reasonably to token counts. Per-query billing would require separate query counter not available in spend log.

**Customer promise:** billed per token consumed in query + response.

**NOT promised:** flat per-query billing.

**Trigger for re-review:** if search-specific tooling becomes available in LiteLLM spend log.

---

### REALTIME (realtime_token)
**Models:** gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview

**Current behavior:** proxy via token. Realtime audio tokens are significantly more expensive than text tokens — token proxy may under-charge.

**Policy class: REVIEW_LATER**

**Acceptable:** Conditionally. Realtime audio token cost differs materially from text token cost. Under-charge risk is medium. Volume is currently low — acceptable risk.

**Customer promise:** billed per token consumed. Rate set to approximate realtime cost.

**NOT promised:** exact realtime audio token billing.

**Trigger for re-review / potential removal:**
- Volume exceeds 500 sessions/day
- Delta between proxy-billed cost and actual invoice exceeds 15%
- If billing disputes arise related to realtime pricing

---

### RESEARCH (research_token)
**Models:** o4-mini-deep-research

**Current behavior:** proxy via token. Deep research consumes many tokens and may invoke sub-agents — token proxy may under-charge significantly.

**Policy class: REVIEW_LATER**

**Acceptable:** Conditionally. Deep research operations are expensive. Token proxy provides baseline cost coverage. Volume is currently low.

**Customer promise:** billed per token consumed. Rate reflects premium research model cost.

**NOT promised:** per-research-task flat billing.

**Trigger for re-review / potential removal:**
- Any customer complaint about research billing accuracy
- Volume exceeds 200 requests/day
- If OpenAI changes research pricing to non-token model

---

## REMOVED MODELS (chars_token — billing inert)

| model | reason removed | date |
|---|---|---|
| tts-1 | chars_token billing inert — LiteLLM does not expose chars in spend log | 2026-03-27 |
| gpt-4o-mini-tts | chars_token billing inert — confirmed blocker | 2026-03-27 |
| tts-hd-1 | chars_token billing inert — confirmed blocker | 2026-03-27 |

**Re-enable condition:** separate tts_billing_events table + worker integration that reads char count at request time.

---

## POLICY CLASS DEFINITIONS

| Class | Meaning |
|---|---|
| ACCEPTED_PROXY | Token proxy billing is intentional and acceptable. No immediate action needed. |
| REVIEW_LATER | Token proxy is functional but has known accuracy risk. Monitor volume and cost delta. No immediate removal. |
| REMOVE_IF_RISK_INCREASES | Keep only while volume is low and no billing disputes arise. Remove proactively if risk materializes. |

---

## SUMMARY

| Category | Models | Policy class |
|---|---|---|
| Audio | 5 | ACCEPTED_PROXY |
| Search | 3 | ACCEPTED_PROXY |
| Realtime | 2 | REVIEW_LATER |
| Research | 1 | REVIEW_LATER |
| TTS | 0 active (3 removed) | N/A — removed |

No active billing_unit=chars_token models in public surface.
All 11 remaining special-unit models are governed by this policy.