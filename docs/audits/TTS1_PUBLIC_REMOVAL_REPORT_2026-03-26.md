# TTS-1 PUBLIC REMOVAL REPORT

Date: 2026-03-26. Controlled removal of tts-1 from customer-facing public surface.

## WHY REMOVED
- Live validation showed chars-based billing is INERT (no character counts in LiteLLM metadata)
- tts-1 is legacy TTS model — OpenAI recommends gpt-4o-mini-tts as primary
- Remaining public TTS models (tts-hd-1, gpt-4o-mini-tts) cover all use cases

## WHERE tts-1 EXISTED BEFORE REMOVAL

| Layer | Status Before | Action Taken |
|---|---|---|
| billing.public_model_tariff | is_active=true, id=67 | UPDATE is_active=false |
| LIVE_PUBLIC_MODEL_CATALOG.md | Listed under Audio/Speech | Removed from list |
| LIVE_PRICING_REFERENCE.md | Listed ($6.16/$6.16 per 1M) | Removed line |
| LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md | Listed under Proxy-Billed Special-Unit | Removed |
| SPECIAL_UNIT_MODEL_MATRIX.md | Listed as implemented | Marked REMOVED |
| SPECIAL_UNIT_BILLING_DESIGN.md | Listed in affected models | Marked REMOVED |

## CHANGES MADE

### billing.public_model_tariff
```sql
UPDATE billing.public_model_tariff SET is_active = false WHERE public_model_name = 'tts-1';
```
- Affected row: id=67
- Post-state: is_active=false

### Config exposure
- tts-1 is NOT in config.yaml model_list (not a public alias)
- No config change needed

### docs/current changes
1. LIVE_PUBLIC_MODEL_CATALOG.md — removed "tts-1" from Audio/Speech list
2. LIVE_PRICING_REFERENCE.md — removed "tts-1: $6.16/$6.16 per 1M" line
3. LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md — removed "tts-1(chars_token)" from Proxy-Billed list
4. SPECIAL_UNIT_MODEL_MATRIX.md — marked tts-1 as "REMOVED from public surface"
5. SPECIAL_UNIT_BILLING_DESIGN.md — marked tts-1 as "REMOVED from public surface"
6. LIVE_PUBLIC_ALIAS_MAP.md — no change needed (only generic mention)

## ALIGNMENT CHECK

| Layer | tts-1 present? | Aligned? |
|---|---|---|
| billing.public_model_tariff | is_active=false | YES |
| config.yaml | Not in model_list | YES |
| LIVE_PUBLIC_MODEL_CATALOG.md | Removed | YES |
| LIVE_PRICING_REFERENCE.md | Removed | YES |
| LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md | Removed | YES |
| SPECIAL_UNIT_MODEL_MATRIX.md | Marked REMOVED | YES |
| SPECIAL_UNIT_BILLING_DESIGN.md | Marked REMOVED | YES |

## INTERNAL CODE PATH
- Worker code still has chars_token branch — it handles ALL chars_token models, not just tts-1
- tts-1 worker code path remains but is now unreachable (is_active=false → _get_tariff returns None → worker uses USD fallback)
- No need to remove worker code — it serves tts-hd-1 and gpt-4o-mini-tts

## REMAINING TTS PUBLIC SURFACE

| Model | billing_unit | Status |
|---|---|---|
| tts-hd-1 | chars_token | Active, public |
| gpt-4o-mini-tts | chars_token | Active, public |

## VERDICT
tts-1 fully removed from public customer-facing surface. Billing DB deactivated. All docs aligned. Remaining TTS surface: tts-hd-1 + gpt-4o-mini-tts (both chars_token, both with inert chars billing fallback to token proxy).