# POST REMEDIATION BASELINE REPORT

Date: 2026-03-26

## Current Baseline
Active billing rows: 44. Public models: ~32. Proxy-billed: 14. Hidden -tools: 14 (inactive). Providers: 13. Alignment: ALIGNED.

## Trusted Surface
config.yaml + billing.public_model_tariff + custom_callbacks.py. docs/current/ = canonical layer. Git = PavelDumbrao/litellm-docs.

## Known Limitations
1. Proxy-billed models use token proxy — not fully accurate per actual unit
2. Worker has no special-unit logic — billing_unit stored but unused
3. I7DC not in billing DB — separate provider

## Top 5 Drift Risks
1. New model in config without billing entry
2. Provider key rotation without doc update
3. Fallback changed without doc update
4. Duplicate prefix re-activated
5. -tools alias re-activated in DB

## Next Task
Implement special-unit billing in worker for audio/search/realtime/TTS.
