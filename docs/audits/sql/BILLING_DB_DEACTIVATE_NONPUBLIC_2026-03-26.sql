-- BILLING DB DEACTIVATE NONPUBLIC 2026-03-26
-- Only is_active=false. No routing/config changes. Idempotent.

-- Block 1: Duplicate prefix entries (8 rows)
UPDATE billing.public_model_tariff SET is_active=false WHERE id IN (5,6,3,1,9,10,7,8);
-- openai/gpt-4.1, openai/gpt-4.1-mini, openai/gpt-4o, openai/gpt-4o-mini
-- google/gemini-2.0-flash, google/gemini-2.5-flash
-- anthropic/claude-3-5-haiku-20241022, anthropic/claude-sonnet-4-5

-- Block 2: Active -tools aliases (8 rows)
UPDATE billing.public_model_tariff SET is_active=false WHERE id IN (21,27,24,31,17,19,14,12);
-- claude-haiku-4-5-tools, claude-opus-4-6-tools, claude-sonnet-4-6-tools
-- gemini-2.5-flash-tools, gpt-4.1-mini-tools, gpt-4.1-nano-tools
-- gpt-4o-mini-tools, gpt-4o-tools

-- Block 3: Legacy non-public (1 row)
UPDATE billing.public_model_tariff SET is_active=false WHERE id=34;
-- gemini-2.0-flash not in current public catalog
