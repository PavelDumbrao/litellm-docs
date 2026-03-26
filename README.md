# litellm-docs

Canonical documentation for ProAICommunity LiteLLM production router.

**Entry point:** [docs/INDEX.md](docs/INDEX.md)

---

**WARNING:** Legacy docs on VPS (`/docker/litellm-xne6/docs/`) are largely outdated. Do NOT use them as source of truth unless explicitly re-verified against `config.yaml` and `billing.public_model_tariff`. Always prefer `docs/current/*` in this repo.

---

## What This Repo Contains

- `docs/current/` — canonical docs synced with live production
- `docs/audits/` — factual production state audits
- `docs/historical/` — legacy migration plan

## Live Sources of Truth (override all docs)

1. config.yaml on VPS — routing, models, fallbacks, providers
2. billing.public_model_tariff in PostgreSQL — customer pricing
3. custom_callbacks.py on VPS — JSON healing, tools routing

## Date Created

2026-03-26