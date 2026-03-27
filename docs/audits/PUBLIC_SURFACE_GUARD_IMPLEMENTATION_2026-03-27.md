# PUBLIC SURFACE GUARD — IMPLEMENTATION REPORT

Date: 2026-03-27. One-time implementation audit.

## Summary

Implemented a repeatable surface-guard script (`scripts/surface_guard.py`) and
operating policy doc (`docs/current/PUBLIC_SURFACE_GUARD.md`) to protect the
trusted public surface baseline frozen after the 2026-03-27 cleanup session.

## Motivation

After cleaning the public surface (TTS removed, 11 special-unit models classified,
gpt-audio-mini reclassified), the state is correct but fragile — future config.yaml
or billing DB changes could reintroduce drift without detection. Manual vigilance
does not scale. This guard makes drift machine-detectable in < 5 s.

## What Was Built

### Script: `scripts/surface_guard.py`
- Language: Python 3 (asyncio + asyncpg)
- Connects directly to `billing.public_model_tariff` via n8n-postgres
- Runs 8 deterministic checks against hardcoded baseline
- Outputs structured JSON to stdout
- Exit code: 0 = PASS, 1 = FAIL
- No side effects — read-only DB access

### Doc: `docs/current/PUBLIC_SURFACE_GUARD.md`
- Living policy doc explaining all 8 checks
- Baseline values, PASS/FAIL examples
- Deploy and run instructions
- Re-baseline policy (when allowed and when not)

## 8 Checks — Design Rationale

| Check | Why This Matters |
|---|---|
| 1. Active count = 41 | Detects silent adds or removes |
| 2. Token-billed = 30 | Detects reclassification drift in bulk |
| 3. Proxy-billed = 11 | Detects new special-unit adds/removes |
| 4. Removed models not active | Blocks TTS from silently returning |
| 5. No hidden -tools aliases active | Blocks internal aliases from leaking to customers |
| 6. No duplicates | Detects billing table accidents (double-active) |
| 7. chars_token = 0 active | Confirms inert billing path remains suppressed |
| 8. All 11 proxy models present | Detects accidental deactivation of special-unit models |

## Baseline Values (trusted 2026-03-27)

```json
{
  "expected_active_total": 41,
  "expected_token_billed": 30,
  "expected_proxy_billed": 11,
  "expected_chars_token_active": 0
}
```

## Deploy Instructions

```bash
# 1. Из Desktop/litellm-docs — скопировать скрипт на VPS
scp scripts/surface_guard.py root@31.97.199.12:/tmp/surface_guard.py

# 2. На VPS — скопировать в контейнер
ssh root@31.97.199.12 'docker cp /tmp/surface_guard.py billing-portal:/opt/surface_guard.py'

# 3. Запустить
ssh root@31.97.199.12 'docker exec billing-portal python3 /opt/surface_guard.py'
```

## First-Run Expected Output

При запуске сразу после деплоя ожидается:

```json
{
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
  "failures": []
}
```

Если будет FAIL — нужно проверить DB перед тем как обновлять baseline.

## Limitations

- Скрипт проверяет только billing.public_model_tariff — не config.yaml напрямую
- Не проверяет роутинг и fallback (для этого нужен отдельный config-parser)
- Baseline числа (41/30/11) нужно обновлять вручную при намеренных изменениях
- asyncpg должен быть установлен в billing-portal (проверено — присутствует)

## Files Changed This Session

| File | Action |
|---|---|
| `scripts/surface_guard.py` | NEW — guard script |
| `docs/current/PUBLIC_SURFACE_GUARD.md` | NEW — policy doc |
| `docs/audits/PUBLIC_SURFACE_GUARD_IMPLEMENTATION_2026-03-27.md` | NEW — this file |
| `docs/current/LIVE_DOC_INDEX.md` | UPDATED — added guard entries |

## Verdict

Guard layer IMPLEMENTED. Public surface drift is now machine-detectable.
Next step: run first PASS on VPS to confirm baseline is live-accurate.
