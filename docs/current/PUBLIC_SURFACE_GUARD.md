# PUBLIC SURFACE GUARD

Date: 2026-03-27. Living policy doc for repeatable public-surface validation.

## What This Is

A lightweight guard layer that checks 8 deterministic conditions against the live
billing DB and the trusted baseline frozen on 2026-03-27. Run it any time config,
billing DB, or model surface changes. Takes < 5 s. Outputs JSON + PASS/FAIL.

## Trusted Baseline (frozen 2026-03-27)

| Metric | Value |
|---|---|
| Active models (total) | 41 |
| Token-billed models | 30 |
| Proxy-billed special-unit models | 11 |
| Active chars_token models | 0 |
| TTS models in active surface | 0 |
| Hidden -tools aliases in active surface | 0 |

## 8 Checks Performed

| # | Check | Failure Condition |
|---|---|---|
| 1 | Active model count | ≠ 41 |
| 2 | Token-billed count | ≠ 30 |
| 3 | Proxy-billed count | ≠ 11 |
| 4 | Removed-model leakage | any of {tts-1, tts-hd-1, gpt-4o-mini-tts} is_active=true |
| 5 | Hidden-alias leakage | any -tools alias is_active=true in billing table |
| 6 | Duplicate active entries | same model_public_name appears >1 time with is_active=true |
| 7 | chars_token active | any model has billing_unit=chars_token AND is_active=true |
| 8 | Missing proxy models | any of 11 expected proxy-billed models is absent from active surface |

## Where the Script Lives

```
litellm-docs/scripts/surface_guard.py
```

Source of truth for the script is Git. Deploy to VPS before running:

```bash
# Из локальной машины — скопировать в контейнер
docker cp scripts/surface_guard.py billing-portal:/opt/surface_guard.py

# Или через SSH с VPS:
scp scripts/surface_guard.py root@31.97.199.12:/tmp/surface_guard.py
ssh root@31.97.199.12 'docker cp /tmp/surface_guard.py billing-portal:/opt/surface_guard.py'
```

## How To Run

```bash
# На VPS:
docker exec billing-portal python3 /opt/surface_guard.py

# С сохранением отчёта:
docker exec billing-portal python3 /opt/surface_guard.py > /tmp/guard_$(date +%Y-%m-%d).json
```

## What PASS Looks Like

```json
{
  "timestamp": "2026-03-27T09:00:00Z",
  "guard_version": "1.0",
  "verdict": "PASS",
  "checks": {
    "active_model_count": 41,
    "token_billed_count": 30,
    "proxy_billed_count": 11,
    "removed_model_leakage": [],
    "hidden_alias_leakage": [],
    "duplicate_active_count": 0,
    "chars_token_active_count": 0,
    "missing_proxy_models": []
  },
  "failures": [],
  "baseline": { ... }
}
```

Exit code 0.

## What FAIL Looks Like

```json
{
  "verdict": "FAIL",
  "failures": [
    "CHECK4: removed models leaked back into active: ['tts-1']",
    "CHECK1: active=42, expected=41"
  ]
}
```

Exit code 1. Investigate immediately.

## When To Re-Baseline

Re-baseline (update `BASELINE` dict in script + this doc) ONLY when:
- New model intentionally added to public surface after deliberate review
- Model intentionally removed after deliberate review
- Billing unit intentionally reclassified after documented decision

Never re-baseline to silence a failure without investigating root cause.

## Removed Models (blocked from re-activation)

| Model | Reason |
|---|---|
| tts-1 | chars_token billing inert — LiteLLM does not expose char count |
| tts-hd-1 | chars_token billing inert — confirmed blocker |
| gpt-4o-mini-tts | chars_token billing inert — confirmed blocker |

## Proxy-Billed Models (11 total)

| Category | Models |
|---|---|
| Audio | gpt-4o-audio-preview, gpt-audio, gpt-audio-mini, gpt-4o-transcribe, gpt-4o-mini-transcribe |
| Search | gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-5-search-api |
| Realtime | gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview |
| Research | o4-mini-deep-research |

## Dependencies

Script requires `asyncpg` (available in billing-portal container).
DB: `postgresql://n8n:***@n8n-postgres:5432/railway`, schema `billing`, table `public_model_tariff`.
