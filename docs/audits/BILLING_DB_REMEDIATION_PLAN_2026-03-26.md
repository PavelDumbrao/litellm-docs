# BILLING DB REMEDIATION PLAN

Date: 2026-03-26

## Target Rows (17 total)

### Block 1: Duplicate prefix entries (8 rows)
ID 5 openai/gpt-4.1 — duplicate of gpt-4.1
ID 6 openai/gpt-4.1-mini — duplicate of gpt-4.1-mini
ID 3 openai/gpt-4o — duplicate of gpt-4o
ID 1 openai/gpt-4o-mini — duplicate of gpt-4o-mini
ID 9 google/gemini-2.0-flash — duplicate of gemini-2.0-flash
ID 10 google/gemini-2.5-flash — duplicate of gemini-2.5-flash
ID 7 anthropic/claude-3-5-haiku-20241022 — legacy, superseded
ID 8 anthropic/claude-sonnet-4-5 — legacy, superseded

### Block 2: Active -tools aliases (8 rows)
ID 21 claude-haiku-4-5-tools — internal routing
ID 27 claude-opus-4-6-tools — internal routing
ID 24 claude-sonnet-4-6-tools — internal routing
ID 31 gemini-2.5-flash-tools — internal routing
ID 17 gpt-4.1-mini-tools — internal routing
ID 19 gpt-4.1-nano-tools — internal routing
ID 14 gpt-4o-mini-tools — internal routing
ID 12 gpt-4o-tools — internal routing

### Block 3: Legacy non-public (1 row)
ID 34 gemini-2.0-flash — not in current public catalog

## Before/After
Before: 61 active. Deactivate: 17. After: 44 active.

## Risk Notes
- No routing/config changes
- No tariff recalculation
- Only is_active flag flipped
- Clean-name equivalents remain active
- Worker falls to fallback for deactivated -tools aliases

## Safety
All 17 rows have clean-name equivalents that remain active. No valid customer-facing surface removed.
