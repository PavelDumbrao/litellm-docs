# USAGE TRANSPARENCY SOURCE MAP

Date: 2026-03-27. Maps all current data sources for usage and debit transparency.

## Source 1: LiteLLM Spend Log (StandardLoggingPayload)

**What it is:** Per-request log entry written by LiteLLM proxy at request completion.

| Field | Authoritative For | NOT Authoritative For |
|---|---|---|
| `model` | Which model alias was used | Internal route (provider model) |
| `prompt_tokens` | Input token count | Audio seconds, search queries |
| `completion_tokens` | Output token count | Native special-unit count |
| `response_cost` | LiteLLM's own cost estimate | Our actual debit (different rate) |
| `user` | Requesting user identifier | Customer account balance |
| `startTime` / `endTime` | Request timing | — |

**For customer:** Not directly exposed. Used as source for ledger debit calculation.
**For operator:** Available via LiteLLM `/usage` endpoint and direct DB query.

**Critical limitation:** Spend log is sealed before async_pre_call_hook callbacks fire.
Custom fields (e.g. native audio units) cannot be injected retroactively.

---

## Source 2: billing.public_model_tariff

**What it is:** Canonical pricing table in PostgreSQL. Source of truth for rates.

| Field | Authoritative For | NOT Authoritative For |
|---|---|---|
| `public_model_name` | Public-facing model name | Internal LiteLLM model alias |
| `billing_unit` | How this model is billed | What the customer actually consumed |
| `input_rate_credits` | Input credit rate | Whether billing is exact or approximate |
| `output_rate_credits` | Output credit rate | Same |
| `is_active` | Whether model is active in catalog | Whether it is routable in config.yaml |

**For customer:** Rates shown as $/1M in public catalog. billing_unit NOT currently shown.
**For operator:** Direct source for debit calculation. Full access.

---

## Source 3: Billing Ledger (per-request debit records)

**What it is:** Per-request debit entries created by billing-portal at request completion.

| Field | Authoritative For | NOT Authoritative For |
|---|---|---|
| Debit amount (credits) | What was charged for this request | Why it cost that amount |
| Timestamp | When request was processed | — |
| Model name | Which model was used | Billing unit type |
| User/account | Which account was debited | Token breakdown |

**For customer:** Debit history list is shown (amount + model + timestamp). No token detail.
**For operator:** Full ledger access via DB.

**Gap:** Ledger entry does not store: input_tokens, output_tokens, billing_unit label.
Once written, the debit is a black box to the customer — no explanation attached.

---

## Source 4: LiteLLM /usage Endpoint

**What it is:** Aggregated usage stats endpoint provided by LiteLLM proxy.

| Field | Authoritative For | NOT Authoritative For |
|---|---|---|
| Total spend (LiteLLM estimate) | LiteLLM's own cost accounting | Our billing (different rates) |
| Per-model breakdown | Model usage volume | billing_unit type |
| Per-user breakdown | User traffic distribution | Customer balance |

**For customer:** Not exposed. Internal operator tool only.
**For operator:** Useful for traffic analysis. NOT aligned with actual debit amounts.

**Gap:** `/usage` uses LiteLLM's own rates, not our billing.public_model_tariff rates.
Numbers will differ. Operators must not show `/usage` output directly to customers.

---

## Source 5: billing.public_model_tariff (is_active flag)

**What it is:** Single source of truth for what is active in public surface.

**For customer:** Determines which models appear in catalog.
**For operator:** Controlled by PublicSurfaceGuard automated checks.

---

## Source Map Summary

| Source | Customer-Facing? | Operator-Facing? | Exact? |
|---|---|---|---|
| LiteLLM Spend Log | No | Yes | Partial (no native units) |
| billing.public_model_tariff | Rates only | Full | Yes (for rates) |
| Billing Ledger | Debit amount only | Full | Yes (for debits) |
| LiteLLM /usage endpoint | No | Yes | No (different rates) |
| PublicSurfaceGuard output | No | Yes | Yes (for catalog state) |

## What Each Audience Should See

### Customer should see:
1. Model name (from ledger)
2. Debit amount in credits (from ledger)
3. Timestamp (from ledger)
4. Published rate in $/1M (from billing.public_model_tariff)
5. Billing type label: "Standard" (token) or "Estimated" (proxy)
6. Caveat text for proxy-billed models (static doc)

### Customer should NOT see:
1. LiteLLM /usage data (wrong rates)
2. Internal model route (provider model name)
3. Spend log response_cost (LiteLLM estimate, not our rate)
4. Raw billing_unit enum value

### Operator should see:
1. Everything customer sees
2. billing_unit type per model
3. input_tokens + output_tokens per request (from spend log)
4. Spend log cost vs ledger debit comparison
5. is_active status and PublicSurfaceGuard verdict
6. Real traffic volume by model and billing_unit
