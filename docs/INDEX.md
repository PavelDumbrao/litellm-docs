# LiteLLM Documentation — Entry Point

**Date:** 2026-03-26
**Purpose:** One obvious entry point for any person, agent, or chat.

---

## Start Here

1. Read [current/CURRENT_SOURCE_OF_TRUTH.md](current/CURRENT_SOURCE_OF_TRUTH.md) — what to trust, what to ignore
2. Read [current/LIVE_DOC_INDEX.md](current/LIVE_DOC_INDEX.md) — full navigation guide

## Current Canonical Docs (TRUST THESE)

| Doc | What It Covers |
|---|---|
| [CURRENT_SOURCE_OF_TRUTH.md](current/CURRENT_SOURCE_OF_TRUTH.md) | What is truth, what to trust, verification checklist |
| [LIVE_PUBLIC_MODEL_CATALOG.md](current/LIVE_PUBLIC_MODEL_CATALOG.md) | All customer-facing models by group |
| [LIVE_PUBLIC_ALIAS_MAP.md](current/LIVE_PUBLIC_ALIAS_MAP.md) | Public alias to internal route mapping |
| [LIVE_PRICING_REFERENCE.md](current/LIVE_PRICING_REFERENCE.md) | Retail prices ($/1M) for all models |
| [LIVE_ROUTING_AND_FALLBACK_REFERENCE.md](current/LIVE_ROUTING_AND_FALLBACK_REFERENCE.md) | Routing, providers, fallback chains |

## Audits

| Audit | Date |
|---|---|
| [CURRENT_STATE_AUDIT_2026-03-26.md](audits/CURRENT_STATE_AUDIT_2026-03-26.md) | Full factual production state audit |

## Legacy Docs

Legacy docs live on VPS at /docker/litellm-xne6/docs/. Most are outdated. See CURRENT_SOURCE_OF_TRUTH.md for which legacy docs to trust and which to ignore.

## Live Sources of Truth

These override any doc:
1. config.yaml — all routing, models, fallbacks, providers (on VPS)
2. billing.public_model_tariff — all customer pricing (in PostgreSQL)
3. custom_callbacks.py — JSON healing, tools routing (on VPS)