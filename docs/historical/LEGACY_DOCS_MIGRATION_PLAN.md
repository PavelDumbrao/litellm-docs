# LEGACY DOCS MIGRATION PLAN

**Date:** 2026-03-26
**Source:** VPS /docker/litellm-xne6/docs/ (56 .md files)
**Note:** This plan does NOT move VPS files. It classifies them for future action.

---

## Bucket 1 — HISTORICAL ONLY (leave on VPS, do not migrate)

Past decisions or completed rollouts. Useful as history only.

ROLLOUT_READPACK.md, ROLL_OUT_CRITERIA.md, CHATGPT_READPACK.md, HIDE_PLAN.md, HIDE_IMPLEMENTATION_DECISION.md, CANARY_CHECKLIST.md, CLAUDE_POLOAPI_*.md (4 files), FALLBACK_PLAN_PROPOSAL.md, PHASE1_SUCCESS_SUMMARY.md, DOC_SYNC_AUDIT.md, PUBLIC_ALIAS_BLOCKER_CANARY_REPORT.md, implementation_plan.md, ADMIN_ANALYTICS_AUDIT.md, BACKEND_CHANGE_DIFF.md, BACKEND_TEST_EVIDENCE.md, JSON_HEALING_CHANGE_DIFF.md, JSON_HEALING_TEST_RESULTS.md, USER_TRACKING_DECISION.md, USER_UI_SCOPE.md, SPEND_TRACKING_CHECK.md, COOLDOWN_POLICY.md, BACKEND_TIMEOUT_POLICY.md

Action: Leave on VPS. Mark historical if moved to Git later.

---

## Bucket 2 — SUPERSEDED (replaced by docs/current/*)

| Legacy Doc | Superseded By |
|---|---|
| PRICING_AUDIT.md | LIVE_PRICING_REFERENCE.md |
| PRICING_VERIFICATION.md | LIVE_PRICING_REFERENCE.md |
| PUBLIC_ALIAS_MAP.md | LIVE_PUBLIC_ALIAS_MAP.md |
| BACKEND_MODEL_MATRIX.md | LIVE_PUBLIC_MODEL_CATALOG.md |
| MODEL_AUDIT_MASTER.md | LIVE_PUBLIC_MODEL_CATALOG.md |
| FINAL_PUBLIC_CATALOG.md | LIVE_PUBLIC_MODEL_CATALOG.md |
| PUBLIC_MODEL_CATALOG_FINAL.md | LIVE_PUBLIC_MODEL_CATALOG.md |
| BACKEND_APIKEY_GROUP_MAP.md | LIVE_ROUTING_AND_FALLBACK_REFERENCE.md |
| BACKEND_FALLBACK_MATRIX.md | LIVE_ROUTING_AND_FALLBACK_REFERENCE.md |
| ROUTING_POLICY.md | LIVE_ROUTING_AND_FALLBACK_REFERENCE.md |
| BACKEND_TYPE_GROUPS.md | LIVE_PUBLIC_MODEL_CATALOG.md |
| FALLBACK_POLICY_FINAL.md | LIVE_ROUTING_AND_FALLBACK_REFERENCE.md |

Action: Do NOT migrate. If needed for reference, copy to docs/historical/ with superseded header.

---

## Bucket 3 — MIGRATE LATER IF STILL USEFUL

| Legacy Doc | Why Useful | Action |
|---|---|---|
| MODEL_DUPLICATE_CLUSTERS.md | Duplicate analysis still relevant | Review, migrate after verification |
| PER_USER_USAGE_TRACKING.md | Billing architecture, accurate | Already trusted |
| USAGE_TRACKING_SCHEME.md | Tracking approach, accurate | Already trusted |
| USER_ACCESS_MODEL.md | Access model | Review, migrate if accurate |
| JSON_HEALING_V1.md | Callback docs, active | Already trusted |
| JSON_HEALING_LIMITATIONS.md | Known limitations, accurate | Already trusted |
| JSON_HEALING_TEST_MATRIX.md | Test cases, valid | Already trusted |
| JENIYA_UNIVERSAL_CURATED_SHORTLIST.md | Stage 2 list | Verify Stage 2 status |
| LITELLM_STAGE2_PLAN.md | Stage 2 plan | Verify completion |
| MVP_SOURCE_OF_TRUTH.md | Architecture | Review, update if migrating |
| PROJECT_MASTER_README.md | Architecture overview | Already trusted |
| AI_OPERATOR_GUIDE.md | Operational guide | Already trusted |
| DIAGNOSTICS_AND_HEALTH_GUIDE.md | Health checks | Already trusted |

Action: Review individually. Migrate only after accuracy confirmation.

---

## Summary

| Bucket | Count | Action |
|---|---|---|
| Historical only | ~25 | Leave on VPS |
| Superseded | ~12 | Do NOT migrate |
| Migrate later | ~13 | Review individually |
| Already trusted | 9 | No action |

## What NOT To Do
1. Do NOT bulk-move all legacy docs to Git
2. Do NOT create new "final" versions of outdated docs
3. Do NOT delete legacy docs from VPS
4. Do NOT use legacy docs as source of truth without re-verification

## What TO Do
1. Use docs/current/* as primary reference
2. Re-verify legacy against config.yaml + billing DB before using
3. Migrate individual docs only after accuracy confirmation
4. Add "Migrated from VPS on [date]" header when migrating