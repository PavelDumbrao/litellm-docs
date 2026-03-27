# TTS REBASELINE REPORT

Date: 2026-03-26. Documentation rebaseline after tts-1 removal + inert validation.

## Files Updated

| File | Change |
|---|---|
| LIVE_BASELINE_SNAPSHOT_2026-03-26.md | 44→43 active rows, 14→13 proxy-billed, added Change Log |
| POST_REMEDIATION_BASELINE_REPORT_2026-03-26.md | Updated baseline counts, Known Limitations, Next Task |
| CURRENT_SOURCE_OF_TRUTH.md | Added Special-Unit Billing Note |

## Before/After Baseline Changes

| Metric | Before | After |
|---|---|---|
| Active billing rows | 44 | 43 |
| Proxy-billed special-unit | 14 | 13 |
| Public customer-facing models | ~32 | ~31 |

## Current Public TTS Surface

| Model | billing_unit | Status |
|---|---|---|
| tts-hd-1 | chars_token | Active, public |
| gpt-4o-mini-tts | chars_token | Active, public |

## Current Special-Unit Truth for tts-1

- **Code:** chars_token branch exists in worker (serves all chars_token models)
- **Validation:** Live test confirmed chars-based billing INERT (no char counts in metadata)
- **DB:** is_active=false (id=67)
- **Public surface:** Fully removed from all customer-facing docs
- **Worker path:** Unreachable for tts-1 (_get_tariff returns None → USD fallback)

## Alignment Check

| Layer | tts-1 present? | Aligned? |
|---|---|---|
| billing.public_model_tariff | is_active=false | YES |
| config.yaml | Not in model_list | YES |
| LIVE_PUBLIC_MODEL_CATALOG.md | Removed | YES |
| LIVE_PRICING_REFERENCE.md | Removed | YES |
| LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md | Removed | YES |
| SPECIAL_UNIT_MODEL_MATRIX.md | Marked REMOVED | YES |
| SPECIAL_UNIT_BILLING_DESIGN.md | Marked REMOVED | YES |
| LIVE_BASELINE_SNAPSHOT.md | 43 rows (updated) | YES |
| POST_REMEDIATION_BASELINE_REPORT.md | Updated | YES |
| CURRENT_SOURCE_OF_TRUTH.md | Special-unit note added | YES |

## Docs Fully Aligned?

YES. All docs/current reflect post-tts-1 removal state. No doc advertises tts-1 as public offering.

## Next Recommended Docs Task

If chars_token billing needs to become active:
1. Patch LiteLLM upstream to expose char counts in metadata, OR
2. Add input text length proxy in worker (extract from messages column)
Then re-validate and update docs accordingly.