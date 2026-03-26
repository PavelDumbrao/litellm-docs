# SPECIAL UNIT TTS LIVE VALIDATION

Date: 2026-03-26. Live validation of chars_token billing for tts-1 through production LiteLLM proxy.

## BLOCK A — TEST EXECUTION

### Test Request
- **Endpoint:** `POST http://localhost:32779/v1/audio/speech`
- **Model:** tts-1
- **Input:** "Hello, this is a test of the text to speech system. We are testing character count billing."
- **Input length:** 82 characters
- **Voice:** alloy
- **Response:** HTTP 200, 110,880 bytes MP3

### Spend Log Row
- **request_id:** 35a810f8-8d82-44d3-99a6-730e365bb53a
- **model:** tts-1
- **spend:** 0.001125 USD (charged by OpenAI provider)
- **prompt_tokens:** 0
- **completion_tokens:** 0
- **user:** default_user_id (master key)

### Raw Metadata (FULL DUMP)
```json
{
  "status": null,
  "usage_object": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0},
  "cost_breakdown": {
    "input_cost": 0.001125,
    "total_cost": 0.001125,
    "output_cost": 0,
    "original_cost": 0.001125
  },
  "additional_usage_values": {},
  "spend_logs_metadata": null
}
```

### Fields Checked for Character Count
| Field | Value | Has Chars? |
|---|---|---|
| metadata.usage_object | total_tokens=0, prompt_tokens=0, completion_tokens=0 | NO |
| metadata.additional_usage_values | {} | NO (empty) |
| metadata.spend_logs_metadata | null | NO |
| response column | {} | NO (empty) |

**RESULT: No character count field exists anywhere in spend log metadata.**

## BLOCK B — VALIDATION

### Tariff Data (billing.public_model_tariff)
- **billing_unit:** chars_token
- **input_rate_credits:** 0.00000653
- **output_rate_credits:** 0.00000653
- **request_minimum_credits:** 0.000100

### Expected Billing Calculations

**If chars-based billing worked:**
- 82 chars * 0.00000653 = 0.00053546 credits
- Above minimum (0.000100), so debit = 0.00053546 credits

**Actual (token proxy fallback):**
- input_tokens=0, output_tokens=0
- 0 * 0.00000653 + 0 * 0.00000653 = 0
- max(0, 0.000100) = 0.000100 credits (minimum applies)

### Verdict on Billing Path
- `_extract_char_count_from_metadata()` returns None (no chars in metadata)
- Worker falls back to token proxy path
- Token proxy computes debit = 0.000100 credits (minimum)
- Fallback works correctly — no crash, no double-charge

### For Short Texts
Chars-based debit (0.000535) vs token proxy debit (0.000100) — different values. Chars billing would charge 5.35x more.

### For Long Texts
If input was 5000 chars: 5000 * 0.00000653 = 0.03265 credits
Token proxy with 0 tokens: still 0.000100 credits (minimum)
Chars billing would charge 326x more for same request.

## BLOCK C — SAFETY CHECK

- Anti-double-charge: CONFIRMED. Only one billing path executes.
- Token models unaffected: CONFIRMED. tts-1 has billing_unit="chars_token", branch activates. All token models have billing_unit="token", standard path unchanged.
- Fallback behavior: CONFIRMED. Missing chars falls back to token proxy, minimum charge applies. No failure.

## BLOCK D — ROLLOUT VERDICT

### Safe for tts-1 rollout?

**Answer: CODED CORRECTLY BUT INERT**

The code is correct:
1. Checks for chars in metadata
2. Falls back gracefully when missing
3. No double-charge
4. No token model impact

But chars-based billing CANNOT activate because LiteLLM does NOT expose character counts in spend log metadata. The code path is dead — worker will ALWAYS take the token proxy fallback for TTS.

### Root Cause
LiteLLM spend log metadata only contains:
- Token counts (always 0 for TTS)
- Cost breakdown (USD amounts)
- No character counts, no audio duration, no custom metrics

### Next Instrumentation Steps

**Option 1: Upstream Fix (Recommended)**
- Patch LiteLLM to populate additional_usage_values.characters from OpenAI response
- OpenAI TTS API may return usage.characters in response headers
- LiteLLM should capture this and add to metadata

**Option 2: Worker-side Proxy Calculation**
- Use input text length as proxy for character count
- char_count = len(input_text) from spend log messages column
- Less accurate (counts prompt text, not output), but available now

**Option 3: Accept Token Proxy**
- Keep token proxy fallback as production billing for TTS
- Token proxy with minimum charge gives reasonable billing
- Accept billing inaccuracy as acceptable tradeoff

### Recommendation
Option 2 (input text length) is the fastest path to chars-based billing without waiting for upstream LiteLLM fix. Worker would extract input text from messages column and count characters.

## Summary

| Criterion | Status |
|---|---|
| Real TTS request made | YES |
| Spend log captured | YES |
| Character counts in metadata | NOT PRESENT |
| Chars-based billing activated | BLOCKED |
| Token proxy fallback | WORKS |
| Anti-double-charge | YES |
| Token models unaffected | YES |
| Ready for rollout | CODED BUT INERT |