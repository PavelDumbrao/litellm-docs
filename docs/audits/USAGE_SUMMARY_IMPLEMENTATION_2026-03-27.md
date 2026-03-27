# USAGE SUMMARY IMPLEMENTATION REPORT

Date: 2026-03-27. Usage summary layer with Standard/Estimated breakdown.

## Verdict

**Summary implemented** — period totals, Standard/Estimated split, and caveat are live.

---

## BLOCK A — Backend Endpoint

**Path:** `GET /api/billing/usage/summary`
**File:** `/app/app/api/billing.py` (inside `billing-portal` container)

**Query params:**
- `date_from` (optional, YYYY-MM-DD)
- `date_to` (optional, YYYY-MM-DD)

**Fields returned:**

| Field | Type | Description |
|---|---|---|
| `total_requests` | int | Total usage rows for period |
| `total_debit` | float | Sum of all charged_credits |
| `standard_debit` | float | Sum of token-billed credits |
| `estimated_debit` | float | Sum of proxy-billed credits |
| `has_estimated` | bool | true if any proxy-billed rows |
| `estimated_caveat` | string\|null | Caveat text if has_estimated |
| `models` | array | Per-model breakdown (top 20) |
| `period_from` | string\|null | Filter applied |
| `period_to` | string\|null | Filter applied |

**Fields NOT exposed:** raw_cost_usd, provider, spend_log_id, LiteLLM response_cost

**Implementation:** LEFT JOIN `billing.public_model_tariff` to get `billing_unit` per model. CASE WHEN to split Standard/Estimated in one SQL pass.

---

## BLOCK B — Frontend Component

**File:** `frontend/src/pages/Usage.tsx`
**Build:** `index-B8IbQTVa.js` (298 kB)

**Summary UI location:** Top of Usage screen, 4-card grid above filters.

**Cards:**
1. Запросов — total request count
2. Списано всего — total debit
3. Standard — exact-billed subtotal + «Точный биллинг» label
4. Estimated — proxy-billed subtotal (amber if > 0) + «~Приближённый» label

**Caveat block:** renders below cards if `has_estimated = true` — amber border box with italic caveat text.

---

## BLOCK C — Summary Examples

### No Estimated rows

```json
{
  "total_requests": 47,
  "total_debit": 0.1823,
  "standard_debit": 0.1823,
  "estimated_debit": 0.0,
  "has_estimated": false,
  "estimated_caveat": null
}
```

**UI:** 4 cards. Estimated card shows `0.0000` in gray. No caveat block.

### With Estimated rows

```json
{
  "total_requests": 52,
  "total_debit": 0.2341,
  "standard_debit": 0.1890,
  "estimated_debit": 0.0451,
  "has_estimated": true,
  "estimated_caveat": "Part of your total includes estimated charges from special-billing models (audio, search, realtime). These amounts are best-effort approximations."
}
```

**UI:** Estimated card shows `0.0451` in amber. Caveat block appears below cards: amber border, italic text.

---

## BLOCK D — Regression Check

| Check | Status |
|---|---|
| Build completed | ✅ (766ms) |
| Container restarted | ✅ |
| /health responds | ✅ |
| /usage/summary in OpenAPI | ✅ |
| Summary cards render | ✅ |
| Filters still work | ✅ |
| Row-level labels preserved | ✅ |
| No raw_cost_usd anywhere | ✅ |
