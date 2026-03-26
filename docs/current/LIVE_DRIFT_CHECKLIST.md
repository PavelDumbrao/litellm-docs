# LIVE DRIFT CHECKLIST

Date: 2026-03-26. Repeatable after any change.

## 1. Changed config.yaml?
Verify: model_list count, new/removed models.
Mismatch: model in config but not in billing DB or vice versa.

## 2. Changed billing.public_model_tariff?
Verify: SELECT COUNT(*) WHERE is_active=true. Baseline=44.
Mismatch: count differs.

## 3. Changed provider groups?
Verify: config.yaml env keys, api_base.
Mismatch: new provider not in docs, or removed provider still referenced.

## 4. Changed public catalog?
Verify: LIVE_PUBLIC_MODEL_CATALOG.md vs config.yaml.
Mismatch: model in catalog but hidden, or public model missing.

## 5. Changed fallbacks?
Verify: LIVE_ROUTING_AND_FALLBACK_REFERENCE.md vs config.yaml fallbacks.
Mismatch: fallback chain differs.

## 6. Changed callbacks?
Verify: custom_callbacks.py, config.yaml callbacks list.
Mismatch: callback listed but file changed.

## 7. Changed proxy-billed handling?
Verify: worker special-unit logic. Currently NO — token proxy only.

## 8. Changed docs/current?
Verify: git diff vs last known good state.
Mismatch: doc contradicts config or DB.

## Stop Condition
Any mismatch = DO NOT proceed with rollout. Fix drift first.
