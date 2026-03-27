# LIVE DOC INDEX

Date: 2026-03-26. Navigation for new people/chats/agents.

## What This Is
Canonical doc set synced with live production. Legacy docs are largely outdated.

## Read In This Order
1. CURRENT_SOURCE_OF_TRUTH.md — what to trust, what to ignore
2. LIVE_PUBLIC_MODEL_CATALOG.md — all customer-facing models
3. LIVE_PUBLIC_ALIAS_MAP.md — public alias -> internal route mapping (summary)
3b. LIVE_PUBLIC_ALIAS_MAP_EXPANDED.md — detailed mapping with providers, fallbacks, pricing
4. LIVE_PRICING_REFERENCE.md — retail prices ($/1M)
5. LIVE_ROUTING_AND_FALLBACK_REFERENCE.md — routing, providers, fallbacks
6. SPECIAL_UNIT_MODEL_MATRIX.md — billing categories for all special-unit models (audio, search, realtime, research)
7. SPECIAL_UNIT_OPERATING_POLICY.md — operating policy for all 11 proxy-billed public models (ACCEPTED_PROXY / REVIEW_LATER, removed TTS)
8. PUBLIC_SURFACE_GUARD.md — repeatable drift-check layer: 8 checks, baseline 41/30/11, PASS/FAIL, deploy instructions
9. USAGE_TRANSPARENCY_SOURCE_MAP.md — maps all usage/debit data sources (spend log, ledger, tariff, /usage) per audience
10. USAGE_DISPLAY_POLICY.md — customer-facing display rules: Standard vs Estimated labels, caveat policy, wording principles
11. OPERATOR_TROUBLESHOOTING_SOURCE_MAP.md — operator-only source-of-truth chain for debit inspection
12. OPERATOR_UI_IMPLEMENTATION_2026-03-27.md — internal operator UI flow on top of usage rows and operator endpoint

## Source of Truth Hierarchy
1. config.yaml (live) — routing, models, fallbacks, providers
2. billing.public_model_tariff (live DB) — pricing
3. custom_callbacks.py (live) — JSON healing, tools routing
4. These docs — derived from above

## Trustworthy Legacy Docs
PROJECT_MASTER_README.md, AI_OPERATOR_GUIDE.md, DIAGNOSTICS_AND_HEALTH_GUIDE.md, JSON_HEALING_V1.md, JSON_HEALING_LIMITATIONS.md, JSON_HEALING_TEST_MATRIX.md, MODEL_DUPLICATE_CLUSTERS.md, PER_USER_USAGE_TRACKING.md, USAGE_TRACKING_SCHEME.md

## Historical Only (not source)
ROLLOUT_READPACK.md, ROLL_OUT_CRITERIA.md, CHATGPT_READPACK.md, HIDE_PLAN.md, CANARY_CHECKLIST.md, CLAUDE_POLOAPI_*.md, FALLBACK_PLAN_PROPOSAL.md, PHASE1_SUCCESS_SUMMARY.md

## Outdated (broken — do not trust)
PRICING_AUDIT.md, PRICING_VERIFICATION.md, PUBLIC_ALIAS_MAP.md, BACKEND_MODEL_MATRIX.md, MODEL_AUDIT_MASTER.md, PUBLIC_MODEL_CATALOG_FINAL.md, BACKEND_APIKEY_GROUP_MAP.md, BACKEND_FALLBACK_MATRIX.md, FINAL_PUBLIC_CATALOG.md, JENIYA_UNIVERSAL_MODELS_FULL.md

## Verify Anything
Model exists? -> config.yaml model_list | Cost? -> billing.public_model_tariff | Fallback? -> config.yaml litellm_settings.fallbacks | Hidden? -> config.yaml model_info.hide | Provider? -> config.yaml litellm_params.api_base | Active? -> billing.public_model_tariff.is_active

## For New People
Start here. Trust config.yaml + billing DB. These 6 files are your safe starting point.
