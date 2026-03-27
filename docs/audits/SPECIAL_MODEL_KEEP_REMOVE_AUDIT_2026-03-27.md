# SPECIAL MODEL KEEP / REMOVE AUDIT

Date: 2026-03-27. Scope: all non-plain-token models currently is_active=true in billing.public_model_tariff.

## CLASSIFICATION

### AUDIO (audio_token)

| model | billing_unit | current behavior | metering confidence | op risk | decision |
|---|---|---|---|---|---|
| gpt-4o-audio-preview | audio_token | proxy via token | LOW (proxy approx) | LOW | KEEP AS PROXY |
| gpt-audio | audio_token | proxy via token | LOW (proxy approx) | LOW | KEEP AS PROXY |
| gpt-4o-transcribe | audio_token | proxy via token | LOW (proxy approx) | LOW | KEEP AS PROXY |
| gpt-4o-mini-transcribe | audio_token | proxy via token | LOW (proxy approx) | LOW | KEEP AS PROXY |

**Reason:** audio_token proxy billing functional. No billing ambiguity vs customers. Under-charges possible but operationally safe. Keep until proper audio minute billing available.

### AUDIO / chars_token (special flag)

| model | billing_unit | current behavior | metering confidence | op risk | decision |
|---|---|---|---|---|---|
| gpt-audio-mini | chars_token | proxy via token | NONE (same blocker as TTS) | HIGH | **AMBIGUOUS — REVIEW** |

**Note:** gpt-audio-mini uses billing_unit=chars_token, is_active=true. Same blocker as TTS (LiteLLM does not expose chars in spend log). Currently proxy-billed via token which approximates. Risk: customer-facing pricing implies chars billing but actual billing is token proxy. RECOMMEND: deactivate or reclassify as audio_token proxy to remove ambiguity.

### SEARCH (search_token)

| model | billing_unit | current behavior | metering confidence | op risk | decision |
|---|---|---|---|---|---|
| gpt-4o-search-preview | search_token | proxy via token | MEDIUM (per-query approx) | LOW | KEEP AS PROXY |
| gpt-4o-mini-search-preview | search_token | proxy via token | MEDIUM (per-query approx) | LOW | KEEP AS PROXY |
| gpt-5-search-api | search_token | proxy via token | MEDIUM (per-query approx) | LOW | KEEP AS PROXY |

**Reason:** search_token unit is per-query. Proxy approximates reasonably. No billing path failure.

### REALTIME (realtime_token)

| model | billing_unit | current behavior | metering confidence | op risk | decision |
|---|---|---|---|---|---|
| gpt-4o-realtime-preview | realtime_token | proxy via token | LOW (proxy approx) | MEDIUM | KEEP AS PROXY |
| gpt-4o-mini-realtime-preview | realtime_token | proxy via token | LOW (proxy approx) | MEDIUM | KEEP AS PROXY |

**Reason:** Realtime audio pricing differs from token pricing. Proxy under-charges but operationally functional. Medium risk — worth improving but no immediate removal needed.

### RESEARCH (research_token)

| model | billing_unit | current behavior | metering confidence | op risk | decision |
|---|---|---|---|---|---|
| o4-mini-deep-research | research_token | proxy via token | LOW (proxy approx) | MEDIUM | KEEP AS PROXY |

**Reason:** Deep research is expensive. Proxy approximation may under-charge significantly. Worth monitoring. Keep for now, improve billing unit later.

## TTS (ALL REMOVED 2026-03-27)

| model | billing_unit | decision |
|---|---|---|
| tts-1 | chars_token | REMOVE — legacy, chars billing inert |
| gpt-4o-mini-tts | chars_token | REMOVE — chars NOT in spend log metadata |
| tts-hd-1 | chars_token | REMOVE — chars NOT in spend log metadata |

Confirmed removed: is_active=false in billing.public_model_tariff.

## SUMMARY TABLE

| Decision | Count | Models |
|---|---|---|
| KEEP | 0 | — |
| KEEP AS PROXY | 10 | gpt-4o-audio-preview, gpt-audio, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-5-search-api, gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview, o4-mini-deep-research |
| AMBIGUOUS | 1 | gpt-audio-mini (chars_token but token proxy active) |
| REMOVE | 3 | tts-1, gpt-4o-mini-tts, tts-hd-1 (done) |

## NEXT ACTIONS

1. **gpt-audio-mini** — review billing_unit. If chars_token billing is also inert, consider same removal or reclassify to audio_token proxy. Requires confirmation.
2. **Realtime** — monitor spend vs cost. If significant delta, prioritize proper realtime billing.
3. **Research** — same as realtime. Low volume for now.
4. **TTS re-enable path** — separate tts_billing_events table + worker integration before re-enabling any TTS model.