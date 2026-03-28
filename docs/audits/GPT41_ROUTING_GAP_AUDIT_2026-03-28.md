# GPT-4.1 Routing Gap Audit

**Date:** 2026-03-28  
**Author:** Operator  
**Status:** CONFIRMED — routing gap identified

---

## 1. Scope

This audit covers the live LiteLLM routing configuration for `gpt-4.1` (exact model, no suffix).  
Economics gap was closed separately in commit `798a5e4`. This audit targets the runtime/routing layer only.

---

## 2. Gap Summary

| Item | Status |
|---|---|
| `gpt-4.1` in `model_list` | ❌ ABSENT |
| `gpt-4.1` provider mapping (POLO_AZ) | ❌ ABSENT |
| `gpt-4.1` provider mapping (JENIYA_AZ15) | ❌ ABSENT |
| `gpt-4.1` fallback entry | ❌ ABSENT |
| `gpt-4.1` in `billing.public_model_tariff` | ✅ EXISTS (retail truth, untouched) |
| `gpt-4.1-mini` in `model_list` | ✅ EXISTS (POLO_AZ + JENIYA_AZ15) |
| `gpt-4.1-nano` in `model_list` | ✅ EXISTS (POLO_AZ + JENIYA_AZ15) |

**Root cause:** `gpt-4.1` was never added to `config.yaml` `model_list`.  
Retail tariff exists. Economics snapshot exists (Estimated confidence, commit `798a5e4`).  
But no routing path → any request to `gpt-4.1` through LiteLLM proxy returns 404/model-not-found.

---

## 3. Evidence

### config.yaml grep — `model_name: gpt-4.1` (exact)

```
$ grep -n 'model_name: gpt-4.1$' /docker/litellm-xne6/config.yaml
(no output)
```

### config.yaml grep — all gpt-4.1 variants

```
$ grep -n 'gpt-4.1' /docker/litellm-xne6/config.yaml | grep model_name
170:- model_name: gpt-4.1-mini     # POLO_AZ order:1
179:- model_name: gpt-4.1-mini     # JENIYA_AZ15 order:2
188:- model_name: gpt-4.1-nano     # POLO_AZ order:1
197:- model_name: gpt-4.1-nano     # JENIYA_AZ15 order:2
843:- model_name: gpt-4.1-mini-tools   # hidden
854:- model_name: gpt-4.1-mini-tools   # hidden
865:- model_name: gpt-4.1-nano-tools   # hidden
876:- model_name: gpt-4.1-nano-tools   # hidden
```

**`gpt-4.1` (exact) = 0 entries in model_list.**

### Fallbacks — `gpt-4.1` entry

```yaml
# Absent from fallbacks section
# Only gpt-4.1-mini and gpt-4.1-nano have entries
```

---

## 4. Intended Routing Path

Based on:
- Pattern from `gpt-4.1-mini` and `gpt-4.1-nano` (both use POLO_AZ primary + JENIYA_AZ15 secondary)
- LIVE_PUBLIC_ALIAS_MAP.md (2026-03-26): `gpt-4.1 -> polo-az (order:1), gpt-4.1-mini (fallback)`
- Economics snapshot: provider = `https://poloai.top/v1` (Estimated)
- `POLO_AZ_API_KEY` covers GPT-4.1, audio/search/TTS models group

| Priority | Provider | api_base | key |
|---|---|---|---|
| order:1 | POLO_AZ | `https://poloai.top/v1` | `POLO_AZ_API_KEY` |
| order:2 | JENIYA_AZ15 | `https://jeniya.top/v1` | `JENIYA_AZ15_API_KEY` |

### Intended fallback chain
`gpt-4.1` → `gpt-4o` → `gpt-4.1-mini`

---

## 5. Cost Tracking Values (model_info)

**Source:** Economics snapshot (Estimated), commit `798a5e4`  
**Provider cost basis (POLO reseller):** $2.0/$8.0 per 1M tokens  
**LiteLLM model_info format:**

```yaml
model_info:
  input_cost_per_token: 2.0e-06   # $2.0/1M
  output_cost_per_token: 8.0e-06  # $8.0/1M
```

These values are internal cost tracking only. They do NOT affect `billing.public_model_tariff`.

---

## 6. Retail Pricing Boundary

- `billing.public_model_tariff.gpt-4.1` = retail truth, **not modified**
- `input_rate_credits = 0.00000424`, `output_rate_credits = 0.00001694`
- `model_info` in LiteLLM = provider cost tracking only
- No customer tariff changes in this fix

---

## 7. Fix Plan

1. Add two `model_list` entries to `config.yaml` for `gpt-4.1`
2. Add fallback entry `gpt-4.1 → gpt-4o → gpt-4.1-mini`
3. Hot-reload LiteLLM container
4. Smoke test via proxy port 32779
5. Document result in `GPT41_ROUTING_REMEDIATION_RESULT_2026-03-28.md`

---

## 8. Verdict

**Gap class:** MISSING_MODEL_LIST_ENTRY  
**Severity:** P0 — model routable in billing, unroutable in LiteLLM  
**Impact:** Any client request to `gpt-4.1` fails at LiteLLM routing layer  
**Retail affected:** NO  
**Fix complexity:** LOW — pattern-based addition, no new provider or key needed
