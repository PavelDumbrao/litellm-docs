# USAGE TRANSPARENCY IMPLEMENTATION BACKLOG

Date: 2026-03-27. Prioritized list of transparency improvements.
Source: USAGE_TRANSPARENCY_AUDIT_2026-03-27.md

---

## P0 — Must-Have (blocking customer trust)

### P0-1: Billing Type Label in Usage History
**What:** Add "Standard" / "Estimated" label to every ledger row in customer UI.
**Why:** Customer currently cannot tell if a charge is exact or approximated.
**How:** Query billing.public_model_tariff by model name, map billing_unit → label.
**Effort:** Small (1 DB query + UI label).
**Acceptance:** Every usage row shows a billing type label.

### P0-2: Proxy-Billed Caveat Text in Usage History
**What:** For every "Estimated" row, show or link to caveat text.
**Why:** Required by USAGE_DISPLAY_POLICY.md. Without it, customer has no way to understand approximation.
**How:** Static text per billing_unit category. Render conditionally in UI.
**Effort:** Small (static copy + conditional render).
**Acceptance:** Proxy-billed rows show caveat without requiring user action.

### P0-3: Stop Exposing LiteLLM response_cost to Customers
**What:** Ensure LiteLLM's own cost estimate is never shown in customer-facing surfaces.
**Why:** LiteLLM uses different rates. Showing it creates confusion and disputes.
**How:** Audit billing portal API responses. Remove response_cost if present.
**Effort:** Small (audit + remove).
**Acceptance:** Customer API and UI never return response_cost field.

---

## P1 — Good Next Improvements

### P1-1: Token Breakdown for Standard-Billed Models
**What:** Show input_tokens + output_tokens per request in customer usage detail.
**Why:** Allows customer to verify: cost = tokens × published rate.
**How:** Store input_tokens + output_tokens in ledger at write time (from spend log).
**Effort:** Medium (ledger schema change + billing-portal write path + UI).
**Acceptance:** Standard-billed rows show token detail. Customer can independently verify math.

### P1-2: Usage Summary by Model (Customer Dashboard)
**What:** Aggregate usage by model over time period (day/week/month).
**Why:** Customer currently has no way to understand which models drive their spend.
**How:** New endpoint: `GET /usage/summary?period=7d` → model: {total_credits, request_count, billing_type}.
**Effort:** Medium (new endpoint + UI widget).
**Acceptance:** Customer can see top-N models by spend in billing portal.

### P1-3: Operator Usage Drill-Down View
**What:** Per-user, per-model breakdown for operators with billing_unit column.
**Why:** Operators currently must write raw SQL to investigate usage.
**How:** Internal admin endpoint: `GET /admin/usage?user=X&model=Y&period=Z`.
**Effort:** Medium (new endpoint).
**Acceptance:** Operator can view any user's usage breakdown without DB access.

### P1-4: Spend Log ↔ Ledger Reconciliation Report
**What:** Periodic report showing discrepancy between LiteLLM spend log and actual ledger debits.
**Why:** Ensures our billing layer is not drifting from source-of-truth.
**How:** Script that compares spend log cost vs ledger debit for same request_id.
**Effort:** Medium (script + cron on VPS).
**Acceptance:** Weekly reconciliation report available to operators.

---

## P2 — Later Polish

### P2-1: Usage Export / CSV Download
**What:** Customer can download their usage history as CSV.
**Why:** Enterprise customers need this for internal accounting.
**How:** `GET /usage/export?format=csv&period=30d`.
**Effort:** Small-Medium.
**Acceptance:** CSV download available in billing portal.

### P2-2: Per-Request Cost Explanation Tooltip
**What:** Click/hover on any usage row → show detailed breakdown.
**Why:** Deeper transparency for power users.
**How:** UI modal with: model, billing_type, rate, tokens (if available), caveat.
**Effort:** Small (UI only, data already available).
**Acceptance:** Usage rows are expandable with detail.

### P2-3: Help Article on Proxy Billing
**What:** Customer-facing doc explaining what "Estimated" billing means.
**Why:** Reduces support tickets from confused customers.
**How:** Markdown doc in docs/help/ + link from UI caveat text.
**Effort:** Small (writing + link).
**Acceptance:** Caveat text links to published article.

### P2-4: Operator Troubleshooting View for Disputed Charges
**What:** Given a request_id or timestamp, operator can see full audit trail.
**Why:** Dispute resolution currently requires manual DB queries.
**How:** `GET /admin/request/{id}/audit` → spend log + ledger entry + billing_unit + rate used.
**Effort:** Medium.
**Acceptance:** Operator can fully reconstruct any charge in < 60 seconds.

### P2-5: Native Unit Metering (Long-Term)
**What:** Hook into provider response to extract actual audio seconds / search query count.
**Why:** Would make proxy-billed models fully exact, remove "Estimated" caveat.
**Blocker:** LiteLLM StandardLoggingPayload sealed before callbacks — requires upstream fix or custom response parsing.
**Effort:** Large (upstream dependency or custom middleware).
**Acceptance:** Proxy-billed models can show exact native unit consumed.

---

## Priority Summary

| ID | Description | Priority | Effort |
|---|---|---|---|
| P0-1 | Billing type label in UI | P0 | Small |
| P0-2 | Proxy caveat text | P0 | Small |
| P0-3 | Remove LiteLLM cost from customer API | P0 | Small |
| P1-1 | Token breakdown for standard models | P1 | Medium |
| P1-2 | Usage summary dashboard | P1 | Medium |
| P1-3 | Operator drill-down view | P1 | Medium |
| P1-4 | Spend log reconciliation | P1 | Medium |
| P2-1 | CSV export | P2 | Small-Medium |
| P2-2 | Per-request tooltip | P2 | Small |
| P2-3 | Help article on proxy billing | P2 | Small |
| P2-4 | Dispute audit trail | P2 | Medium |
| P2-5 | Native unit metering | P2 | Large |
