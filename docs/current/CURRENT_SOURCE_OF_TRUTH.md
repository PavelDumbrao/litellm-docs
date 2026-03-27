# CURRENT SOURCE OF TRUTH

**Date audited:** 2026-03-26
**Purpose:** Tell any new person, chat, or agent what to trust and what to ignore.

---

## Live Sources of Truth (TRUST THESE)

| Source | What It Controls | Where |
|---|---|---|
| config.yaml | All routing, models, fallbacks, providers, callbacks | /docker/litellm-xne6/config.yaml |
| billing.public_model_tariff | All customer-facing pricing (credits/token) | PostgreSQL (n8n-postgres / railway) |
| custom_callbacks.py | JSON healing, tools routing logic | /docker/litellm-xne6/custom_callbacks.py |
| Docker containers | Actual running state | docker ps |

**Rule:** If a doc contradicts config.yaml or billing DB, the doc is wrong.

---

## Trustworthy Docs (KEEP THESE)

| Doc | Why Trust It |
|---|---|
| canonical-pack/PROJECT_MASTER_README.md | Architecture overview, still accurate |
| canonical-pack/AI_OPERATOR_GUIDE.md | Operational guide, still accurate |
| canonical-pack/DIAGNOSTICS_AND_HEALTH_GUIDE.md | Health check procedures, still valid |
| JSON_HEALING_V1.md | Callback documentation, callback still active |
| JSON_HEALING_LIMITATIONS.md | Known limitations, still accurate |
| JSON_HEALING_TEST_MATRIX.md | Test cases, still valid |
| MODEL_DUPLICATE_CLUSTERS.md | Duplicate analysis, still relevant |
| PER_USER_USAGE_TRACKING.md | Billing architecture, still accurate |
| USAGE_TRACKING_SCHEME.md | Tracking approach, still accurate |

---

## Historical Only (DO NOT USE AS SOURCE)

These docs describe past decisions or completed rollouts:

ROLLOUT_READPACK.md, ROLL_OUT_CRITERIA.md, CHATGPT_READPACK.md, HIDE_PLAN.md, HIDE_IMPLEMENTATION_DECISION.md, CANARY_CHECKLIST.md, CLAUDE_POLOAPI_*.md, FALLBACK_PLAN_PROPOSAL.md, PHASE1_SUCCESS_SUMMARY.md, DOC_SYNC_AUDIT.md, PUBLIC_ALIAS_BLOCKER_CANARY_REPORT.md, implementation_plan.md

---

## Outdated (KNOWN BROKEN — DO NOT TRUST)

| Doc | Why Broken |
|---|---|
| PRICING_AUDIT.md | Before normalization, missing 25 models |
| PRICING_VERIFICATION.md | Date 2026-03-17, outdated |
| PUBLIC_ALIAS_MAP.md | Missing 20+ models |
| BACKEND_MODEL_MATRIX.md | Missing gemini-3, audio/search/TTS, I7DC |
| MODEL_AUDIT_MASTER.md | Pre-March-20 data |
| PUBLIC_MODEL_CATALOG_FINAL.md | Missing 25 seeded models |
| BACKEND_APIKEY_GROUP_MAP.md | Missing I7DC, ANIDEAAI |
| BACKEND_FALLBACK_MATRIX.md | Chains differ from config |
| FINAL_PUBLIC_CATALOG.md | Superseded |
| JENIYA_UNIVERSAL_MODELS_FULL.md | 187 models, outdated |
| LITELLM_STAGE2_PLAN.md | May be completed |

---

## How to Verify Anything

1. Is this model real? -> Check config.yaml model_list
2. What does it cost? -> Check billing.public_model_tariff
3. What is its fallback? -> Check config.yaml litellm_settings.fallbacks
4. Is it hidden? -> Check config.yaml model_info.hide
5. Which provider? -> Check config.yaml litellm_params.api_base
6. Is it active? -> Check billing.public_model_tariff.is_active

---

## Special-Unit Billing Note

Some special-unit billing paths (chars_token, audio_token, etc.) exist in worker code but are NOT trusted for public billing until live-validated. Currently, chars_token path is INERT — LiteLLM spend logs do not contain character counts, so worker always falls back to token proxy.

## For New People / New Chats / New Agents

1. Read this file
2. Read LIVE_DOC_INDEX.md
3. Trust config.yaml and billing DB above all docs
4. Ignore any doc in Outdated or Historical Only lists
