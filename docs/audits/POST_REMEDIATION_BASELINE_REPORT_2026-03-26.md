# POST REMEDIATION BASELINE REPORT

Date: 2026-03-26

## Current Baseline (post tts-1 removal)
Active billing rows: 43. Public models: ~31. Proxy-billed: 13. Hidden -tools: 14 (inactive). Providers: 13. Alignment: ALIGNED.

## Trusted Surface
config.yaml + billing.public_model_tariff + custom_callbacks.py. docs/current/ = canonical layer. Git = PavelDumbrao/litellm-docs.

## Known Limitations
1. Proxy-billed models use token proxy — not fully accurate per actual unit
2. Worker has chars_token branch but chars metadata not in spend logs — billing inert
3. I7DC not in billing DB — separate provider
4. tts-1 removed from public surface (inert billing, legacy model)

## Top 5 Drift Risks
1. New model in config without billing entry
2. Provider key rotation without doc update
3. Fallback changed without doc update
4. Duplicate prefix re-activated
5. -tools alias re-activated in DB

## Next Task
Either patch LiteLLM upstream to expose char counts, or use input text length as char proxy in worker.
