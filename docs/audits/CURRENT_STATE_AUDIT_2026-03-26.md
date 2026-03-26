# CURRENT STATE AUDIT — LiteLLM Production

**Date:** 2026-03-26
**VPS:** 31.97.199.12 (Hostinger)
**Production URL:** https://api.proaicommunity.online

---

## BLOCK A — FACTUAL PRODUCTION STATE

### A.1 Services

| Container | Image | Port | Status | Traefik |
|---|---|---|---|---|
| litellm-xne6-litellm-1 | litellm:main-stable v1.82.0.patch5 | 32779:4000 | Up 2 days (healthy) | api.proaicommunity.online |
| litellm-xne6-litellm-db-1 | postgres:16.1-alpine | 5432 | Up 2 days (healthy) | internal |
| litellm-public-canary | litellm:main-stable v1.82.0.patch5 | 32789:4000 | Up 8 days | NO (testing) |
| litellm-public-only-canary | litellm:main-stable v1.82.0.patch5 | 32790:4000 | Up 8 days | NO (testing) |
| openwebui-litellm | open-webui:main | 3000:8080 | Up 2 days (healthy) | hub.proaicommunity.online |
| whisper-asr | openai-whisper-asr-webservice | 9000:9000 | Up 13 days | internal |

### A.2 Config.yaml — Model Inventory

~80 routes across multi-provider deployments.

Public models: gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.3-codex, gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 (+thinking variants), gemini-3-flash-preview (+nothinking/thinking), gemini-3.1-pro-preview (+high/low/medium), gemini-2.5-flash (+thinking/lite), deepseek-v3.2, gpt-4o-audio-preview, gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview, gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-mini-tts, gpt-5-search-api, gpt-audio, gpt-audio-mini, o4-mini-deep-research, tts-1, tts-hd-1, text-embedding-3-large/small/ada-002, i7dc-claude-haiku-4-5, i7dc-claude-sonnet-4-6, i7dc-claude-opus-4-6

Hidden -tools aliases (14): gpt-5.4-tools, gpt-5.4-mini-tools, gpt-5.4-nano-tools, gpt-4o-tools, gpt-4o-mini-tools, gpt-4.1-mini-tools, gpt-4.1-nano-tools, claude-haiku-4-5-tools, claude-sonnet-4-6-tools, claude-opus-4-6-tools, gemini-2.5-flash-tools, gemini-3-flash-tools, gemini-3.1-pro-preview-tools

### A.3 Provider Groups (13 keys)

| Key | Provider | Models |
|---|---|---|
| JENIYA_CODEX_API_KEY | jeniya.top | GPT-5.4, GPT-5.3-codex |
| JENIYA_GEMINI_API_KEY | jeniya.top | Gemini models |
| JENIYA_SKIDKA_API_KEY | jeniya.top | DeepSeek |
| JENIYA_DEFAULT_API_KEY | jeniya.top | GPT-5.4-mini, GPT-5.4-nano |
| JENIYA_AZ15_API_KEY | jeniya.top | Various fallback |
| POLO_CLAUDE_API_KEY | poloai.top | Claude models |
| POLO_CODEX_GPT_API_KEY | poloai.top | GPT-5.x fallback |
| POLO_AZ_API_KEY | poloai.top | GPT-4.1, audio/search/TTS |
| POLO_GEMINI_API_KEY | poloai.top | Gemini fallback |
| POLO_FASTGEMINI_API_KEY | poloai.top | Gemini 3/3.1 fast |
| ANIDEAAI_API_KEY | anideaai.com | Claude native |
| I7DC_API_KEY | i7dc.com | I7DC relay |

### A.4 Fallback Chains (30+ groups configured)

Key: gpt-5.4->gpt-4o->gpt-4o-mini, gpt-5.4-mini->gpt-4o-mini->gpt-4.1-mini, gpt-5.4-nano->gpt-4.1-nano->gpt-4o-mini, claude-opus->claude-sonnet->claude-haiku, claude-sonnet->claude-haiku->gpt-4o, gemini-3.1-pro->gemini-3-flash->gemini-2.5-flash, deepseek->gpt-4o->gpt-4o-mini, all -tools -> base model

### A.5 Callbacks

- JsonHealingV1Handler — JSON response healing
- ToolsRoutingHandler — Auto-Tools Router for -tools aliases

### A.6 Routing Settings

simple-shuffle, 2 retries, 300s request timeout, 60s router timeout, 3 allowed fails, 30s cooldown, pre_call_checks enabled

### A.7 Drift Risks

1. Shared DB: prod and canary use same litellm-db
2. Key naming drift: canary uses POLOAI_GROUP2 vs prod POLO_CLAUDE
3. No traefik on canary: not externally routable but shares DB writes
4. Config drift: canary may have different model_list from prod

---

## BLOCK B — DOC SOURCE OF TRUTH AUDIT

| # | Doc | Status | Matches Prod? | Action |
|---|---|---|---|---|
| 1 | PRICING_AUDIT.md | outdated | NO — pre-seed, missing 25 models | Rewrite |
| 2 | PRICING_VERIFICATION.md | outdated | NO — date 2026-03-17 | Rewrite |
| 3 | PUBLIC_ALIAS_MAP.md | outdated | NO — 20+ models missing | Rebuild from config.yaml |
| 4 | BACKEND_MODEL_MATRIX.md | outdated | NO — missing gemini-3, audio/search/TTS | Rebuild from config.yaml |
| 5 | MODEL_AUDIT_MASTER.md | outdated | NO — pre-March 20 data | Re-run audit |
| 6 | PUBLIC_MODEL_CATALOG_FINAL | outdated | NO — 25 seeded models missing | Update with DB data |
| 7 | MVP_SOURCE_OF_TRUTH | partial | PARTIALLY — architecture OK, details outdated | Update model/provider lists |
| 8 | PROJECT_MASTER_README | accurate | YES — architecture correct | Keep |
| 9 | BACKEND_APIKEY_GROUP_MAP.md | outdated | NO — missing I7DC, ANIDEAAI | Rebuild from config |
| 10 | BACKEND_FALLBACK_MATRIX.md | outdated | NO — chains differ from config | Re-extract from config |

Trustworthy source of truth right now: 0 of 10 priority docs fully current.

---

## BLOCK C — CANONICAL DOCUMENT SET

| Role | Doc | Status | Action |
|---|---|---|---|
| Master entrypoint | canonical-pack/PROJECT_MASTER_README.md | accurate | Keep |
| MVP source of truth | mvp-pack/MVP_SOURCE_OF_TRUTH.md | partial | Update model list |
| Public model catalog | mvp-pack/PUBLIC_MODEL_CATALOG_FINAL.md | outdated | Must add 25 models |
| Pricing source | billing.public_model_tariff (DB) | live | Doc should reference DB |
| Alias mapping | docs/PUBLIC_ALIAS_MAP.md | outdated | Rebuild from config |
| Routing/fallback | config.yaml (live) | live | Doc should document config |
| Operator guide | canonical-pack/AI_OPERATOR_GUIDE.md | accurate | Keep |

Needs creating: CURRENT_MODEL_INVENTORY.md (auto from config.yaml)

---

## BLOCK D — REMEDIATION PLAN

### P0 — CRITICAL

| File | Reason | Change |
|---|---|---|
| PUBLIC_ALIAS_MAP.md | 20+ models missing | Rebuild from config.yaml model_list |
| BACKEND_MODEL_MATRIX.md | Missing entire model families | Re-extract from config.yaml |
| PUBLIC_MODEL_CATALOG_FINAL.md | 25 models not in catalog | Add from billing.public_model_tariff |
| Billing DB sync check | Verify DB matches config | Compare DB vs config.yaml names |

### P1 — SOON (1 week)

| File | Reason | Change |
|---|---|---|
| PRICING_AUDIT.md | Pre-normalization | Rewrite, reference billing DB |
| PRICING_VERIFICATION.md | Date 2026-03-17 | Rewrite with current DB snapshot |
| MODEL_AUDIT_MASTER.md | Pre-March 20 data | Re-run with current config |
| BACKEND_APIKEY_GROUP_MAP.md | Missing I7DC, ANIDEAAI | Rebuild from config env vars |
| BACKEND_FALLBACK_MATRIX.md | Chains differ from config | Re-extract from config.yaml |
| MVP_SOURCE_OF_TRUTH.md | Model/provider lists outdated | Update to match prod |

### P2 — ARCHIVE

| File | Reason |
|---|---|
| FINAL_PUBLIC_CATALOG.md | Superseded |
| FALLBACK_PLAN_PROPOSAL.md | gpt-5-low unused |
| JENIYA_UNIVERSAL_MODELS_FULL.md | 187 models, outdated |
| HIDE_PLAN.md | Implemented |
| HIDE_IMPLEMENTATION_DECISION.md | Implemented |
| ROLL_OUT_CRITERIA.md | Completed |
| ROLLOUT_READPACK.md | Completed |
| CHATGPT_READPACK.md | Completed |
| LITELLM_STAGE2_PLAN.md | Verify then archive |
| JENIYA_UNIVERSAL_CURATED_SHORTLIST.md | Verify then archive |

---

## VERDICT

### Source of Truth

- **config.yaml** = ONLY reliable source for routing, models, fallbacks, providers
- **billing.public_model_tariff** = ONLY reliable source for customer pricing
- All docs are secondary and must match these two live sources

### Top 5 Doc Drifts

1. PUBLIC_ALIAS_MAP.md — 20+ models missing
2. PUBLIC_MODEL_CATALOG_FINAL.md — 25 seeded models not in catalog
3. PRICING_AUDIT.md — written before normalization
4. BACKEND_MODEL_MATRIX.md — missing gemini-3, audio/search/TTS
5. MODEL_AUDIT_MASTER.md — pre-March 20 audit data

### Top 5 Operational Risks

1. Shared DB between prod and canary — corruption risk
2. Canary key naming drift (POLOAI vs POLO_CLAUDE)
3. No separate DB for canary testing
4. 56 docs with only ~20% accurate = confusion risk
5. Pricing docs don't reference billing DB as source

### Minimal Doc Set to Trust

1. config.yaml (live)
2. billing.public_model_tariff (live DB)
3. canonical-pack/PROJECT_MASTER_README.md
4. canonical-pack/AI_OPERATOR_GUIDE.md
