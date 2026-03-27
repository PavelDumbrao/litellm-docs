# USAGE SUMMARY GAP AUDIT

Date: 2026-03-27. Audits what summary/totals customer currently has and what is missing.

## 1. What Summary/Totals Customer Currently Has

- Summary cards on Usage screen: total_requests, success_requests, error_requests, total_charged_credits
- These come from `GET /billing/usage/summary` — **endpoint does not exist yet** (returns null, caught silently)
- In practice: `total_charged_credits` card falls back to summing raw log rows client-side
- No breakdown by billing type
- No Standard vs Estimated separation
- No caveat at summary level

## 2. What Summary/Totals Are Missing

| Missing Item | Impact |
|---|---|
| `total_standard_debit` | Customer cannot see how much of their spend is exact-billed |
| `total_estimated_debit` | Customer cannot see how much is approximated |
| `has_estimated` flag | Summary-level caveat cannot be shown |
| Model-grouped breakdown | Customer cannot see which model drives spend |
| Period filtering on summary | Current summary is all-time, not period-aware |

## 3. What Can Be Computed Safely from Current Backend Data

All from `usage_billing_snapshot` + `billing.public_model_tariff` JOIN:

| Field | Safe? | Source |
|---|---|---|
| total_debit | ✅ | SUM(charged_credits) |
| total_requests | ✅ | COUNT(*) |
| standard_debit | ✅ | SUM where billing_unit = 'token' |
| estimated_debit | ✅ | SUM where billing_unit IN proxy_units |
| has_estimated | ✅ | estimated_debit > 0 |
| model breakdown | ✅ | GROUP BY public_model_name + billing_unit |

## 4. Standard vs Estimated Totals Must Be Separated

Yes — because:
- Standard debit is exact: customer can verify math independently
- Estimated debit is approximated: customer must be warned
- Showing a single total without separation implies false precision on the estimated portion
- Policy: USAGE_DISPLAY_POLICY.md §5 — no fake precision

## 5. Required Caveats at Summary Level

If `has_estimated = true`:
> Part of your total includes estimated charges from special-billing models (audio, search, realtime). These amounts are best-effort approximations.

If `has_estimated = false`:
> No caveat needed — all charges are Standard (exact billing).
