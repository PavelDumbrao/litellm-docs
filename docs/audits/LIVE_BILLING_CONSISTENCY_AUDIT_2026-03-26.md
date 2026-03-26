# LIVE BILLING CONSISTENCY AUDIT

Date: 2026-03-26. Source: billing.public_model_tariff (live DB) + config.yaml.

## BLOCK A — BILLING vs ROUTING CROSS-CHECK

### A.1 Totals

Active rows in billing DB: 61
Unique public models (deduplicated): ~47
-tools aliases active in DB: 8
Duplicate prefix entries: 8
Public models in config.yaml: ~32
Hidden -tools in config: 14
I7DC models: 3

### A.2 DUPLICATES IN BILLING DB

gpt-4.1 + openai/gpt-4.1 — BOTH active
gpt-4.1-mini + openai/gpt-4.1-mini — BOTH active
gpt-4o + openai/gpt-4o — BOTH active
gpt-4o-mini + openai/gpt-4o-mini — BOTH active
gemini-2.0-flash + google/gemini-2.0-flash — BOTH active
gemini-2.5-flash + google/gemini-2.5-flash — BOTH active
claude-haiku-4-5 + anthropic/claude-3-5-haiku-20241022 — BOTH active
claude-sonnet-4-6 + anthropic/claude-sonnet-4-5 — BOTH active

Risk: Worker may bill on prefix name instead of clean name.

### A.3 -tools ALIASES ACTIVE IN BILLING DB

claude-haiku-4-5-tools, claude-opus-4-6-tools, claude-sonnet-4-6-tools, gemini-2.5-flash-tools, gpt-4.1-mini-tools, gpt-4.1-nano-tools, gpt-4o-mini-tools, gpt-4o-tools

Risk: -tools aliases should NOT be in public_model_tariff. They are internal routing.

### A.4 MISSING FROM BILLING DB

i7dc-claude-haiku-4-5, i7dc-claude-sonnet-4-6, i7dc-claude-opus-4-6 — expected (separate provider, no billing layer)
gpt-5.4-tools, gpt-5.4-mini-tools, gpt-5.4-nano-tools — is_active=false (correct)
gemini-3-flash-tools, gemini-3.1-pro-preview-tools — not in DB (correct)

### A.5 LEGACY ENTRIES

anthropic/claude-3-5-haiku-20241022 — legacy full-path, superseded by claude-haiku-4-5
anthropic/claude-sonnet-4-5 — legacy full-path, superseded by claude-sonnet-4-6
gemini-2.0-flash — not in current public catalog

## BLOCK B — PRICE SURFACE CHECK

Safe token-billed: all standard text models have correct billing_unit and pricing.
Proxy-billed special-unit: 14 models have correct billing_unit labels but worker uses token proxy logic.
All pricing entries present and active.

## BLOCK C — DOC CONSISTENCY CHECK

LIVE_PUBLIC_MODEL_CATALOG.md: PARTIALLY ALIGNED — missing I7DC note
LIVE_PUBLIC_ALIAS_MAP.md: PARTIALLY ALIGNED — summary only
LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md: MOSTLY ALIGNED — good coverage
LIVE_PRICING_REFERENCE.md: MOSTLY ALIGNED — has safe + proxy models

## BLOCK D — REMEDIATION

### D.1 Summary

Active in billing DB: 61
Unique (deduplicated): ~47
Duplicates: 8
-tools in billing DB (active): 8
Proxy-billed: 14
Mismatches: 8 duplicates + 8 -tools

### D.2 P0 Action Required

1. Deactivate 8 duplicate prefix entries (UPDATE is_active=false)
2. Deactivate 8 -tools aliases (UPDATE is_active=false)
3. Deactivate 2 legacy anthropic/ entries (UPDATE is_active=false)

### D.3 Doc Corrections

LIVE_PUBLIC_MODEL_CATALOG.md: add I7DC note
Others: no changes needed

### D.4 Verdict

billing/routing/docs NOT fully aligned. Main issues:
1. 8 duplicate prefix entries active in DB
2. 8 -tools aliases active in DB (should be inactive)
3. Docs correct but DB has drift

P0: deactivate duplicates and -tools in billing.public_model_tariff
