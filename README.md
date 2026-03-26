# litellm-docs

Canonical documentation for ProAICommunity LiteLLM production router.

**Entry point:** [docs/INDEX.md](docs/INDEX.md)

## What This Repo Contains

- `docs/current/` — canonical docs synced with live production (config.yaml + billing DB)
- `docs/audits/` — factual production state audits
- `docs/historical/` — legacy docs marked as historical

## Live Sources of Truth (override all docs)

1. config.yaml on VPS — routing, models, fallbacks, providers
2. billing.public_model_tariff in PostgreSQL — customer pricing
3. custom_callbacks.py on VPS — JSON healing, tools routing

## Date Created

2026-03-26