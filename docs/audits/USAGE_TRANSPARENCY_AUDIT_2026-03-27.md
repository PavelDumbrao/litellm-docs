# USAGE TRANSPARENCY AUDIT

Date: 2026-03-27. Scope: what customers and operators can currently see about usage and debits.

## 1. What Usage/Debit Information Is Currently Available to a Customer?

### Available (confirmed present)
- Credit balance (current balance visible in billing portal UI)
- Debit history: per-request ledger entries with timestamp, model name, debit amount in credits
- Model name used per request
- Approximate cost per request (in credits)

### NOT available (gaps)
- Raw token counts per request (input/output separately)
- Breakdown of why proxy-billed cost differs from simple token math
- Cumulative usage by model over time period
- Export/download of usage history
- Billing unit type label (customer cannot tell if model is `token` vs `audio_token` vs `search_token`)
- Explanation when a request costs more/less than a naive per-token calculation would suggest

## 2. What Usage/Debit Information Is Currently Available to an Operator?

### Available (confirmed present)
- LiteLLM spend logs: per-request StandardLoggingPayload (model, tokens, cost)
- billing.public_model_tariff: model name, billing_unit, rates, is_active
- billing.ledger (or equivalent): per-request debit records
- LiteLLM `/usage` endpoint (aggregated stats)
- Direct DB query access

### NOT available (gaps)
- Unified view of spend log + ledger in sync
- Per-model aggregated usage dashboard
- Discrepancy report (spend log cost vs actual debit cost)
- Real audio/search/realtime unit count (chars, audio seconds, search queries) — these are not in spend log metadata
- Explanation trail: why a proxy-billed request cost X credits

## 3. For Token-Billed Models — What Can Be Shown Clearly?

Token-billed models (billing_unit = 'token') are fully transparent:

| Data Point | Can Show? | Note |
|---|---|---|
| Input tokens | ✅ Yes | From LiteLLM spend log |
| Output tokens | ✅ Yes | From LiteLLM spend log |
| Cost per 1M tokens | ✅ Yes | From billing.public_model_tariff |
| Total debit = (input × input_rate) + (output × output_rate) | ✅ Yes | Deterministic math |
| Model name | ✅ Yes | Direct |

Customer can independently verify: cost = tokens × published rate. Zero ambiguity.

## 4. For Proxy-Billed Special-Unit Models — What Caveats Must Be Shown?

Proxy-billed models (billing_unit = audio_token / search_token / realtime_token / research_token) use token-count approximation because LiteLLM does not expose the native unit (audio seconds, search queries, realtime tokens) in the standard spend log.

### Required Caveats

| Caveat | Why |
|---|---|
| "Cost is approximated based on token count" | Native billing unit not available from LiteLLM spend log |
| "Actual cost may vary from simple token math" | Provider (OpenAI) bills these models differently |
| "Search requests include per-query overhead" | search_token models have a per-query cost component |
| "Audio/Realtime costs depend on duration, not just tokens" | Audio seconds ≠ token count |
| "This is a best-effort approximation" | No exact native unit metering available |

### What MUST NOT be claimed
- Exact audio seconds consumed
- Exact search queries counted
- Exact realtime session duration
- Cost matches OpenAI invoice exactly

## 5. Current Visibility Gaps by Layer

### Backend
- LiteLLM spend log seals before callbacks inject custom fields (confirmed blocker)
- No native audio/search/realtime unit in StandardLoggingPayload
- No per-request discrepancy log between spend log cost and actual debit

### API
- No public endpoint: `GET /usage/breakdown?model=X&period=Y`
- No endpoint: `GET /usage/model-type-explanation` (token vs proxy)
- LiteLLM `/usage` aggregates do not distinguish billing_unit types

### Frontend (billing portal)
- Model billing_unit not shown to customer (no label: "token" vs "proxy")
- No per-request cost explanation tooltip
- No caveat text for proxy-billed models in UI
- No token breakdown (input vs output) visible to customer

### Docs
- No customer-facing usage explanation doc
- No USAGE_DISPLAY_POLICY defining what is shown and what is caveat-only
- No source map explaining where usage data comes from

## Summary Table

| Layer | Token-Billed | Proxy-Billed | Gap Severity |
|---|---|---|---|
| Backend data | Full | Approximate only | Medium |
| API | Partial | Partial | High |
| Frontend labels | None | None | High |
| Customer explanation | None | None | Critical |
| Operator view | Good | Partial | Medium |
| Docs | None | None | High |
