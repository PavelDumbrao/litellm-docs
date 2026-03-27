# SPECIAL UNIT MODEL MATRIX

Date: 2026-03-26.

## Audio (P1)
gpt-4o-audio-preview(audio_token, proxy, desired:audio tokens), gpt-audio(audio_token, proxy, desired:audio tokens), gpt-audio-mini(audio_token, proxy, reclassified 2026-03-27 from chars_token — LiteLLM bills per token), gpt-4o-transcribe(audio_token, proxy, desired:audio minutes), gpt-4o-mini-transcribe(audio_token, proxy, desired:audio minutes)

## TTS (ALL REMOVED FROM PUBLIC SURFACE 2026-03-27)
tts-1(chars_token, ❌ REMOVED — legacy, inert billing), tts-hd-1(chars_token, ❌ REMOVED — chars NOT in metadata, blocker confirmed), gpt-4o-mini-tts(chars_token, ❌ REMOVED — chars NOT in metadata, blocker confirmed)

## Search (P2)
gpt-4o-search-preview(search_token, proxy, desired:per query), gpt-4o-mini-search-preview(search_token, proxy, desired:per query), gpt-5-search-api(search_token, proxy, desired:per query)

## Realtime (P2)
gpt-4o-realtime-preview(realtime_token, proxy, desired:realtime tokens), gpt-4o-mini-realtime-preview(realtime_token, proxy, desired:realtime tokens)

## Research (P2)
o4-mini-deep-research(research_token, proxy, desired:per query)

## Summary
11 models remaining in public surface (TTS fully removed). Audio (5, proxy), Search/Realtime/Research (6, proxy).

## Implementation Status (2026-03-27)
- TTS: ALL 3 REMOVED from public surface (tts-1, tts-hd-1, gpt-4o-mini-tts). is_active=false in DB.
- Audio: 5 models active, proxy-billed, no special-unit logic (gpt-4o-audio-preview, gpt-audio, gpt-audio-mini, gpt-4o-transcribe, gpt-4o-mini-transcribe)
- Search: 3 models active, proxy-billed
- Realtime: 2 models active, proxy-billed
- Research: 1 model active, proxy-billed
- **Blocker for TTS confirmed and actioned:** Removed from public surface pending reliable metering path.
- **Next for TTS:** Separate tts_billing_events table + worker integration before re-enabling.
