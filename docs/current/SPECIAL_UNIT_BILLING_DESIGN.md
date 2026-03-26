# SPECIAL UNIT BILLING DESIGN

Date: 2026-03-26. DESIGN ONLY — no production changes.

## Target Architecture
Worker reads tariff.billing_unit. If != "token": branch to unit-specific calc. Use raw spend USD as ground truth when unit metric unavailable.

## Unit Sources
Audio/Transcribe: metadata may have audio_duration_seconds. TTS: metadata may have char count. Search: no reliable metric. Realtime: no reliable metric.

## Fallback
If unit metric absent: fall to token proxy, log warning, do NOT fail billing.

## Pricing
Always from billing.public_model_tariff. Future: add unit_rate_credits column.

## Anti-Double-Charge
Do not bill both tokens AND unit metric. If unit metric available, use exclusively.

## Verification
1. Add billing_unit branch in worker
2. Test 1 proxy model
3. Compare vs expected rate
4. Expand if accurate
5. Document if not possible
