# SPECIAL UNIT AUDIO SLICE PLAN

Date: 2026-03-26. Implementation plan for first special-unit billing vertical slice.

## BLOCK A — CHOSEN MODEL

**Model:** `tts-1`
**billing_unit:** `chars_token`
**Unit metric source:** `litellm_spend_log.metadata.usage.characters` or `metadata.usage.char_count` or `metadata.usage.character_count`
**Why tts-1:** Simplest TTS model. Character count is the natural billing unit. Metadata is most likely to contain usage character counts from LiteLLM.

## BLOCK B — WORKER BRANCH DESIGN

### Changes to `app/workers/usage_sync.py`

#### 1. New function: `_extract_char_count_from_metadata(metadata: dict) -> Optional[int]`
Extracts character count from spend log metadata. Tries keys in priority order:
- `metadata.usage.characters`
- `metadata.usage.char_count`
- `metadata.usage.character_count`
- `metadata.usage.total_characters`

Returns None if no valid char count found.

#### 2. New function: `_calc_credits_chars(tariff, char_count, loyalty_discount_pct) -> Decimal`
Computes credits for chars_token billing:
- Uses `tariff.output_rate_credits` as rate per character
- Formula: `char_count * output_rate_credits`
- Applies minimum: `max(gross, tariff.request_minimum_credits)`
- Applies loyalty discount
- Returns net credits

#### 3. Modification to `process_spend_log()`
After tariff lookup and loyalty discount resolution, add branch:

```python
if tariff and tariff.billing_unit and tariff.billing_unit != "token":
    # Special-unit billing path
    metadata = log.get("metadata") or {}
    char_count = _extract_char_count_from_metadata(metadata)
    if char_count and char_count > 0:
        charged_credits = _calc_credits_chars(tariff, char_count, loyalty_discount_pct)
    else:
        # Fallback: token proxy path
        logger.debug(f"spend_log {spend_log_id}: chars_token metric missing for {model_name}, falling back to token proxy")
        charged_credits = _calc_credits(tariff, input_tokens, output_tokens, loyalty_discount_pct)
else:
    # Standard token billing
    charged_credits = _calc_credits(tariff, input_tokens, output_tokens, loyalty_discount_pct)
```

### Fallback Behavior
If character metric is missing from metadata → fall back to current token proxy path. No billing failure. Warning logged.

### Anti-Double-Charge
Only one billing path executes per request. If chars_token path is used, token proxy is NOT applied.

### Rollback Path
Set `is_active = false` for tts-1 tariff. Worker will skip it, fall to generic USD-based fallback.

## BLOCK C — VALIDATION PLAN

1. Make test TTS request via API (tts-1 model)
2. Check spend log metadata for character count
3. Compare: old proxy result vs new chars_token result
4. Verify against expected rate from billing.public_model_tariff
5. Confirm no double-charge
6. Confirm other token models unaffected

## BLOCK D — GIT ARTIFACTS

1. This file: `docs/audits/SPECIAL_UNIT_AUDIO_SLICE_PLAN_2026-03-26.md`
2. After validation: `docs/audits/SPECIAL_UNIT_AUDIO_SLICE_RESULT_2026-03-26.md`
3. Update: `docs/current/SPECIAL_UNIT_BILLING_DESIGN.md` — implementation status
4. Update: `docs/current/SPECIAL_UNIT_MODEL_MATRIX.md` — tts-1 from planned to implemented

## BLOCK E — SAFETY GUARANTEES

- No pricing values changed in billing DB
- Only tts-1 model affected
- Other 13 special-unit models unchanged
- All token models unchanged
- Fallback to token proxy if metric missing
- Idempotency preserved (spend_log_id unique constraint)