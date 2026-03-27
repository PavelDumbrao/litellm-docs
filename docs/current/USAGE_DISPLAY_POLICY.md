# USAGE DISPLAY POLICY

Date: 2026-03-27. Defines what is shown to customers, what is hidden, and how to explain usage.

## Scope

This policy applies to all customer-facing usage display in the billing portal.
It is binding for frontend, API, and documentation decisions.

---

## 1. Fields We Show to Customers

| Field | Source | Display Format |
|---|---|---|
| Model name | Billing ledger | Public alias (e.g. `gpt-4o-audio-preview`) |
| Debit amount | Billing ledger | Credits (e.g. `0.0042 credits`) |
| Timestamp | Billing ledger | ISO date + time, user's timezone |
| Published rate | billing.public_model_tariff | $/1M input / $/1M output |
| Billing type label | billing.public_model_tariff.billing_unit | "Standard" or "Estimated" (see below) |
| Caveat text | Static (this policy) | Per model category (see below) |

---

## 2. Fields We Do NOT Show to Customers

| Field | Reason |
|---|---|
| Internal model route (e.g. `openai/gpt-4o-audio-preview`) | Internal routing detail, not customer concern |
| LiteLLM response_cost | LiteLLM uses different rates — misleading |
| Raw billing_unit enum (audio_token, search_token...) | Technical, replace with human label |
| Provider API key group | Internal infra detail |
| Fallback chain used | Internal routing detail |
| Spend log metadata | Raw internal telemetry |
| Other customers' usage | Privacy |

---

## 3. How We Explain Token-Billed Usage

**Label:** "Standard"

**Display template:**
```
Model: {model_name}
Type: Standard billing
Input: {input_tokens} tokens × ${input_rate}/1M = ${input_cost}
Output: {output_tokens} tokens × ${output_rate}/1M = ${output_cost}
Total: {total_cost} credits
```

**Rules:**
- Show input and output tokens separately when available
- Show cost per token at published rate
- Customer can independently verify the math
- No caveats needed — billing is exact

**Current state:** Input/output token breakdown not yet shown (gap). Show total debit only until fixed.

---

## 4. How We Explain Proxy-Billed Usage

**Label:** "Estimated"

**Display template:**
```
Model: {model_name}
Type: Estimated billing (special model)
Approximate cost: {total_cost} credits
Note: Cost is estimated based on token approximation.
      Actual usage units for this model type are not
      directly measurable by our platform.
```

**Mandatory caveat text (verbatim or equivalent):**
> This model uses a special billing method. Your cost is calculated using a token-based approximation of the actual usage. The exact amount may differ slightly from what you would see in a direct provider invoice.

**Rules:**
- ALWAYS show the "Estimated" label for proxy-billed models
- ALWAYS show caveat text on first occurrence or on hover/expand
- NEVER claim exact audio seconds, search queries, or realtime duration
- NEVER show a breakdown implying precision (e.g. "3.2 audio seconds")
- SHOULD link to a help doc explaining proxy billing

**Per-category caveat addendum:**

| Category | Additional note |
|---|---|
| Audio (gpt-4o-audio-preview, gpt-audio, gpt-audio-mini, gpt-4o-transcribe, gpt-4o-mini-transcribe) | "Audio processing costs are based on transcript token volume." |
| Search (gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-5-search-api) | "Search requests include a query overhead in addition to response tokens." |
| Realtime (gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview) | "Realtime session costs include connection and streaming overhead." |
| Research (o4-mini-deep-research) | "Deep research tasks may run multiple internal steps; cost reflects total processing." |

---

## 5. Wording Principles

### No Fake Precision
- DO NOT show `0.002341 audio seconds` — we don't measure this
- DO NOT show `1 search query` — we don't count this
- DO show `0.0042 credits` — this IS what was charged

### Clear Caveat Where Approximation Exists
- Every proxy-billed transaction MUST have a visible indicator that billing is estimated
- The indicator must not require user action to appear (not hidden in a tooltip only)
- Minimum: a label "Estimated" next to the cost
- Better: an expandable explanation
- Best: a link to a help article

### No Technical Jargon in Customer UI
- NOT: `billing_unit: audio_token`
- YES: `Billing type: Estimated (Audio model)`

### Rates Are Always Published
- Customer can always see the published rate ($/1M) for any model they used
- Rates come from billing.public_model_tariff only — no other source

---

## 6. Edge Cases

| Case | Policy |
|---|---|
| Model was removed but customer used it before | Show historical ledger entry as-is. Add note: "This model has been retired." |
| Customer disputes proxy-billed amount | Direct to operator. Operator can view spend log to reconstruct. |
| Debit is 0 (minimum charge applied) | Show actual debit. Note: "Minimum request charge applied." |
| Multiple models in one request (future) | Itemize per model. Apply respective billing type label. |

---

## Related Docs

- `USAGE_TRANSPARENCY_SOURCE_MAP.md` — where data comes from
- `SPECIAL_UNIT_OPERATING_POLICY.md` — proxy-billed model policy
- `LIVE_PRICING_REFERENCE.md` — published rates
- `USAGE_TRANSPARENCY_AUDIT_2026-03-27.md` — current gap analysis
