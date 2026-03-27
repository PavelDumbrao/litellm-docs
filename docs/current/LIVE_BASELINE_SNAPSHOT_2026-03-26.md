# LIVE BASELINE SNAPSHOT

Date: 2026-03-26. Status: TRUSTED after remediation.

## Frozen Baseline

Active public billing rows: 43
Public customer-facing models: ~31
Proxy-billed special-unit models: 13
Hidden -tools aliases: 14 (all is_active=false in DB)
Provider groups: 13
Billing/routing/docs alignment: ALIGNED

## Live Sources of Truth
1. /docker/litellm-xne6/config.yaml
2. billing.public_model_tariff (43 active rows)
3. /docker/litellm-xne6/custom_callbacks.py

## I7DC
Expected as separate provider. Not in billing DB. Routed via i7dc.com.

## Change Log
- 2026-03-26: tts-1 deactivated (is_active=false). 44→43 active rows. 14→13 proxy-billed. tts-1 removed from public surface due to inert chars-based billing.

## Drift Protection
Any change to config, billing DB, or provider groups triggers verification.
