# LIVE ALIAS MAP BUILD REPORT

Date: 2026-03-26

## Live Sources Used
- config.yaml model_list (~80 routes)
- config.yaml litellm_settings.fallbacks (30+ chains)
- config.yaml router_settings.model_group_alias
- billing.public_model_tariff (66 rows)

## Public Models Mapped
GPT-5.x: 4 models. GPT-4.x: 5 models. Claude: 3 base + 4 thinking. Gemini: 5 base + 3 thinking. Other: 1 (deepseek). Special-unit: 14. Embeddings: 3. I7DC: 3. Hidden -tools: 14 (excluded). Total public: ~32 unique.

## Billing DB vs Routing Mismatch
All 25 seeded models have matching routes in config.yaml. All routed public models have pricing in billing DB. No mismatches.

## Verdict
Alias map complete. All public models have providers, fallbacks, pricing, exact-name flags.
