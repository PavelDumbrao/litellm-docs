# BILLING ROUTING ALIGNMENT RUNBOOK

Date: 2026-03-26.

## When to Run
After model changes, pricing seeds, fallback changes, provider changes, before rollout, after config reload.

## Order
1. Read config.yaml model_list
2. Query billing.public_model_tariff WHERE is_active=true
3. Compare sets
4. Check docs/current
5. Report in docs/audits/

## Files to Read
1. /docker/litellm-xne6/config.yaml
2. billing.public_model_tariff
3. docs/current/LIVE_BASELINE_SNAPSHOT_2026-03-26.md

## Outputs
docs/audits/LIVE_BILLING_CONSISTENCY_AUDIT_[date].md
Corrected docs/current/ if drift found

## Stop Conditions
Ambiguous naming, missing pricing, -tools in active surface, duplicate prefixes active
