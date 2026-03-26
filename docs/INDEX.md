# LiteLLM Documentation — Entry Point

**Date:** 2026-03-26
**Purpose:** One obvious entry point for any person, agent, or chat.

---

## Start Here

1. Read [current/CURRENT_SOURCE_OF_TRUTH.md](current/CURRENT_SOURCE_OF_TRUTH.md) — what to trust, what to ignore
2. Read [current/LIVE_DOC_INDEX.md](current/LIVE_DOC_INDEX.md) — full navigation guide

---

## Current Canonical Docs (TRUST THESE)

Synced with live production. If a doc contradicts config.yaml or billing DB, the doc is wrong.

| Doc | What It Covers |
|---|---|
| [CURRENT_SOURCE_OF_TRUTH.md](current/CURRENT_SOURCE_OF_TRUTH.md) | Truth definition, verification checklist, trustworthy vs outdated |
| [LIVE_PUBLIC_MODEL_CATALOG.md](current/LIVE_PUBLIC_MODEL_CATALOG.md) | Customer-facing models by group, hidden aliases excluded |
| [LIVE_PUBLIC_ALIAS_MAP.md](current/LIVE_PUBLIC_ALIAS_MAP.md) | Public alias to internal route/fallback mapping |
| [LIVE_PRICING_REFERENCE.md](current/LIVE_PRICING_REFERENCE.md) | Retail prices ($/1M), safe vs proxy-billed |
| [LIVE_ROUTING_AND_FALLBACK_REFERENCE.md](current/LIVE_ROUTING_AND_FALLBACK_REFERENCE.md) | Provider groups, fallback chains, callbacks |

---

## Audits

| Audit | Date |
|---|---|
| [CURRENT_STATE_AUDIT_2026-03-26.md](audits/CURRENT_STATE_AUDIT_2026-03-26.md) | Full factual production state |
| [GIT_CANONICALIZATION_REPORT_2026-03-26.md](audits/GIT_CANONICALIZATION_REPORT_2026-03-26.md) | What was transferred to Git |

---

## Legacy / Historical

| Plan | Purpose |
|---|---|
| [LEGACY_DOCS_MIGRATION_PLAN.md](historical/LEGACY_DOCS_MIGRATION_PLAN.md) | Which legacy docs to archive, migrate, or ignore |

Legacy docs on VPS (/docker/litellm-xne6/docs/) are largely outdated. Do NOT use without re-verification.

---

## Live Sources of Truth

These override ANY doc:

1. config.yaml on VPS — all routing, models, fallbacks, providers
2. billing.public_model_tariff in PostgreSQL — all customer pricing
3. custom_callbacks.py on VPS — JSON healing, tools routing

Rule: if a doc contradicts these three, the doc is wrong.