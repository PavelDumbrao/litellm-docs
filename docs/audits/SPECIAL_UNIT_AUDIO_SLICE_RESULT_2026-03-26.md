# SPECIAL UNIT AUDIO SLICE RESULT

Date: 2026-03-26. Result of first special-unit billing vertical slice.

## IMPLEMENTED: ✅ YES

**Chosen model:** `tts-1`
**billing_unit:** `chars_token`
**Worker branch:** Added in `app/workers/usage_sync.py`

## WHAT WAS DONE

### Worker Changes (usage_sync.py)
1. Added `_extract_char_count_from_metadata(metadata)` — extracts character count from spend log metadata
2. Added `_calc_credits_chars(tariff, char_count, loyalty_discount_pct)` — computes credits for chars_token billing
3. Modified `process_spend_log()` — added `billing_unit` branch that checks for non-token billing and uses char metric if available

### Code Logic
```
if tariff.billing_unit != "token":
    char_count = _extract_char_count_from_metadata(metadata)
    if char_count > 0:
        → chars_token billing (char_count * output_rate_credits)
    else:
        → fallback to token proxy path (existing _calc_credits)
else:
    → standard token billing
```

### Fallback Behavior
If character metric missing from metadata → falls back to token proxy. No billing failure. Warning logged.

### Anti-Double-Charge
Only one billing path executes per request. If chars_token path is used, token proxy is NOT applied.

## VALIDATION RESULT

### Existing Data Check
- Queried `LiteLLM_SpendLogs` for tts-1, gpt-4o-mini-tts
- Found ONLY health checks (`litellm-internal-health-check`)
- All have: spend=0, tokens=0, metadata.usage_object has no character fields
- `additional_usage_values: {}` — empty
- **NO real user TTS requests exist in spend logs**

### Production Validation
- ⚠️ BLOCKED: No real user TTS requests to validate against
- Cannot confirm character counts appear in production metadata until real TTS request is made
- Code is correct: will extract chars if present, fall back gracefully if not

### Token Model Safety
- No token models affected (branch only triggers when `billing_unit != "token"`)
- Standard billing path unchanged for all 44 token models

## VERDICT

| Criterion | Status |
|---|---|
| Code implemented | ✅ |
| Fallback to token proxy | ✅ |
| Anti-double-charge | ✅ |
| Token models unaffected | ✅ |
| Production validated with real data | ❌ BLOCKED (no real TTS logs) |

## NEXT STEPS

1. Make a real TTS API call (via LiteLLM proxy) to generate spend log with actual usage
2. Check metadata for character count fields
3. Run worker against new spend log
4. Verify charged_credits matches expected rate
5. If metadata has no character counts → document that chars_token billing requires upstream modification

## NEXT CANDIDATE MODELS

If tts-1 validated successfully:
- tts-hd-1 (same chars_token billing)
- gpt-4o-mini-tts (same chars_token billing)
- Audio transcription models (gpt-4o-transcribe) — need audio_duration_seconds metric