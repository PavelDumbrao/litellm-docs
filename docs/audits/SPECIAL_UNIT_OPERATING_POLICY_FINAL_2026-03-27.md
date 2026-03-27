# SPECIAL UNIT OPERATING POLICY — FINAL AUDIT

Date: 2026-03-27. This is the canonical reference for all non-plain-token public models.

## 1. EXACT REMAINING SPECIAL PUBLIC MODELS (11)

### Audio (5 models)
| model | billing_unit | DB is_active | proxy behavior |
|---|---|---|---|
| gpt-4o-audio-preview | audio_token | true | token proxy |
| gpt-audio | audio_token | true | token proxy |
| gpt-audio-mini | audio_token | true | token proxy (reclassified from chars_token 2026-03-27) |
| gpt-4o-transcribe | audio_token | true | token proxy |
| gpt-4o-mini-transcribe | audio_token | true | token proxy |

### Search (3 models)
| model | billing_unit | DB is_active | proxy behavior |
|---|---|---|---|
| gpt-4o-search-preview | search_token | true | token proxy |
| gpt-4o-mini-search-preview | search_token | true | token proxy |
| gpt-5-search-api | search_token | true | token proxy |

### Realtime (2 models)
| model | billing_unit | DB is_active | proxy behavior |
|---|---|---|---|
| gpt-4o-realtime-preview | realtime_token | true | token proxy |
| gpt-4o-mini-realtime-preview | realtime_token | true | token proxy |

### Research (1 model)
| model | billing_unit | DB is_active | proxy behavior |
|---|---|---|---|
| o4-mini-deep-research | research_token | true | token proxy |

## 2. CATEGORY-LEVEL VERDICTS

| Category | Count | Policy class | Verdict |
|---|---|---|---|
| Audio | 5 | ACCEPTED_PROXY | Safe to keep. Token proxy is reasonable approximation for audio tokens. |
| Search | 3 | ACCEPTED_PROXY | Safe to keep. Per-token billing maps acceptably to search queries. |
| Realtime | 2 | REVIEW_LATER | Keep at current volume. Monitor cost delta. |
| Research | 1 | REVIEW_LATER | Keep at current volume. Monitor cost delta. |

## 3. MODELS SAFE TO KEEP AS PROXY (today)

All 11 models are safe to keep as proxy under current volume and billing structure.

**Rationale:**
- Audio: token counts are exposed in spend log. Under-charge risk is low.
- Search: token proxy covers query context + response. Acceptable.
- Realtime: medium risk but low volume. Rate set to approximate realtime cost.
- Research: low volume. Token proxy covers baseline cost.

## 4. MODELS NEEDING FUTURE REVIEW (not immediate removal)

| model | reason for future review |
|---|---|
| gpt-4o-realtime-preview | Realtime audio token cost diverges from text token cost |
| gpt-4o-mini-realtime-preview | Same as above |
| o4-mini-deep-research | Deep research may under-charge significantly at scale |

These do NOT require removal now. Volume is low. Policy class REVIEW_LATER is intentional.

## 5. CHARS_TOKEN CONFIRMATION

**No active billing_unit=chars_token models remain in public surface.**

| model | is_active | removed date |
|---|---|---|
| tts-1 | false | 2026-03-27 |
| gpt-4o-mini-tts | false | 2026-03-27 |
| tts-hd-1 | false | 2026-03-27 |

gpt-audio-mini was the last active chars_token entry — reclassified to audio_token on 2026-03-27.
Reclassification was correct: config.yaml shows input_cost_per_token (token billing), not per-char.

## 6. FINAL RECOMMENDATION

**Public surface status: TRUSTED WITH PROXY CAVEAT**

- 30/41 active public models: plain token billing — TRUSTED (clean, accurate)
- 11/41 active public models: proxy-billed special-unit — TRUSTED WITH PROXY CAVEAT
  - All categories have intentional, documented, and monitored proxy billing
  - No billing path is inert (unlike TTS chars_token which was removed)
  - Under-charge risk exists but is low to medium and volume-dependent

**No further immediate cleanup required.**

The public surface is operationally clean. All remaining ambiguity is documented and governed by SPECIAL_UNIT_OPERATING_POLICY.md.

**Next milestone for special-unit improvement:**
- When realtime or research volume grows → build proper unit metering
- When TTS demand justifies it → implement tts_billing_events table and re-enable