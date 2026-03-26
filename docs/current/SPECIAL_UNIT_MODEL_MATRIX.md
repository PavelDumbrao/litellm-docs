# SPECIAL UNIT MODEL MATRIX

Date: 2026-03-26.

## Audio (P1)
gpt-4o-audio-preview(audio_token, proxy, desired:audio tokens), gpt-audio(audio_token, proxy, desired:audio tokens), gpt-audio-mini(chars_token, proxy, desired:chars), gpt-4o-transcribe(audio_token, proxy, desired:audio minutes), gpt-4o-mini-transcribe(audio_token, proxy, desired:audio minutes)

## TTS (P1) ✅ IMPLEMENTED
tts-1(chars_token, ✅ worker branch active, validation BLOCKED — no real logs), tts-hd-1(chars_token, ✅ branch active, pending validation), gpt-4o-mini-tts(chars_token, ✅ branch active, pending validation)

## Search (P2)
gpt-4o-search-preview(search_token, proxy, desired:per query), gpt-4o-mini-search-preview(search_token, proxy, desired:per query), gpt-5-search-api(search_token, proxy, desired:per query)

## Realtime (P2)
gpt-4o-realtime-preview(realtime_token, proxy, desired:realtime tokens), gpt-4o-mini-realtime-preview(realtime_token, proxy, desired:realtime tokens)

## Research (P2)
o4-mini-deep-research(research_token, proxy, desired:per query)

## Summary
14 models, all proxy via token. P1: audio/TTS (8, metadata available). P2: search/realtime/research (6, no reliable unit data).

## Implementation Status (2026-03-26)
- TTS: 3/3 models have chars_token branch in worker (tts-1, tts-hd-1, gpt-4o-mini-tts)
- Audio: 0/5 models implemented (pending TTS validation first)
- Search: P2
- Realtime: P2
- Research: P2
- **Blocker:** No real user TTS logs to validate character count metadata
