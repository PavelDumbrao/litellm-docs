# SPECIAL UNIT BILLING DESIGN

Date: 2026-03-26. Design + implementation status.

## Target Architecture
Worker reads tariff.billing_unit. If != "token": branch to unit-specific calc. Use raw spend USD as ground truth when unit metric unavailable.

## Unit Sources
Audio/Transcribe: metadata may have audio_duration_seconds. TTS: metadata may have char count. Search: no reliable metric. Realtime: no reliable metric.

## Fallback
If unit metric absent: fall to token proxy, log warning, do NOT fail billing.

## Pricing
Always from billing.public_model_tariff. Future: add unit_rate_credits column.

## Anti-Double-Charge
Do not bill both tokens AND unit metric. If unit metric available, use exclusively.

## Implementation Status (2026-03-26)

### ✅ Worker branch implemented
- `_extract_char_count_from_metadata()` — extracts char count from metadata
- `_calc_credits_chars()` — computes credits for chars_token billing
- `process_spend_log()` — branches on `billing_unit != "token"`, uses char metric if available, falls back to token proxy

### ⚠️ Validation RESULT: INERT
- Real TTS request made via LiteLLM proxy (HTTP 200, tts-1, 82 chars input)
- LiteLLM metadata contains: usage_object (tokens=0), cost_breakdown (USD), additional_usage_values (EMPTY)
- **NO character counts in spend log metadata** — chars_token billing CANNOT activate
- Worker falls back to token proxy (minimum charge applies)
- Root cause: LiteLLM does not expose OpenAI TTS character counts in metadata
- Next step: either patch LiteLLM upstream, or use input text length as char proxy in worker

### Affected models
- tts-1 (chars_token) — ❌ REMOVED from public surface (inert billing, legacy model)
- tts-hd-1 (chars_token) — branch active
- gpt-4o-mini-tts (chars_token) — branch active
- All other models — unchanged (standard token path)

## Verification
1. ✅ Add billing_unit branch in worker
2. ⚠️ Test 1 proxy model — chars_token billing INERT (no chars in metadata)
3. ✅ Fallback works — token proxy minimum applies correctly
4. ✅ Safety confirmed — no double-charge, token models unaffected
5. ✅ Blocker documented — LiteLLM does not expose character counts
